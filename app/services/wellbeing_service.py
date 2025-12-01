from typing import List, Optional
from datetime import date
from app.database.models import Survey, StressLevel
from app.database.connection import get_db_connection

class WellbeingService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def submit_survey(self, student_id: str, week: int, stress_level: int, hours_slept: int, mood_score: int,) -> Survey:
        # Basic validation – adjust ranges if you have explicit rules
        if not (1 <= stress_level <= 5):
            raise ValueError(f"Invalid stress level: {stress_level}. Must be between 1 and 5.")

        if hours_slept < 0:
            raise ValueError("Hours slept cannot be negative.")

        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO wellbeing_surveys (student_id, week, stress_level, hours_slept, mood_score)
            VALUES (?, ?, ?, ?, ?)
            """,
            (student_id, week, stress_level, hours_slept, mood_score),
        )
        conn.commit()
        conn.close()

        # Return a Survey Pydantic model instance
        return Survey(
            student_id=student_id,
            week=week,
            stress_level=stress_level,
            hours_slept=hours_slept,
            mood_score=mood_score,
        )

    def get_student_history(self, student_id: str) -> List[Survey]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT student_id, week, stress_level, hours_slept, mood_score
            FROM wellbeing_surveys
            WHERE student_id = ?
            ORDER BY week
            """,
            (student_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Survey(
                student_id=row["student_id"],
                week=row["week"],
                stress_level=row["stress_level"],
                hours_slept=row["hours_slept"],
                mood_score=row["mood_score"],
            )
            for row in rows
        ]

    def delete_survey(self, survey_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM wellbeing_surveys WHERE id = ?", (survey_id,))
        if not cursor.fetchone():
            conn.close()
            raise ValueError(f"Survey with id {survey_id} not found")
            
        cursor.execute("DELETE FROM wellbeing_surveys WHERE id = ?", (survey_id,))
        conn.commit()
        conn.close()
        return True
    
    # Added for Analytics
    def get_all_surveys(self) -> List[Survey]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wellbeing_surveys")
        rows = cursor.fetchall()
        conn.close()
        
        return [Survey(
            student_id=row["student_id"],
            week=row["week"],
            stress_level=row["stress_level"],
            hours_slept=row["hours_slept"],
            mood_score=row["mood_score"],
        ) for row in rows]
