"""
src/infrastructure/wiring/_documents.py
=====================================
Composition root for the Documents bounded context.

This file is OWNED by the team working on the documents context.
No other wiring file needs to change when this context is implemented.
Zero merge conflicts with other context teams.

Implementation checklist:
  [ ] Instantiate outbound adapters (DB repos, HTTP clients, notification adapters)
  [ ] Inject into use-case constructors via their outbound port Protocols
  [ ] Return populated DocumentsContainer
"""
from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.config.settings import Settings
from src.infrastructure.wiring._shared import SharedInfrastructure


@dataclass
class DocumentsContainer:
    """
    Holds wired use-case instances for the Documents context.
    Members added here as use cases are implemented.

    Example (fill in when implementing):
        create_assignment: CreateAssignmentUseCase
        list_assignments:  ListAssignmentsUseCase
        check_deadlines:   CheckDeadlinesUseCase
    """
    pass


def build_documents(settings: Settings, shared: SharedInfrastructure) -> DocumentsContainer:
    """
    Wire all adapters and use cases for the Documents bounded context.

    Example implementation (uncomment as you build):
        repo = SqlDocumentsRepository(shared.db_session_factory)
        notifier = TelegramNotificationAdapter(settings.notifications)
        use_case = CreateDocumentsUseCase(repo=repo, notifier=notifier, clock=shared.clock)
        return DocumentsContainer(create_documents=use_case)
    """
    return DocumentsContainer()
