"""
src/infrastructure/wiring/_cafeteria.py
=====================================
Composition root for the Cafeteria bounded context.

This file is OWNED by the team working on the cafeteria context.
No other wiring file needs to change when this context is implemented.
Zero merge conflicts with other context teams.

Implementation checklist:
  [ ] Instantiate outbound adapters (DB repos, HTTP clients, notification adapters)
  [ ] Inject into use-case constructors via their outbound port Protocols
  [ ] Return populated CafeteriaContainer
"""
from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.config.settings import Settings
from src.infrastructure.wiring._shared import SharedInfrastructure


@dataclass
class CafeteriaContainer:
    """
    Holds wired use-case instances for the Cafeteria context.
    Members added here as use cases are implemented.

    Example (fill in when implementing):
        create_assignment: CreateAssignmentUseCase
        list_assignments:  ListAssignmentsUseCase
        check_deadlines:   CheckDeadlinesUseCase
    """
    pass


def build_cafeteria(settings: Settings, shared: SharedInfrastructure) -> CafeteriaContainer:
    """
    Wire all adapters and use cases for the Cafeteria bounded context.

    Example implementation (uncomment as you build):
        repo = SqlCafeteriaRepository(shared.db_session_factory)
        notifier = TelegramNotificationAdapter(settings.notifications)
        use_case = CreateCafeteriaUseCase(repo=repo, notifier=notifier, clock=shared.clock)
        return CafeteriaContainer(create_cafeteria=use_case)
    """
    return CafeteriaContainer()
