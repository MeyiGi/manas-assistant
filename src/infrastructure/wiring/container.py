"""
src/infrastructure/wiring/container.py
========================================
FIX 6: This file is now a THIN ORCHESTRATOR only (~50 lines).

Each bounded context has its own wiring file:
    _shared.py        → SharedInfrastructure
    _identity.py      → IdentityContainer
    _timetable.py     → TimetableContainer
    _credits.py       → CreditsContainer
    _assignments.py   → AssignmentsContainer
    _exams.py         → ExamsContainer
    _documents.py     → DocumentsContainer
    _grades.py        → GradesContainer
    _attendance.py    → AttendanceContainer
    _cafeteria.py     → CafeteriaContainer

Why: At 5+ developers, a single 2000-line container.py becomes a merge
conflict machine. Each developer owns one _<context>.py file. This file
just assembles the result. No merge conflicts on feature work.

Rules:
  1. This file only imports from the _<context>.py wiring modules.
  2. No concrete adapter class is ever imported here directly.
  3. Tests bypass this entirely and build their own fake containers.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.infrastructure.config.settings import Settings
from src.infrastructure.wiring._shared import SharedInfrastructure, build_shared
from src.infrastructure.wiring._identity import IdentityContainer, build_identity
from src.infrastructure.wiring._timetable import TimetableContainer, build_timetable
from src.infrastructure.wiring._credits import CreditsContainer, build_credits
from src.infrastructure.wiring._assignments import AssignmentsContainer, build_assignments
from src.infrastructure.wiring._exams import ExamsContainer, build_exams
from src.infrastructure.wiring._documents import DocumentsContainer, build_documents
from src.infrastructure.wiring._grades import GradesContainer, build_grades
from src.infrastructure.wiring._attendance import AttendanceContainer, build_attendance
from src.infrastructure.wiring._cafeteria import CafeteriaContainer, build_cafeteria


@dataclass
class PlatformContainer:
    """Single root object. Injected into FastAPI lifespan + CLI entry points."""
    settings: Settings
    shared: SharedInfrastructure
    identity: IdentityContainer
    timetable: TimetableContainer
    credits: CreditsContainer
    assignments: AssignmentsContainer
    exams: ExamsContainer
    documents: DocumentsContainer
    grades: GradesContainer
    attendance: AttendanceContainer
    cafeteria: CafeteriaContainer


def build_platform(settings: Settings | None = None) -> PlatformContainer:
    """Single composition root call. Called once at application startup."""
    if settings is None:
        settings = Settings.from_env()

    shared = build_shared(settings)

    return PlatformContainer(
        settings=settings,
        shared=shared,
        identity=build_identity(settings, shared),
        timetable=build_timetable(settings, shared),
        credits=build_credits(settings, shared),
        assignments=build_assignments(settings, shared),
        exams=build_exams(settings, shared),
        documents=build_documents(settings, shared),
        grades=build_grades(settings, shared),
        attendance=build_attendance(settings, shared),
        cafeteria=build_cafeteria(settings, shared),
    )
