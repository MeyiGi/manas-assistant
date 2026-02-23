"""
src/contexts/assignments/application/ports/outbound.py
=======================================================
FIX 2: AssignmentNotificationPort defined HERE, not in shared_kernel.

The port is narrow — only the notification shapes this context needs.
The concrete TelegramAdapter implements this Protocol alongside
ExamNotificationPort without any inheritance: structural typing handles it.
"""
from __future__ import annotations

from datetime import datetime
from typing import Awaitable, Callable, Protocol

from src.shared_kernel.domain.events import DomainEvent
from src.shared_kernel.domain.identity import AssignmentId, StudentId
from src.shared_kernel.ports.event_bus import EventBus  # noqa: F401 (re-export)
from src.shared_kernel.ports.system import Clock  # noqa: F401 (re-export)


class AssignmentRepository(Protocol):
    async def save(self, assignment: object) -> None: ...
    async def get_by_id(self, id: AssignmentId) -> object | None: ...
    async def list_by_student(self, student_id: StudentId, status: str | None = None) -> list: ...
    async def list_due_within(self, hours: int) -> list:
        """For the scheduler job — returns assignments with deadline in next N hours."""
        ...


class AssignmentNotificationPort(Protocol):
    """Narrowly typed for what the Assignments context actually needs to send.

    Separate from ExamNotificationPort intentionally:
    - Different content (no room info, no duration).
    - May evolve independently (SMS-only for overdue, Telegram for approaching).
    """
    async def notify_deadline_approaching(
        self,
        student_id: StudentId,
        assignment_title: str,
        hours_remaining: int,
    ) -> None: ...

    async def notify_overdue(
        self,
        student_id: StudentId,
        assignment_title: str,
    ) -> None: ...
