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
    student_id: str
    degree_id: int
    degree_name: str
    year: int
    age_band: str
    domicile: str
    go_home_frequency: Optional[str] = None
    extracurricular_per_week: Optional[int] = None
    avg_commute_time_min: Optional[int] = None
    avg_screen_time_hours: Optional[int] = None
    commute_type: Optional[str] = None
    medical_information: Optional[str] = None
    disabilities: Optional[str] = None

class StudentName(BaseModel):
    student_id: str
    name: str

class Degree(BaseModel):
    degree_id: int
    degree_name: str

class Module(BaseModel):
    module_id: int
    degree_id: int
    code: str
    name: str
    semester: int
    lecture_day: str
    lecture_time: str
    difficulty_level: Optional[str] = None

class ModuleFeedback(BaseModel):
    feedback_id: str
    student_id: str
    module_id: int
    engaging_content: int
    comfortable_asking_questions: int
    pace_rating: int
    prepared_for_exams: int
    hours_outside_class: int

class Attendance(BaseModel):
    student_id: str
    module_id: int
    total_sessions: int
    attended_sessions: int
    attendance_rate: float

class Survey(BaseModel):
    student_id: str
    week: int
    stress_level: int
    hours_slept: int
    mood_score: int

class Submission(BaseModel):
    submission_id: int
    student_id: str
    module_id: int
    semester: int
    deadline_datetime: datetime
    submitted_datetime: datetime
    early_late_submissions: int
    mark: Optional[float] = None
    late: bool

class RiskIndicator(BaseModel):
    student_id: str
    avg_stress: float
    late_submissions: int
    avg_mark: float
    min_mark: float
    max_mark: float
    risk_level: str