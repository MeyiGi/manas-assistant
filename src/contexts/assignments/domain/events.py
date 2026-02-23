"""
src/contexts/assignments/domain/events.py
==========================================
Events published by the Assignments bounded context.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from src.shared_kernel.domain.events import DomainEvent
from src.shared_kernel.domain.identity import AssignmentId, StudentId


@dataclass(frozen=True)
class AssignmentCreated(DomainEvent):
    assignment_id: AssignmentId | None = None
    student_id: StudentId | None = None
    due_at: datetime | None = None


@dataclass(frozen=True)
class AssignmentCompleted(DomainEvent):
    assignment_id: AssignmentId | None = None
    student_id: StudentId | None = None


@dataclass(frozen=True)
class AssignmentDeadlineApproaching(DomainEvent):
    """Fired by the scheduler — student needs a nudge."""
    assignment_id: AssignmentId | None = None
    student_id: StudentId | None = None
    hours_remaining: int = 0


@dataclass(frozen=True)
class AssignmentOverdue(DomainEvent):
    assignment_id: AssignmentId | None = None
    student_id: StudentId | None = None
