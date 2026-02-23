"""
tests/contexts/timetable/unit/test_domain_services.py
=======================================================
Unit tests for the Timetable bounded context.

Rules demonstrated here:
  - Only imports from: src.contexts.timetable.*, src.shared_kernel.*, tests.shared.*
  - Never imports from another context (assignments, exams, etc.)
  - No real I/O — pure domain logic only
"""
from __future__ import annotations

import pytest
from uuid import uuid4
from datetime import datetime

from src.shared_kernel.domain.identity import DepartmentId, RoomId
from src.contexts.timetable.domain.value_objects import (
    CourseCode, TimeSlot, WeekDay, DepartmentRange,
)
from src.contexts.timetable.domain.entities import (
    TimetableEntry, StudentSavedTimetable, TeacherSavedTimetable, RoomScheduleView,
)
from src.contexts.timetable.domain.services import (
    merge_time_slots, deduplicate_entries, find_free_room_ids, matches_search_query,
)
from src.shared_kernel.domain.identity import StudentId, TeacherId
from tests.shared.fakes.infrastructure import FakeClock, FakeEventBus


# ── Helpers ──────────────────────────────────────────────────────────────────

def _entry(**kwargs) -> TimetableEntry:
    defaults = dict(
        course_code=CourseCode("UNS-301"),
        course_name="Calculus",
        day=WeekDay.MONDAY,
        time_slot=TimeSlot("08:00-08:45"),
        room_id=RoomId(uuid4()),
        teacher_name="Dr. Smith",
        department_id=DepartmentId(uuid4()),
        scraped_at=datetime(2024, 9, 1, 10, 0),
    )
    defaults.update(kwargs)
    return TimetableEntry.create(**defaults)


# ── TimeSlot value object ─────────────────────────────────────────────────────

class TestTimeSlot:
    def test_valid_parses_start_end(self):
        s = TimeSlot("08:00-08:45")
        assert s.start() == "08:00"
        assert s.end() == "08:45"
        assert s.is_valid()

    def test_malformed_is_invalid(self):
        s = TimeSlot("BADTIME")
        assert not s.is_valid()
        assert s.start() == ""

    def test_overlaps_true(self):
        a = TimeSlot("08:00-09:00")
        b = TimeSlot("08:30-09:30")
        assert a.overlaps(b)
        assert b.overlaps(a)

    def test_overlaps_false_adjacent(self):
        a = TimeSlot("08:00-09:00")
        b = TimeSlot("09:00-10:00")
        assert not a.overlaps(b)

    def test_overlaps_false_disjoint(self):
        a = TimeSlot("08:00-09:00")
        b = TimeSlot("10:00-11:00")
        assert not a.overlaps(b)


# ── DepartmentRange value object ──────────────────────────────────────────────

class TestDepartmentRange:
    def test_ids_inclusive(self):
        r = DepartmentRange(start=3, end=5)
        assert r.ids() == [3, 4, 5]

    def test_start_gt_end_raises(self):
        with pytest.raises(ValueError):
            DepartmentRange(start=10, end=5)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            DepartmentRange(start=-1, end=5)


# ── FIX 3: Split aggregate tests ─────────────────────────────────────────────

class TestStudentSavedTimetable:
    """FIX 3A: Student aggregate has its own behaviour, no union type."""

    def test_pin_and_unpin(self):
        student_id = StudentId(uuid4())
        saved = StudentSavedTimetable.create(student_id)
        entry_id = uuid4()

        saved.pin(entry_id)
        assert entry_id in saved.entry_ids

        saved.unpin(entry_id)
        assert entry_id not in saved.entry_ids

    def test_pin_duplicate_ignored(self):
        saved = StudentSavedTimetable.create(StudentId(uuid4()))
        eid = uuid4()
        saved.pin(eid)
        saved.pin(eid)
        assert saved.entry_ids.count(eid) == 1


class TestTeacherSavedTimetable:
    """FIX 3B: Teacher aggregate is completely separate — no shared base needed."""

    def test_create_has_correct_teacher_id(self):
        tid = TeacherId(uuid4())
        saved = TeacherSavedTimetable.create(tid, label="My Spring Classes")
        assert saved.teacher_id == tid
        assert saved.label == "My Spring Classes"


