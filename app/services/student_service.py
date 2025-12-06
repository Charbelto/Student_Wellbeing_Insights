from typing import List, Optional
import sqlite3
from app.database.models import Student
from app.database.connection import get_db_connection
import app.database.queries as q


class StudentService:
    def __init__(self, db_name: str = 'wellbeing.db'):
        self.db_name = db_name

    def create_student(
        self,
        university_id: str,
        name: str,
        email: Optional[str] = None,
        degree_name: Optional[str] = None,
        year: Optional[int] = None,
        medical_info: Optional[str] = None,
        disabilities: Optional[str] = None,
    ) -> Student:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()

        cursor.execute(q.GET_STUDENT_BY_UNIVERSITY_ID, (university_id,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return self._map_row_to_student(existing)

        try:
            cursor.execute(
                q.INSERT_STUDENT,
                (
                    university_id,
                    name,
                    email,
                    degree_name,
                    year,
                    medical_info,
                    disabilities,
                ),
            )
            conn.commit()
            new_id = cursor.lastrowid
            cursor.execute(q.GET_STUDENT_BY_ID, (new_id,))
            row = cursor.fetchone()
            conn.close()
            return self._map_row_to_student(row)
        except sqlite3.IntegrityError as exc:
            conn.close()
            raise ValueError(f"Database error: {exc}") from exc

    def get_student(self, student_id: int) -> Optional[Student]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_STUDENT_BY_ID, (student_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._map_row_to_student(row)
        return None

    def get_all_students(self) -> List[Student]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.GET_ALL_STUDENTS)
        rows = cursor.fetchall()
        conn.close()
        return [self._map_row_to_student(row) for row in rows]

    def delete_student(self, student_id: int) -> bool:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(q.DELETE_STUDENT, (student_id,))
        if cursor.rowcount == 0:
            conn.close()
            raise ValueError(f"Student with id {student_id} not found")
        conn.commit()
        conn.close()
        return True

    def _map_row_to_student(self, row) -> Student:
        return Student(
            id=row["id"],
            university_id=row["university_id"],
            name=row["name"],
            email=row["email"],
            degree_name=row["degree_name"],
            year=row["year"],
            medical_info=row["medical_info"],
            disabilities=row["disabilities"],
        )
