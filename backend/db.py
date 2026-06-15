import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parents[1] / "mood_detector.db"

def get_connection():
    conn = sqlite3.connect(str(DATABASE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
