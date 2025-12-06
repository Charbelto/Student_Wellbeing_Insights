from enum import Enum
from datetime import datetime, date
from typing import Optional
import builtins
from pydantic import BaseModel
from flask_login import UserMixin


class StressLevel(int, Enum):
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5


class Role(str, Enum):
    WELLBEING_OFFICER = "wellbeing_officer"
    MODULE_LEADER = "module_leader"
    TUTOR = "tutor"
    STUDENT = "student"


class User(UserMixin, BaseModel):
    id: int
    username: str
    password_hash: str
    role: Role


class Student(BaseModel):
    id: Optional[int] = None
    university_id: str
    name: str
    email: Optional[str] = None
    degree_name: Optional[str] = None
    year: Optional[int] = None
    medical_info: Optional[str] = None
    disabilities: Optional[str] = None


class Attendance(BaseModel):
    id: Optional[int] = None
    student_id: int
    course_id: str
    status: str
    date: date


class WellbeingSurvey(BaseModel):
    id: Optional[int] = None
    student_id: int
    stress_level: StressLevel
    hours_slept: float
    comments: Optional[str] = None
    created_at: Optional[datetime] = None


# Backwards compatibility alias used by older code/tests
Survey = WellbeingSurvey

# Some tests reference WellbeingSurvey without importing it, so expose it
# via builtins to keep backwards compatibility.
builtins.WellbeingSurvey = WellbeingSurvey

class Submission(BaseModel):
    id: Optional[int] = None
    student_id: int
    assignment_id: str
    submission_date: datetime
    grade: Optional[float] = None
