"""
src/contexts/exams/domain/entities.py
=======================================
FIX 4: Exam.enrolled_student_ids: list[StudentId] REMOVED.

Why it was wrong:
  - 300+ students per exam = 300 UUIDs loaded every time ANY field is read.
  - Enrollment is a separate lifecycle from exam scheduling.
  - Concurrency issues: two students enrolling simultaneously fight over
    the same aggregate.

Enrollment is handled by StudentExamSubscription (already existed).
The subscription IS the enrollment record. Queries for "who is enrolled"
go to SubscriptionRepository, not through the Exam aggregate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from src.shared_kernel.domain.identity import CourseId, ExamId, RoomId


class ExamType(Enum):
    MIDTERM = "midterm"
    FINAL = "final"
    QUIZ = "quiz"
    MAKEUP = "makeup"


@dataclass
class Exam:
    """Aggregate root: an exam event (scheduling data only).

    Does NOT hold enrolled students — see StudentExamSubscription.
    Single responsibility: when, where, and what type of exam.
    """
    id: ExamId
    course_id: CourseId
    course_code: str
    course_name: str
    scheduled_at: datetime
    duration_minutes: int
    exam_type: ExamType
    room_id: RoomId | None
    created_at: datetime

    # NO enrolled_student_ids here — that's SubscriptionRepository's job

    @classmethod
    def schedule(
        cls,
        course_id: CourseId,
        course_code: str,
        course_name: str,
        scheduled_at: datetime,
        duration_minutes: int,
        exam_type: ExamType,
        room_id: RoomId | None = None,
    ) -> "Exam":
        return cls(
            id=ExamId(uuid4()),
            course_id=course_id,
            course_code=course_code,
            course_name=course_name,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            exam_type=exam_type,
            room_id=room_id,
            created_at=datetime.utcnow(),
        )

    def reschedule(self, new_time: datetime) -> None:
        self.scheduled_at = new_time

    def assign_room(self, room_id: RoomId) -> None:
        self.room_id = room_id


@dataclass
class StudentExamSubscription:
    """A student's enrollment + notification preferences for one exam.

    This is BOTH the enrollment record AND the notification config.
    Querying who is enrolled = querying this table, not the Exam aggregate.
    Reminder scheduler queries: SubscriptionRepository.list_due(now).
    """
    id: UUID
    student_id: "StudentId"  # noqa: F821
    exam_id: ExamId
    notify_before_hours: list[int] = field(default_factory=lambda: [24, 2])
    subscribed_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        student_id: "StudentId",  # noqa: F821
        exam_id: ExamId,
        notify_before_hours: list[int],
    ) -> "StudentExamSubscription":
        return cls(
            id=uuid4(),
            student_id=student_id,
            exam_id=exam_id,
            notify_before_hours=notify_before_hours,
        )
