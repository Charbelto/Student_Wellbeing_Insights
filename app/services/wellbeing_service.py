from typing import List, Optional
from datetime import date
from app.database.models import WellbeingSurvey, StressLevel

class WellbeingService:
    def __init__(self):
        self._storage: List[WellbeingSurvey] = []

    def submit_survey(self, student_id: int, stress_level: int, hours_slept: float, comments: str = None) -> WellbeingSurvey:
        # Pydantic validation handles the int to Enum conversion if valid, but we should ensure robustness or let Pydantic raise ValueError
        
        # Since StressLevel is an IntEnum, passing an int that is not a valid member might raise ValueError during init if we are strictly typing,
        # or we can manually validate before creation to give better error messages.
        
        try:
            valid_stress = StressLevel(stress_level)
        except ValueError:
            raise ValueError(f"Invalid stress level: {stress_level}. Must be between 1 and 5.")

        survey = WellbeingSurvey(
            student_id=student_id,
            date=date.today(),
            stress_level=valid_stress,
            hours_slept=hours_slept,
            comments=comments,
            id=len(self._storage) + 1
        )
        self._storage.append(survey)
        return survey

    def get_student_history(self, student_id: int) -> List[WellbeingSurvey]:
        return [s for s in self._storage if s.student_id == student_id]

    def delete_survey(self, survey_id: int) -> bool:
        for i, survey in enumerate(self._storage):
            if survey.id == survey_id:
                self._storage.pop(i)
                return True
        raise ValueError(f"Survey with id {survey_id} not found")
