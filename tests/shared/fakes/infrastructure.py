"""
tests/shared/fakes/infrastructure.py
======================================
Shared fake implementations for testing.

RULE (Golden Rule 10): Tests in tests/contexts/<ctx>/ import from HERE only.
They never import from another context's test directory.

These fakes implement shared_kernel ports — they have no context-specific logic.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Awaitable, Callable, TypeVar
from unittest.mock import AsyncMock

from src.shared_kernel.domain.events import DomainEvent
from src.shared_kernel.ports.event_bus import EventBus
from src.shared_kernel.ports.system import Clock

T = TypeVar("T", bound=DomainEvent)


class FakeClock:
    """Frozen clock for deterministic tests.

    Usage:
        clock = FakeClock(datetime(2024, 9, 1, 10, 0))
        clock.advance_hours(24)
        assert clock.now() == datetime(2024, 9, 2, 10, 0)
    """

    def __init__(self, fixed: datetime | None = None) -> None:
        self._now = fixed or datetime(2024, 1, 15, 12, 0, 0)

    def now(self) -> datetime:
        return self._now

    def advance_hours(self, hours: float) -> None:
        from datetime import timedelta
        self._now += timedelta(hours=hours)

    def advance_days(self, days: int) -> None:
        from datetime import timedelta
        self._now += timedelta(days=days)

    def set(self, dt: datetime) -> None:
        self._now = dt


class FakeEventBus:
    """In-memory event bus. Captures published events for assertions.

    Usage:
        bus = FakeEventBus()
        bus.subscribe(ExamScheduled, handler)
        # ... call use case ...
        assert len(bus.published) == 1
        assert isinstance(bus.published[0], ExamScheduled)
    """

    def __init__(self) -> None:
        self.published: list[DomainEvent] = []
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    async def publish(self, event: DomainEvent) -> None:
        self.published.append(event)
        for handler in self._handlers.get(type(event), []):
            await handler(event)

    def subscribe(self, event_type: type[T], handler: Callable[[T], Awaitable[None]]) -> None:
        self._handlers[event_type].append(handler)

    def events_of(self, event_type: type[T]) -> list[T]:
        """Filter published events by type."""
        return [e for e in self.published if isinstance(e, event_type)]

    def clear(self) -> None:
        self.published.clear()
