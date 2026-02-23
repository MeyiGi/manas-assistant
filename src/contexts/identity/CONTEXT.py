"""
src/contexts/identity/
=======================
IDENTITY BOUNDED CONTEXT  (FIX 8 — new context)

FIX 8: AuthenticatedUser and ManasSSOPort were homeless — spread between
shared_kernel and the attendance context. Auth logic cannot live in shared_kernel
(no owner, everyone depends on it) and attendance should not own identity.

This context owns:
  - User entity (platform-side user record linked to Manas student number)
  - Authentication via Manas SSO portal
  - JWT token lifecycle
  - Publishing UserAuthenticated, UserRegistered events

Other contexts receive a StudentId AFTER auth completes. They never touch
credentials or session tokens.
"""
from __future__ import annotations

# ── Domain ──────────────────────────────────────────────────────────────────

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from src.shared_kernel.domain.identity import StudentId, TeacherId


class UserRole(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


@dataclass
class User:
    """Aggregate root: a platform user.

    Created on first successful Manas portal login.
    Credentials are NEVER stored — only the student_id reference.
    """
    id: UUID
    student_id: StudentId          # canonical identity reference
    full_name: str
    email: str
    manas_username: str            # Manas login ID (not password)
    role: UserRole
    created_at: datetime
    last_login_at: datetime | None = None

    @classmethod
    def register(
        cls,
        student_id: StudentId,
        full_name: str,
        email: str,
        manas_username: str,
        role: UserRole = UserRole.STUDENT,
    ) -> "User":
        return cls(
            id=uuid4(),
            student_id=student_id,
            full_name=full_name,
            email=email,
            manas_username=manas_username,
            role=role,
            created_at=datetime.utcnow(),
        )

    def record_login(self) -> None:
        self.last_login_at = datetime.utcnow()


# ── Application ports ────────────────────────────────────────────────────────

from typing import Protocol


@dataclass(frozen=True)
class AuthenticatedUser:
    """Result of a successful Manas portal login.

    Moved here from shared_kernel (FIX 8).
    Only the Identity context and the Attendance context (via its own SSO port)
    work with this type. Other contexts receive StudentId only.
    """
    student_id: StudentId
    full_name: str
    email: str
    manas_username: str
    raw_session_token: str   # opaque — used only by Manas HTTP adapter, discarded after use


class ManasSSOPort(Protocol):
    """Authenticate against the Manas University student portal.

    Moved here from shared_kernel (FIX 8).
    Implemented by adapters/outbound/http/manas_sso.py.
    """
    async def login(self, username: str, password: str) -> AuthenticatedUser:
        """Returns AuthenticatedUser or raises AuthenticationFailed."""
        ...


class UserRepository(Protocol):
    async def find_by_student_id(self, student_id: StudentId) -> User | None: ...
    async def save(self, user: User) -> None: ...


class TokenIssuer(Protocol):
    """Issue and verify JWT tokens."""
    def issue(self, user: User) -> str: ...
    def verify(self, token: str) -> StudentId: ...


# ── Inbound use-case interfaces ──────────────────────────────────────────────

@dataclass(frozen=True)
class LoginCommand:
    username: str
    password: str


@dataclass(frozen=True)
class LoginResult:
    token: str
    student_id: str
    full_name: str
    role: str


class LoginUseCase(Protocol):
    async def execute(self, cmd: LoginCommand) -> LoginResult: ...


class GetCurrentUserUseCase(Protocol):
    async def execute(self, token: str) -> User: ...
