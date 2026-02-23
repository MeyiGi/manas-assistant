"""
src/contexts/timetable/domain/events.py
=========================================
Events published by the Timetable bounded context.

Other contexts MAY import these. That is the only permitted cross-context import.
"""
from __future__ import annotations
from dataclasses import dataclass
from src.shared_kernel.domain.events import DomainEvent


@dataclass(frozen=True)
class TimetableScraped(DomainEvent):
    """Fired after a full scrape cycle completes successfully."""
    department_count: int = 0
    course_count: int = 0


@dataclass(frozen=True)
class RoomScheduleUpdated(DomainEvent):
    """Fired when a room's schedule changes after a scrape."""
    room_id: str = ""
    affected_entry_count: int = 0
