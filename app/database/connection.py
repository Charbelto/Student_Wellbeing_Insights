import sqlite3
import os
from datetime import date, datetime

DEFAULT_DB = 'wellbeing.db'

def adapt_date(val):
    return val.isoformat()

def adapt_datetime(val):
    return val.isoformat()

def convert_date(val):
    return date.fromisoformat(val.decode())

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

# Register adapters
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATE", convert_date)
sqlite3.register_converter("TIMESTAMP", convert_datetime)

def get_db_connection(db_name=DEFAULT_DB):
    conn = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    # Enforce relational integrity across all connections
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_name=DEFAULT_DB):
    conn = get_db_connection(db_name)
    with open('app/database/schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()
