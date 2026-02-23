"""src/contexts/timetable/domain/errors.py"""
from __future__ import annotations


class DomainError(Exception):
    """Base for all timetable domain errors."""


class TimetableEntryNotFound(DomainError):
    pass


class SavedTimetableNotFound(DomainError):
    pass


class ScrapeFailure(DomainError):
    def __init__(self, department_id: object, reason: str) -> None:
        super().__init__(f"Scrape failed for dept {department_id}: {reason}")


class InvalidDepartmentRange(DomainError):
    pass
