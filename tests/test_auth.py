import pytest
from app.services.user_service import UserService
from app.database.models import User, Role

def test_create_user(user_service):
    user = user_service.create_user("officer", "securepass", Role.WELLBEING_OFFICER)
    assert user.username == "officer"
    assert user.role == Role.WELLBEING_OFFICER
    assert user.password_hash != "securepass" # Should be hashed

def test_verify_password(user_service):
    user = user_service.create_user("tutor", "pass123", Role.TUTOR)
    assert user_service.verify_password("tutor", "pass123") is True
    assert user_service.verify_password("tutor", "wrong") is False

def test_get_user(user_service):
    created = user_service.create_user("leader", "pass", Role.MODULE_LEADER)
    retrieved = user_service.get_user_by_id(created.id)
    assert retrieved.username == "leader"

