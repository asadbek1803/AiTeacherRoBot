import sqlite3
import json
import os
from threading import Lock

DB_FILE = "user_memory.db"
_lock = Lock()


def _get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            level TEXT NOT NULL DEFAULT 'beginner',
            model TEXT NOT NULL DEFAULT 'groq',
            weak_points TEXT NOT NULL DEFAULT '[]',
            recent_topics TEXT NOT NULL DEFAULT '[]'
        )"""
    )
    try:
        conn.execute("ALTER TABLE users ADD COLUMN model TEXT NOT NULL DEFAULT 'groq'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    return conn


def get_user(user_id: int) -> dict:
    with _lock:
        conn = _get_conn()
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row:
            result = {
                "level": row["level"],
                "model": row["model"],
                "weak_points": json.loads(row["weak_points"]),
                "recent_topics": json.loads(row["recent_topics"]),
            }
        else:
            result = {"level": "beginner", "model": "groq", "weak_points": [], "recent_topics": []}
            conn.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return result


def update_user(user_id: int, **kwargs):
    with _lock:
        conn = _get_conn()
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        fields = []
        values = []
        for key, val in kwargs.items():
            if key in ("weak_points", "recent_topics"):
                val = json.dumps(val)
            fields.append(f"{key} = ?")
            values.append(val)
        values.append(user_id)
        conn.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?", values
        )
        conn.commit()
        conn.close()


def get_level(user_id: int) -> str:
    return get_user(user_id)["level"]


def set_level(user_id: int, level: str):
    update_user(user_id, level=level)


def get_model(user_id: int) -> str:
    return get_user(user_id).get("model", "groq")


def set_model(user_id: int, model: str):
    update_user(user_id, model=model)
