import pytest
from app.database.connection import get_db_connection


@pytest.fixture
def seeded_student(db_setup):
    conn = get_db_connection(db_setup)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students(student_id, degree_id, degree_name, year, age_band, domicile) VALUES(?,1,'CS',1,'18-21','UK')",
        ("WB1",),
    )
    cur.execute("INSERT INTO student_names(student_id, name) VALUES(?, ?)", ("WB1", "Well Student"))
    conn.commit()
    conn.close()
    return "WB1"


def test_submit_and_history(wellbeing_service, seeded_student):
    wellbeing_service.submit_survey(seeded_student, week=1, stress_level=3, hours_slept=7, mood_score=3)
    wellbeing_service.submit_survey(seeded_student, week=2, stress_level=4, hours_slept=6, mood_score=2)
    history = wellbeing_service.get_student_history(seeded_student)
    assert len(history) == 2
    assert history[0].week == 1
    assert history[1].stress_level == 4


def test_submit_validation_error(wellbeing_service, seeded_student):
    with pytest.raises(ValueError):
        wellbeing_service.submit_survey(seeded_student, week=1, stress_level=6, hours_slept=7, mood_score=3)
