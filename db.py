"""Database functions"""
import sqlite3

conn = sqlite3.connect("db.sqlite3")
conn.row_factory = sqlite3.Row


def create_table():
    """Create questions table"""
    conn.execute(
        """CREATE TABLE IF NOT EXISTS questions (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    bundesland TEXT,
    question_png_bytes BYTES,
    answer0 TEXT,
    answer1 TEXT,
    answer2 TEXT,
    answer3 TEXT,
    correct_answer_index INTEGER
    )"""
    )
