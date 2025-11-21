from typing import List
from datetime import date
from app.database.models import WellbeingSurvey, StressLevel

class WellbeingService:
    def __init__(self):
        self._storage = []

    def submit_survey(self, student_id: int, stress_level: int, hours_slept: float, comments: str = None) -> WellbeingSurvey:
        raise NotImplementedError

    def get_student_history(self, student_id: int) -> List[WellbeingSurvey]:
        raise NotImplementedError

