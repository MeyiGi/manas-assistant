"""
src/contexts/attendance/domain/events.py
==========================================
Events published by the Attendance bounded context.
"""
from __future__ import annotations
from dataclasses import dataclass
from src.shared_kernel.domain.events import DomainEvent
from src.shared_kernel.domain.identity import StudentId


@dataclass(frozen=True)
class AttendanceSynced(DomainEvent):
    student_id: StudentId | None = None
    records_updated: int = 0


@dataclass(frozen=True)
class AttendanceCritical(DomainEvent):
    """Fired when a student crosses the critical absence threshold."""
    student_id: StudentId | None = None
    course_code: str = ""
    absences: int = 0
    max_allowed: int = 0
