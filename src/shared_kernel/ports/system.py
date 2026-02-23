"""
src/shared_kernel/ports/system.py
===================================
System-level port: Clock only.

FIX 8: ManasSSOPort and AuthenticatedUser have been MOVED to:
    src/contexts/identity/application/ports/outbound.py

Why: Authentication is owned by the Identity context, not shared_kernel.
     shared_kernel has no owner — putting auth logic there means everyone
     depends on it and no team is responsible for maintaining it.
     The Identity context owns auth; other contexts receive a StudentId
     (already in shared_kernel) after auth completes.

Clock stays here because it is a universal infrastructure concern used
by Assignments, Exams, Cafeteria, and Attendance — not owned by any one context.
"""
from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Provide the current UTC time.

    Inject this into every use case that touches time-sensitive logic.
    Never call datetime.now(UTC) directly in domain or application layers.
    Tests use FakeClock from tests/shared/fakes/clock.py.
    """

    def now(self) -> datetime:
        """Return current UTC datetime."""
        ...
