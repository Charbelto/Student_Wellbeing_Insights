import pandas as pd
from app.services.student_service import StudentService
from app.services.user_service import UserService
from app.database.models import Role
from app.database.connection import init_db
import os

def seed_users(db_name='wellbeing.db'):
    print("Seeding users...")
    service = UserService(db_name)
    
    # Default Users
    users = [
        ("officer", "admin123", Role.WELLBEING_OFFICER),
        ("leader", "lead123", Role.MODULE_LEADER),
        ("tutor", "tutor123", Role.TUTOR)
    ]
    
    for username, password, role in users:
        if not service.get_user_by_username(username):
            service.create_user(username, password, role)
            print(f"Created user: {username}")
        else:
            print(f"User {username} already exists")

def import_students_from_excel(file_path: str, db_name='wellbeing.db'):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Importing from {file_path}...")
    df = pd.read_excel(file_path)
    
    service = StudentService(db_name)
    
    count = 0
    for _, row in df.iterrows():
        try:
            service.create_student(
                student_id=str(row['student_id']),
                degree_id=int(row['degree_id']) if pd.notna(row['degree_id']) else None,
                degree_name=str(row['degree_name']) if pd.notna(row['degree_name']) else None,
                year=int(row['year']) if pd.notna(row['year']) else None,
                age_band=str(row['age_band']) if pd.notna(row['age_band']) else None,
                domicile=str(row['domicile']) if pd.notna(row['domicile']) else None,
                go_home_frequency=str(row['go_home_frequency']) if pd.notna(row['go_home_frequency']) else None,
                extracurricular_per_week=int(row['extracurricular_per_week']) if pd.notna(row['extracurricular_per_week']) else None,
                avg_commute_time_min=int(row['avg_commute_time_min']) if pd.notna(row['avg_commute_time_min']) else None,
                avg_screen_time_hours=int(row['avg_screen_time_hours']) if pd.notna(row['avg_screen_time_hours']) else None,
                commute_type=str(row['commute_type']) if pd.notna(row['commute_type']) else None,
                medical_information=str(row['medical_information']) if pd.notna(row['medical_information']) else None,
                disabilities=str(row['disabilities']) if pd.notna(row['disabilities']) else None,
            )
            count += 1
        except Exception as e:
            print(f"Error importing row {row.get('student_id', 'unknown')}: {e}")
            
    print(f"Successfully imported {count} students.")

if __name__ == "__main__":
    # Ensure DB is initialized
    # Note: This might drop tables if you changed the schema.sql to drop tables (which I did).
    # So running this resets the DB.
    init_db()
    seed_users()
    import_students_from_excel('app/database/PAI_dataset.xlsx')
