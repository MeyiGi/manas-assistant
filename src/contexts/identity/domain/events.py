"""
src/contexts/identity/domain/events.py
========================================
Events published by the Identity bounded context.
"""
from __future__ import annotations
from dataclasses import dataclass
from src.shared_kernel.domain.events import DomainEvent
from src.shared_kernel.domain.identity import StudentId


@dataclass(frozen=True)
class UserAuthenticated(DomainEvent):
    """Fired after a successful Manas portal login."""
    student_id: StudentId | None = None


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    student_id: StudentId | None = None
    email: str = ""


@dataclass(frozen=True)
class SessionExpired(DomainEvent):
    student_id: StudentId | None = None
