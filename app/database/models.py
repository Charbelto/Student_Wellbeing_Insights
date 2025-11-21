from enum import Enum
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field

class StressLevel(int, Enum):
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5

class Student(BaseModel):
    id: int
    name: str
    email: str

class Attendance(BaseModel):
    id: Optional[int] = None
    student_id: int
    date: date
    status: str
    course_id: str

class Submission(BaseModel):
    id: Optional[int] = None
    student_id: int
    assignment_id: str
    submission_date: datetime
    grade: Optional[float] = None

class WellbeingSurvey(BaseModel):
    id: Optional[int] = None
    student_id: int
    date: date
    stress_level: StressLevel
    hours_slept: float
    comments: Optional[str] = None

