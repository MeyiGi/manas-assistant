"""
src/infrastructure/wiring/_timetable.py
=====================================
Composition root for the Timetable bounded context.

This file is OWNED by the team working on the timetable context.
No other wiring file needs to change when this context is implemented.
Zero merge conflicts with other context teams.

Implementation checklist:
  [ ] Instantiate outbound adapters (DB repos, HTTP clients, notification adapters)
  [ ] Inject into use-case constructors via their outbound port Protocols
  [ ] Return populated TimetableContainer
"""
from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.config.settings import Settings
from src.infrastructure.wiring._shared import SharedInfrastructure


@dataclass
class TimetableContainer:
    """
    Holds wired use-case instances for the Timetable context.
    Members added here as use cases are implemented.

    Example (fill in when implementing):
        create_assignment: CreateAssignmentUseCase
        list_assignments:  ListAssignmentsUseCase
        check_deadlines:   CheckDeadlinesUseCase
    """
    pass


def build_timetable(settings: Settings, shared: SharedInfrastructure) -> TimetableContainer:
    """
    Wire all adapters and use cases for the Timetable bounded context.

    Example implementation (uncomment as you build):
        repo = SqlTimetableRepository(shared.db_session_factory)
        notifier = TelegramNotificationAdapter(settings.notifications)
        use_case = CreateTimetableUseCase(repo=repo, notifier=notifier, clock=shared.clock)
        return TimetableContainer(create_timetable=use_case)
    """
    return TimetableContainer()
