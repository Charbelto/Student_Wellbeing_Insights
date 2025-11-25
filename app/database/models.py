from enum import Enum
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
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
    id: int # e.g. u2554630 (might need to handle string IDs if they have 'u' prefix, but schema said integer. The excel has 'u' prefix. I should change schema to Text or strip 'u')
    name: str # Excel doesn't have name? It has ID. I might need to fake names or use ID as name.
    email: Optional[str] = None
    degree_name: Optional[str] = None
    medical_info: Optional[str] = None
    disabilities: Optional[str] = None
    
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
