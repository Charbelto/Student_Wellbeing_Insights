from typing import List, Optional
from app.database.models import Student
from app.database.connection import get_db_connection
import sqlite3

class StudentService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def create_student(self, university_id: str, name: str = None, email: str = None, 
                       degree_name: str = None, year: int = None, 
                       medical_info: str = None, disabilities: str = None,
                       commute_type: str = None, avg_commute_time_min: float = None,
                       avg_screen_time_hours: float = None) -> Student:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        try:
            # Check if exists by university_id
            cursor.execute("SELECT id FROM students WHERE university_id = ?", (university_id,))
            existing = cursor.fetchone()
            if existing:
                return self.get_student(existing['id'])

            cursor.execute(
                """INSERT INTO students (
                    university_id, name, email, degree_name, year, 
                    medical_info, disabilities, commute_type, 
                    avg_commute_time_min, avg_screen_time_hours
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (university_id, name, email, degree_name, year, 
                 medical_info, disabilities, commute_type, 
                 avg_commute_time_min, avg_screen_time_hours)
            )
            conn.commit()
            student_id = cursor.lastrowid
            conn.close()
            
            # Build object (simplified for return)
            return Student(
                id=student_id, 
                name=name or university_id, # Fallback to ID if name missing
                email=email,
                degree_name=degree_name,
                medical_info=medical_info,
                disabilities=disabilities
            )
        except sqlite3.IntegrityError as e:
            conn.close()
            raise ValueError(f"Database error: {e}")

    def get_student(self, student_id: int) -> Optional[Student]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._map_row_to_student(row)
        return None

    def get_all_students(self) -> List[Student]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        conn.close()
        
        return [self._map_row_to_student(row) for row in rows]

    def _map_row_to_student(self, row) -> Student:
        # Handle potential missing name by using university_id
        display_name = row['name'] if row['name'] else row['university_id']
        return Student(
            id=row['id'],
            university_id=row['university_id'],
            name=display_name,
            email=row['email'],
            degree_name=row['degree_name'],
            medical_info=row['medical_info'],
            disabilities=row['disabilities']
        )

    def delete_student(self, student_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Delete related records first (if no cascade)
            cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM wellbeing_surveys WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM submissions WHERE student_id = ?", (student_id,))
            
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            raise e
