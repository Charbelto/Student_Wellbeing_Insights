from typing import List
from datetime import datetime
from app.database.models import WellbeingSurvey, StressLevel
from app.database.connection import get_db_connection
import app.database.queries as q


class WellbeingService:
    def __init__(self, db_name: str = 'wellbeing.db'):
        self.db_name = db_name

    def submit_survey(self, student_id: int, stress_level: int, hours_slept: float, comments: str = None) -> WellbeingSurvey:
        if not (1 <= stress_level <= 5):
            raise ValueError("Stress level must be between 1 and 5")
        if hours_slept < 0:
            raise ValueError("Hours slept cannot be negative")

        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.INSERT_SURVEY, (student_id, stress_level, hours_slept, comments))
        conn.commit()
        survey_id = cursor.lastrowid
        cursor.execute(q.GET_SURVEY_BY_ID, (survey_id,))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_survey(row)

    def get_student_history(self, student_id: int) -> List[WellbeingSurvey]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_SURVEYS_FOR_STUDENT, (student_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_survey(row) for row in rows]

    def delete_survey(self, survey_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.DELETE_SURVEY, (survey_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Survey with id {survey_id} not found")
        conn.commit()
        conn.close()
        return True

    def _row_to_survey(self, row) -> WellbeingSurvey:
        return WellbeingSurvey(
            id=row["id"],
            student_id=row["student_id"],
            stress_level=StressLevel(row["stress_level"]),
            hours_slept=row["hours_slept"],
            comments=row["comments"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
