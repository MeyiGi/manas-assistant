"""
src/contexts/timetable/domain/services.py
==========================================
Pure domain services — no I/O, fully testable without mocks.
"""
from __future__ import annotations

from src.contexts.timetable.domain.entities import TimetableEntry
from src.contexts.timetable.domain.value_objects import TimeSlot, WeekDay


def merge_time_slots(slots: list[TimeSlot]) -> str:
    """Collapse multiple time slots into one HH:MM-HH:MM span."""
    valid = [s for s in slots if s.is_valid()]
    if not valid:
        return ""
    return f"{min(s.start() for s in valid)}-{max(s.end() for s in valid)}"


def deduplicate_entries(entries: list[TimetableEntry]) -> list[TimetableEntry]:
    """Remove duplicate entries keeping the most recently scraped."""
    seen: dict[tuple, TimetableEntry] = {}
    for e in entries:
        key = (str(e.course_code), e.day, str(e.time_slot), str(e.room_id), e.teacher_name)
        if key not in seen or e.scraped_at > seen[key].scraped_at:
            seen[key] = e
    return list(seen.values())


def find_free_room_ids(
    entries: list[TimetableEntry],
    day: WeekDay,
    slot: TimeSlot,
) -> list[str]:
    """Return room IDs that have no entry at *day*/*slot*."""
    all_room_ids = {str(e.room_id) for e in entries}
    busy_ids = {
        str(e.room_id)
        for e in entries
        if e.day == day and e.time_slot.overlaps(slot)
    }
    return sorted(all_room_ids - busy_ids)


def matches_search_query(entry: TimetableEntry, query: str) -> bool:
    """Case-insensitive substring search across key fields."""
    q = query.lower().strip()
    if not q:
        return True
    haystack = " ".join([
        str(entry.course_code),
        entry.course_name,
        entry.teacher_name,
        str(entry.room_id),
        entry.day.turkish,
    ]).lower()
    return q in haystack
