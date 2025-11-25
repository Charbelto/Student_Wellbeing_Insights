import pytest
import sqlite3
import os
from app.database.connection import get_db_connection, init_db

TEST_DB = 'test_wellbeing.db'

@pytest.fixture
def db():
    # Setup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Initialize DB
    conn = sqlite3.connect(TEST_DB)
    with open('app/database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()
    
    yield TEST_DB
    
    # Teardown
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_db_connection(db):
    conn = get_db_connection(db)
    assert conn is not None
    conn.close()

def test_tables_exist(db):
    conn = get_db_connection(db)
    cursor = conn.cursor()
    
    tables = ['attendance', 'wellbeing_surveys', 'submissions']
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        assert cursor.fetchone() is not None, f"Table {table} does not exist"
    
    conn.close()

