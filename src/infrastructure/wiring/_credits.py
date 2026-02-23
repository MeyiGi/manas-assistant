"""
src/infrastructure/wiring/_credits.py
=====================================
Composition root for the Credits bounded context.

This file is OWNED by the team working on the credits context.
No other wiring file needs to change when this context is implemented.
Zero merge conflicts with other context teams.

Implementation checklist:
  [ ] Instantiate outbound adapters (DB repos, HTTP clients, notification adapters)
  [ ] Inject into use-case constructors via their outbound port Protocols
  [ ] Return populated CreditsContainer
"""
from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.config.settings import Settings
from src.infrastructure.wiring._shared import SharedInfrastructure


@dataclass
class CreditsContainer:
    """
    Holds wired use-case instances for the Credits context.
    Members added here as use cases are implemented.

    Example (fill in when implementing):
        create_assignment: CreateAssignmentUseCase
        list_assignments:  ListAssignmentsUseCase
        check_deadlines:   CheckDeadlinesUseCase
    """
    pass


def build_credits(settings: Settings, shared: SharedInfrastructure) -> CreditsContainer:
    """
    Wire all adapters and use cases for the Credits bounded context.

    Example implementation (uncomment as you build):
        repo = SqlCreditsRepository(shared.db_session_factory)
        notifier = TelegramNotificationAdapter(settings.notifications)
        use_case = CreateCreditsUseCase(repo=repo, notifier=notifier, clock=shared.clock)
        return CreditsContainer(create_credits=use_case)
    """
    return CreditsContainer()
