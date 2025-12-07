from typing import List, Optional
from app.database.models import Student
from app.database.connection import get_db_connection
import app.database.queries as q
import sqlite3

class StudentService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def create_student(self, name: str,
                        student_id: str,
                        degree_id: int = 1,
                        degree_name: str = "General Studies",
                        year: int = 1,
                        age_band: str = "18-21",
                        domicile: str = "UK",
                        go_home_frequency: str = None,
                        extracurricular_per_week: int = None,
                        avg_commute_time_min: int = None,
                        avg_screen_time_hours: int = None,
                        commute_type: str = None,
                        medical_information: str = None,
                        disabilities: str = None) -> Student:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        try:
            # Check if exists by university_id
            cursor.execute(q.GET_STUDENT_BY_ID, (student_id,))
            existing = cursor.fetchone()
            if existing:
                return self.get_student(existing['student_id'])

            cursor.execute(q.INSERT_STUDENT, 
                           (student_id,
                            degree_id,
                            degree_name,
                            year,
                            age_band,
                            domicile,
                            go_home_frequency,
                            extracurricular_per_week,
                            avg_commute_time_min,
                            avg_screen_time_hours,
                            commute_type,
                            medical_information,
                            disabilities))
            cursor.execute(q.INSERT_NAME, (student_id, name))
            conn.commit()
            conn.close()
            
            # Build object (simplified for return)
            return Student(
                student_id=student_id, 
                id=student_id,
                name=name,
                degree_id=degree_id,
                degree_name=degree_name,
                year=year,
                domicile=domicile,
                medical_information=medical_information,
                disabilities=disabilities
            )
        except sqlite3.IntegrityError as e:
            conn.close()
            raise ValueError(f"Database error: {e}")

    def get_student(self, student_id: str) -> Optional[Student]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_STUDENT_AND_NAME_BY_ID, (student_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._map_row_to_student(row)
        return None

    def get_all_students(self) -> List[Student]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_ALL_STUDENTS_AND_NAME)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._map_row_to_student(row) for row in rows]

    def _map_row_to_student(self, row) -> Student:
        # Handle potential missing name by using student_id
        display_name = row['name'] if row['name'] else row['student_id']
        
        # Build object (simplified for return)
        return Student(
            student_id=row['student_id'],
            id=row['student_id'],
            name = display_name,
            degree_id=row['degree_id'],
            degree_name=row['degree_name'],
            year=row['year'],
            domicile=row['domicile'],
            medical_information=row['medical_information'],
            disabilities=row['disabilities']
        )


    def delete_student(self, student_id: str) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Delete related records first (if no cascade)
            cursor.execute(q.DELETE_STUDENT, (student_id,))
            cursor.execute(q.DELETE_NAME, (student_id,))
            cursor.execute(q.DELETE_STUDENT_FEEDBACK, (student_id,))
            cursor.execute(q.DELETE_STUDENT_ATTENDANCE, (student_id,))
            cursor.execute(q.DELETE_STUDENT_SURVEY, (student_id,))
            cursor.execute(q.DELETE_STUDENT_SUBMISSIONS, (student_id,))
            cursor.execute(q.DELETE_RISK, (student_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
