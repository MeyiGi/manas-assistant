"""
src/contexts/exams/application/ports/outbound.py
=================================================
FIX 2: ExamNotificationPort defined HERE, not in shared_kernel.

Richer than AssignmentNotificationPort: includes room and duration info.
"""
from __future__ import annotations

from datetime import datetime
from typing import Protocol

from src.shared_kernel.domain.identity import ExamId, StudentId
from src.shared_kernel.ports.event_bus import EventBus  # noqa: F401
from src.shared_kernel.ports.system import Clock  # noqa: F401


class ExamRepository(Protocol):
    async def save(self, exam: object) -> None: ...
    async def get_by_id(self, id: ExamId) -> object | None: ...
    async def list_upcoming(self, from_dt: datetime, to_dt: datetime) -> list: ...
    async def list_by_course(self, course_code: str) -> list: ...


class SubscriptionRepository(Protocol):
    async def save(self, sub: object) -> None: ...
    async def get_by_student_and_exam(self, student_id: StudentId, exam_id: ExamId) -> object | None: ...
    async def list_due(self, now: datetime) -> list:
        """Used by reminder scheduler. Returns subscriptions where reminder is due."""
        ...


class ExamNotificationPort(Protocol):
    """Exam-specific notification. Richer than AssignmentNotificationPort.

    Concrete TelegramAdapter implements both Protocols independently.
    No shared base class needed — structural typing handles it.
    """
    async def notify_exam_approaching(
        self,
        student_id: StudentId,
        course_name: str,
        hours_until: int,
        room: str | None,
        duration_minutes: int,
    ) -> None: ...

    async def notify_exam_scheduled(
        self,
        student_id: StudentId,
        course_name: str,
        scheduled_at: datetime,
    ) -> None: ...
