import os
from app.database.connection import get_db_connection, init_db

def test_init_db_creates_tables(tmp_path):
    db_path = tmp_path / "init_test.db"
    init_db(str(db_path))
    conn = get_db_connection(str(db_path))
    cur = conn.cursor()
    for table in ["students", "attendance", "survey", "submissions", "risk_indicator"]:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        assert cur.fetchone() is not None, f"missing table {table}"
    conn.close()
