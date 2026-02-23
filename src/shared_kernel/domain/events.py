"""
src/shared_kernel/domain/events.py
====================================
Base DomainEvent class ONLY.

══════════════════════════════════════════════════
GOLDEN RULE: This file contains ZERO context-specific event classes.
══════════════════════════════════════════════════

Each bounded context owns its events in:
    src/contexts/<context>/domain/events.py

Cross-context subscriptions:
    A subscriber context may import from a publisher context's domain/events.py.
    That is the ONLY permitted cross-context import (besides shared_kernel).
    It must be documented in the subscriber's CONTEXT.py.

Why this rule exists:
    If ExamScheduled, AssignmentCreated, TimetableScraped all lived here,
    then changing any one of them would break every other context's CI pipeline
    — even contexts that have nothing to do with the changed event.
    The shared kernel is for identity TYPES, not event catalogues.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Immutable base for all domain events in all bounded contexts."""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
