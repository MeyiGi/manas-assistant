"""
src/contexts/timetable/domain/value_objects.py
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum


_TIME_RE = re.compile(r"^(\d{2}:\d{2})-(\d{2}:\d{2})$")


@dataclass(frozen=True)
class TimeSlot:
    raw: str

    def start(self) -> str:
        m = _TIME_RE.match(self.raw.strip())
        return m.group(1) if m else ""

    def end(self) -> str:
        m = _TIME_RE.match(self.raw.strip())
        return m.group(2) if m else ""

    def is_valid(self) -> bool:
        return bool(_TIME_RE.match(self.raw.strip()))

    def overlaps(self, other: "TimeSlot") -> bool:
        """Return True if self and other share any time."""
        if not (self.is_valid() and other.is_valid()):
            return False
        return self.start() < other.end() and other.start() < self.end()

    def __str__(self) -> str:
        return self.raw


class WeekDay(Enum):
    MONDAY = ("Pazartesi", 1)
    TUESDAY = ("Salı", 2)
    WEDNESDAY = ("Çarşamba", 3)
    THURSDAY = ("Perşembe", 4)
    FRIDAY = ("Cuma", 5)
    SATURDAY = ("Cumartesi", 6)
    SUNDAY = ("Pazar", 7)

    def __init__(self, turkish: str, order: int) -> None:
        self.turkish = turkish
        self.order = order

    @classmethod
    def from_turkish(cls, name: str) -> "WeekDay":
        for member in cls:
            if member.turkish == name:
                return member
        raise ValueError(f"Unknown Turkish day name: {name!r}")


@dataclass(frozen=True)
class CourseCode:
    value: str

    def prefix(self) -> str:
        return self.value.split("-", 1)[0].upper()

    def section(self) -> str:
        parts = self.value.split("-", 1)
        return parts[1] if len(parts) > 1 else ""

    def year_digit(self) -> str:
        s = self.section()
        return s[0] if s else ""

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class DepartmentRange:
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(f"start ({self.start}) must be <= end ({self.end})")
        if self.start < 0:
            raise ValueError("start must be non-negative")

    def ids(self) -> list[int]:
        return list(range(self.start, self.end + 1))
