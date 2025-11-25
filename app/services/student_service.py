from typing import List, Optional
from app.database.models import Student
from app.database.connection import get_db_connection
import sqlite3

class StudentService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def create_student(self, name: str, email: str) -> Student:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO students (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
            student_id = cursor.lastrowid
            conn.close()
            return Student(id=student_id, name=name, email=email)
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"Student with email {email} already exists.")

    def get_student(self, student_id: int) -> Optional[Student]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Student(id=row['id'], name=row['name'], email=row['email'])
        return None

    def get_all_students(self) -> List[Student]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        conn.close()
        
        return [Student(id=row['id'], name=row['name'], email=row['email']) for row in rows]

