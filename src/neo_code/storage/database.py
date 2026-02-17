"""SQLite database for persistent storage."""

import sqlite3
import json
from pathlib import Path

from neo_code.core.models import StudentProfile


_DB_DIR = Path.home() / ".neo_code"
_DB_PATH = _DB_DIR / "neo_code.db"


def _ensure_db_dir() -> None:
    _DB_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection, creating the database if needed."""
    _ensure_db_dir()
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT DEFAULT '',
            current_phase INTEGER DEFAULT 1,
            current_lesson INTEGER DEFAULT 1,
            skill_level INTEGER DEFAULT 1,
            exercises_completed TEXT DEFAULT '[]',
            common_error_patterns TEXT DEFAULT '{}',
            total_code_runs INTEGER DEFAULT 0,
            total_errors_fixed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            file_path TEXT,
            code_content TEXT,
            phase INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );
    """)
    conn.commit()


def save_profile(profile: StudentProfile) -> None:
    """Save student profile to database."""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO students
            (student_id, name, current_phase, current_lesson, skill_level,
             exercises_completed, common_error_patterns, total_code_runs,
             total_errors_fixed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            profile.student_id,
            profile.name,
            profile.current_phase,
            profile.current_lesson,
            profile.skill_level,
            json.dumps(profile.exercises_completed),
            json.dumps(profile.common_error_patterns),
            profile.total_code_runs,
            profile.total_errors_fixed,
        ))
        conn.commit()
    finally:
        conn.close()


def load_profile(student_id: str) -> StudentProfile | None:
    """Load student profile from database."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        if row is None:
            return None
        return StudentProfile(
            student_id=row["student_id"],
            name=row["name"],
            current_phase=row["current_phase"],
            current_lesson=row["current_lesson"],
            skill_level=row["skill_level"],
            exercises_completed=json.loads(row["exercises_completed"]),
            common_error_patterns=json.loads(row["common_error_patterns"]),
            total_code_runs=row["total_code_runs"],
            total_errors_fixed=row["total_errors_fixed"],
        )
    finally:
        conn.close()


def save_session(student_id: str, file_path: str, code: str, phase: int) -> None:
    """Save a coding session."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO sessions (student_id, file_path, code_content, phase) VALUES (?, ?, ?, ?)",
            (student_id, file_path, code, phase),
        )
        conn.commit()
    finally:
        conn.close()
