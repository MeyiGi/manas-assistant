"""
src/contexts/timetable/domain/entities.py
==========================================
FIX 3: SavedTimetable with owner_id: StudentId | TeacherId | RoomId
was a discriminated-union aggregate needing if/elif owner_type everywhere.

Replaced with:
  StudentSavedTimetable  — student pins their class selections
  TeacherSavedTimetable  — teacher pins their teaching schedule
  RoomScheduleView       — READ MODEL only, never persisted (rooms don't
                           "save" a timetable; their schedule is computed
                           from scraped TimetableEntry objects at query time)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.shared_kernel.domain.identity import DepartmentId, RoomId, StudentId, TeacherId
from src.contexts.timetable.domain.value_objects import CourseCode, TimeSlot, WeekDay


# ---------------------------------------------------------------------------
# Core scrape aggregate
# ---------------------------------------------------------------------------

@dataclass
class TimetableEntry:
    """One parsed course slot from the Manas timetable HTML.

    Aggregate root. Scraped, deduplicated, and stored by the scrape use case.
    Natural key: (course_code, day, time_slot, room_id, teacher_name).
    """
    id: UUID
    course_code: CourseCode
    course_name: str
    day: WeekDay
    time_slot: TimeSlot
    room_id: RoomId
    teacher_name: str
    department_id: DepartmentId
    scraped_at: datetime

    @classmethod
    def create(
        cls,
        course_code: CourseCode,
        course_name: str,
        day: WeekDay,
        time_slot: TimeSlot,
        room_id: RoomId,
        teacher_name: str,
        department_id: DepartmentId,
        scraped_at: datetime,
    ) -> "TimetableEntry":
        return cls(
            id=uuid4(),
            course_code=course_code,
            course_name=course_name,
            day=day,
            time_slot=time_slot,
            room_id=room_id,
            teacher_name=teacher_name,
            department_id=department_id,
            scraped_at=scraped_at,
        )


# ---------------------------------------------------------------------------
# FIX 3A — Student aggregate (persisted)
# ---------------------------------------------------------------------------

@dataclass
class StudentSavedTimetable:
    """A student's personally pinned timetable selection.

    Students search the full timetable, pick their courses, save here.
    Lifecycle: created on first save, updated when student changes selection.
    """
    id: UUID
    student_id: StudentId
    label: str
    entry_ids: list[UUID] = field(default_factory=list)
    saved_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, student_id: StudentId, label: str = "My Timetable") -> "StudentSavedTimetable":
        return cls(id=uuid4(), student_id=student_id, label=label)

    def pin(self, entry_id: UUID) -> None:
        if entry_id not in self.entry_ids:
            self.entry_ids.append(entry_id)

    def unpin(self, entry_id: UUID) -> None:
        self.entry_ids = [e for e in self.entry_ids if e != entry_id]


# ---------------------------------------------------------------------------
# FIX 3B — Teacher aggregate (persisted)
# ---------------------------------------------------------------------------

@dataclass
class TeacherSavedTimetable:
    """A teacher's personally saved class schedule.

    Teachers search by their own name, find their slots, pin them here.
    Separate from StudentSavedTimetable: different search UX, different
    display fields (teacher sees student counts, not room availability).
    """
    id: UUID
    teacher_id: TeacherId
    label: str
    entry_ids: list[UUID] = field(default_factory=list)
    saved_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, teacher_id: TeacherId, label: str = "My Classes") -> "TeacherSavedTimetable":
        return cls(id=uuid4(), teacher_id=teacher_id, label=label)

    def pin(self, entry_id: UUID) -> None:
        if entry_id not in self.entry_ids:
            self.entry_ids.append(entry_id)

    def unpin(self, entry_id: UUID) -> None:
        self.entry_ids = [e for e in self.entry_ids if e != entry_id]


# ---------------------------------------------------------------------------
# FIX 3C — Room schedule is a READ MODEL, never persisted
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RoomScheduleView:
    """Computed view of a room's occupancy. Never stored in the database.

    Generated on-demand by ListAvailableRoomsUseCase from TimetableEntry
    objects. Rooms do not "save" schedules — they have one derived from
    all entries referencing their RoomId.
    """
    room_id: RoomId
    entries: tuple[TimetableEntry, ...]  # immutable — this is a snapshot

    def is_free_at(self, day: WeekDay, slot: TimeSlot) -> bool:
        return not any(
            e.day == day and e.time_slot.overlaps(slot)
            for e in self.entries
        )

    def free_slots(self, day: WeekDay, all_slots: list[TimeSlot]) -> list[TimeSlot]:
        return [s for s in all_slots if self.is_free_at(day, s)]
