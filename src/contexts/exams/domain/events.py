"""
src/contexts/exams/domain/events.py
=====================================
Events published by the Exams bounded context.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from src.shared_kernel.domain.events import DomainEvent
from src.shared_kernel.domain.identity import CourseId, ExamId, StudentId


@dataclass(frozen=True)
class ExamScheduled(DomainEvent):
    """Fired when a new exam date is saved."""
    exam_id: ExamId | None = None
    course_id: CourseId | None = None
    scheduled_at: datetime | None = None


@dataclass(frozen=True)
class ExamCancelled(DomainEvent):
    """Fired when a scheduled exam is cancelled."""
    exam_id: ExamId | None = None
    reason: str = ""


@dataclass(frozen=True)
class ExamReminderDue(DomainEvent):
    """Fired by the scheduler job — reminder window has opened for a student."""
    exam_id: ExamId | None = None
    student_id: StudentId | None = None
    hours_until_exam: int = 0
