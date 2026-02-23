"""
src/shared_kernel/domain/identity.py
=====================================
Canonical identity VALUE OBJECTS shared across ALL bounded contexts.

Rules:
  - Zero external imports. Only stdlib + typing.
  - Reference types only — each context owns its full entity shape.
  - Contexts NEVER share mutable objects across boundaries.
  - Cross-context communication happens via these IDs + domain events only.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class EntityId:
    """Base for all entity identifiers."""
    value: UUID

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_str(cls, s: str) -> "EntityId":
        return cls(UUID(s))


@dataclass(frozen=True)
class StudentId(EntityId):
    """Reference to a student. Owned by the Identity context."""

@dataclass(frozen=True)
class TeacherId(EntityId):
    """Reference to a teacher. Owned by the Identity context."""

@dataclass(frozen=True)
class CourseId(EntityId):
    """Reference to a course definition. Owned by the Timetable context."""

@dataclass(frozen=True)
class RoomId(EntityId):
    """Reference to a physical room. Owned by the Timetable context."""

@dataclass(frozen=True)
class DepartmentId(EntityId):
    """Reference to an academic department."""

@dataclass(frozen=True)
class ExamId(EntityId):
    """Reference to an exam. Owned by the Exams context."""

@dataclass(frozen=True)
class AssignmentId(EntityId):
    """Reference to a homework assignment. Owned by the Assignments context."""

@dataclass(frozen=True)
class DocumentId(EntityId):
    """Reference to an uploaded document. Owned by the Documents context."""
