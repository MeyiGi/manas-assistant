"""
src/shared_kernel/ports/event_bus.py
======================================
Outbound port: domain event bus.

FIX 7: EventBus.subscribe() is now generic-typed so handlers receive the
correct event type without isinstance checks or casts.

Usage:
    bus.subscribe(ExamScheduled, handle_exam_scheduled)
    # handle_exam_scheduled receives ExamScheduled, not DomainEvent
"""
from __future__ import annotations

from typing import Awaitable, Callable, Protocol, TypeVar

from src.shared_kernel.domain.events import DomainEvent

T = TypeVar("T", bound=DomainEvent)

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus(Protocol):
    """Publish domain events and register typed subscribers."""

    async def publish(self, event: DomainEvent) -> None:
        """Publish *event* to all registered subscribers for its type."""
        ...

    def subscribe(
        self,
        event_type: type[T],
        handler: Callable[[T], Awaitable[None]],
    ) -> None:
        """Register *handler* to be called for every event of *event_type*.

        Args:
            event_type: The concrete DomainEvent subclass to subscribe to.
            handler:    Async callable receiving the exact event type — no cast needed.

        Example:
            bus.subscribe(ExamScheduled, my_handler)
            # my_handler(event: ExamScheduled) — fully typed
        """
        ...