class TestRoomScheduleView:
    """FIX 3C: Rooms are a read model — never persisted."""

    def test_is_free_at_empty_room(self):
        view = RoomScheduleView(room_id=RoomId(uuid4()), entries=())
        assert view.is_free_at(WeekDay.MONDAY, TimeSlot("10:00-11:00"))

    def test_is_busy_when_entry_overlaps(self):
        entry = _entry(day=WeekDay.MONDAY, time_slot=TimeSlot("10:00-11:00"))
        view = RoomScheduleView(room_id=entry.room_id, entries=(entry,))
        assert not view.is_free_at(WeekDay.MONDAY, TimeSlot("10:30-11:30"))

    def test_is_free_different_day(self):
        entry = _entry(day=WeekDay.MONDAY, time_slot=TimeSlot("10:00-11:00"))
        view = RoomScheduleView(room_id=entry.room_id, entries=(entry,))
        assert view.is_free_at(WeekDay.TUESDAY, TimeSlot("10:00-11:00"))


# ── Domain services ───────────────────────────────────────────────────────────

class TestMergeTimeSlots:
    def test_merges_two_consecutive(self):
        result = merge_time_slots([TimeSlot("08:00-08:45"), TimeSlot("08:55-09:40")])
        assert result == "08:00-09:40"

    def test_single_slot(self):
        assert merge_time_slots([TimeSlot("10:00-10:45")]) == "10:00-10:45"

    def test_empty_returns_empty(self):
        assert merge_time_slots([]) == ""

    def test_malformed_slots_ignored(self):
        result = merge_time_slots([TimeSlot("BAD"), TimeSlot("08:00-08:45")])
        assert result == "08:00-08:45"


class TestDeduplicateEntries:
    def test_keeps_most_recent(self):
        room = RoomId(uuid4())
        dept = DepartmentId(uuid4())
        old = TimetableEntry.create(
            course_code=CourseCode("UNS-301"), course_name="Calc",
            day=WeekDay.MONDAY, time_slot=TimeSlot("08:00-08:45"),
            room_id=room, teacher_name="Dr. Smith", department_id=dept,
            scraped_at=datetime(2024, 9, 1),
        )
        new = TimetableEntry.create(
            course_code=CourseCode("UNS-301"), course_name="Calc",
            day=WeekDay.MONDAY, time_slot=TimeSlot("08:00-08:45"),
            room_id=room, teacher_name="Dr. Smith", department_id=dept,
            scraped_at=datetime(2024, 9, 2),
        )
        result = deduplicate_entries([old, new])
        assert len(result) == 1
        assert result[0].scraped_at == datetime(2024, 9, 2)

    def test_distinct_entries_kept(self):
        e1 = _entry(day=WeekDay.MONDAY)
        e2 = _entry(day=WeekDay.TUESDAY)
        result = deduplicate_entries([e1, e2])
        assert len(result) == 2


class TestFindFreeRooms:
    def test_busy_room_excluded(self):
        room_id = RoomId(uuid4())
        entry = _entry(
            room_id=room_id,
            day=WeekDay.MONDAY,
            time_slot=TimeSlot("10:00-11:00"),
        )
        free = find_free_room_ids([entry], WeekDay.MONDAY, TimeSlot("10:30-11:30"))
        assert str(room_id) not in free

    def test_free_at_different_time(self):
        room_id = RoomId(uuid4())
        entry = _entry(room_id=room_id, day=WeekDay.MONDAY, time_slot=TimeSlot("10:00-11:00"))
        free = find_free_room_ids([entry], WeekDay.MONDAY, TimeSlot("13:00-14:00"))
        assert str(room_id) in free


class TestMatchesSearchQuery:
    def test_matches_course_name(self):
        e = _entry(course_name="Calculus Advanced")
        assert matches_search_query(e, "calculus")

    def test_matches_teacher(self):
        e = _entry(teacher_name="Prof. Ivanova")
        assert matches_search_query(e, "ivanova")

    def test_no_match(self):
        e = _entry(course_name="Physics")
        assert not matches_search_query(e, "calculus")

    def test_empty_query_matches_all(self):
        e = _entry()
        assert matches_search_query(e, "")


# ── Shared fakes sanity tests ─────────────────────────────────────────────────

class TestFakeClock:
    def test_advance_hours(self):
        clock = FakeClock(datetime(2024, 9, 1, 10, 0))
        clock.advance_hours(48)
        assert clock.now() == datetime(2024, 9, 3, 10, 0)


class TestFakeEventBus:
    import asyncio

    def test_captures_published_events(self):
        import asyncio
        from src.contexts.timetable.domain.events import TimetableScraped

        bus = FakeEventBus()
        event = TimetableScraped(department_count=5, course_count=100)
        asyncio.get_event_loop().run_until_complete(bus.publish(event))

        assert len(bus.published) == 1
        scraped = bus.events_of(TimetableScraped)
        assert len(scraped) == 1
        assert scraped[0].course_count == 100
