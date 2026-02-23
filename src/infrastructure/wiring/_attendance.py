"""
src/infrastructure/wiring/_attendance.py
=====================================
Composition root for the Attendance bounded context.

This file is OWNED by the team working on the attendance context.
No other wiring file needs to change when this context is implemented.
Zero merge conflicts with other context teams.

Implementation checklist:
  [ ] Instantiate outbound adapters (DB repos, HTTP clients, notification adapters)
  [ ] Inject into use-case constructors via their outbound port Protocols
  [ ] Return populated AttendanceContainer
"""
from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.config.settings import Settings
from src.infrastructure.wiring._shared import SharedInfrastructure


@dataclass
class AttendanceContainer:
    """
    Holds wired use-case instances for the Attendance context.
    Members added here as use cases are implemented.

    Example (fill in when implementing):
        create_assignment: CreateAssignmentUseCase
        list_assignments:  ListAssignmentsUseCase
        check_deadlines:   CheckDeadlinesUseCase
    """
    pass


def build_attendance(settings: Settings, shared: SharedInfrastructure) -> AttendanceContainer:
    """
    Wire all adapters and use cases for the Attendance bounded context.

    Example implementation (uncomment as you build):
        repo = SqlAttendanceRepository(shared.db_session_factory)
        notifier = TelegramNotificationAdapter(settings.notifications)
        use_case = CreateAttendanceUseCase(repo=repo, notifier=notifier, clock=shared.clock)
        return AttendanceContainer(create_attendance=use_case)
    """
    return AttendanceContainer()
