from typing import List, Optional
from datetime import date
from app.database.models import WellbeingSurvey, StressLevel
from app.database.connection import get_db_connection

class WellbeingService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def submit_survey(self, student_id: int, stress_level: int, hours_slept: float, comments: str = None) -> WellbeingSurvey:
        try:
            valid_stress = StressLevel(stress_level)
        except ValueError:
            raise ValueError(f"Invalid stress level: {stress_level}. Must be between 1 and 5.")

        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        today = date.today()
        
        cursor.execute(
            "INSERT INTO wellbeing_surveys (student_id, date, stress_level, hours_slept, comments) VALUES (?, ?, ?, ?, ?)",
            (student_id, today, valid_stress.value, hours_slept, comments)
        )
        conn.commit()
        survey_id = cursor.lastrowid
        conn.close()

        return WellbeingSurvey(
            id=survey_id,
            student_id=student_id,
            date=today,
            stress_level=valid_stress,
            hours_slept=hours_slept,
            comments=comments
        )

    def get_student_history(self, student_id: int) -> List[WellbeingSurvey]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wellbeing_surveys WHERE student_id = ?", (student_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [WellbeingSurvey(
            id=row['id'],
            student_id=row['student_id'],
            date=row['date'],
            stress_level=StressLevel(row['stress_level']),
            hours_slept=row['hours_slept'],
            comments=row['comments']
        ) for row in rows]

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
    def get_all_surveys(self) -> List[WellbeingSurvey]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wellbeing_surveys")
        rows = cursor.fetchall()
        conn.close()
        
        return [WellbeingSurvey(
            id=row['id'],
            student_id=row['student_id'],
            date=row['date'],
            stress_level=StressLevel(row['stress_level']),
            hours_slept=row['hours_slept'],
            comments=row['comments']
        ) for row in rows]
