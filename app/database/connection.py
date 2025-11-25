import sqlite3
import os

DEFAULT_DB = 'wellbeing.db'

def get_db_connection(db_name=DEFAULT_DB):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_name=DEFAULT_DB):
    conn = get_db_connection(db_name)
    with open('app/database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()
