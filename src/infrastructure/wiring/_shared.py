"""
src/infrastructure/wiring/_shared.py
======================================
Shared infrastructure: singletons used by all contexts.

Implementation checklist (fill in as you build each piece):
  [ ] SystemClock
  [ ] InMemoryEventBus → swap for RedisEventBus in production
  [ ] SQLAlchemy async engine + session factory
  [ ] httpx.AsyncClient with connection pool
"""
from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.config.settings import Settings


@dataclass
class SharedInfrastructure:
    """
    event_bus:           InMemoryEventBus | RedisEventBus
    clock:               SystemClock
    db_session_factory:  SQLAlchemy async session factory
    http_client:         httpx.AsyncClient (shared, connection-pooled)
    """
    pass  # fields added as implemented


def build_shared(settings: Settings) -> SharedInfrastructure:
    return SharedInfrastructure()
