from typing import Optional
from app.database.models import User, Role
from app.database.connection import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    def __init__(self, db_name='wellbeing.db'):
        self.db_name = db_name

    def create_user(self, username: str, password: str, role: Role) -> User:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        
        password_hash = generate_password_hash(password)
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role.value)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            role=role
        )

    def verify_password(self, username: str, password: str) -> bool:
        user = self.get_user_by_username(username)
        if not user:
            return False
        return check_password_hash(user.password_hash, password)

    def get_user_by_username(self, username: str) -> Optional[User]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                role=Role(row['role'])
            )
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        conn = get_db_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                role=Role(row['role'])
            )
        return None

