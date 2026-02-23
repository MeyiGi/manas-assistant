"""
src/infrastructure/wiring/_assignments.py
=====================================
Composition root for the Assignments bounded context.

This file is OWNED by the team working on the assignments context.
No other wiring file needs to change when this context is implemented.
Zero merge conflicts with other context teams.

Implementation checklist:
  [ ] Instantiate outbound adapters (DB repos, HTTP clients, notification adapters)
  [ ] Inject into use-case constructors via their outbound port Protocols
  [ ] Return populated AssignmentsContainer
"""
from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.config.settings import Settings
from src.infrastructure.wiring._shared import SharedInfrastructure


@dataclass
class AssignmentsContainer:
    """
    Holds wired use-case instances for the Assignments context.
    Members added here as use cases are implemented.

    Example (fill in when implementing):
        create_assignment: CreateAssignmentUseCase
        list_assignments:  ListAssignmentsUseCase
        check_deadlines:   CheckDeadlinesUseCase
    """
    pass


def build_assignments(settings: Settings, shared: SharedInfrastructure) -> AssignmentsContainer:
    """
    Wire all adapters and use cases for the Assignments bounded context.

    Example implementation (uncomment as you build):
        repo = SqlAssignmentsRepository(shared.db_session_factory)
        notifier = TelegramNotificationAdapter(settings.notifications)
        use_case = CreateAssignmentsUseCase(repo=repo, notifier=notifier, clock=shared.clock)
        return AssignmentsContainer(create_assignments=use_case)
    """
    return AssignmentsContainer()
