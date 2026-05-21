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
            allowed INTEGER NOT NULL DEFAULT 0,
            weak_points TEXT NOT NULL DEFAULT '[]',
            recent_topics TEXT NOT NULL DEFAULT '[]'
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS pending_requests (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )"""
    )
    try:
        conn.execute("ALTER TABLE users ADD COLUMN model TEXT NOT NULL DEFAULT 'groq'")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN allowed INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN mode TEXT NOT NULL DEFAULT 'chat'")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN dialog TEXT NOT NULL DEFAULT '[]'")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN topik_topic TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN topik_question TEXT")
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
            row_dict = dict(row)
            result = {
                "level": row_dict["level"],
                "model": row_dict["model"],
                "mode": row_dict.get("mode", "chat"),
                "allowed": bool(row_dict.get("allowed", 0)),
                "weak_points": json.loads(row_dict["weak_points"]),
                "recent_topics": json.loads(row_dict["recent_topics"]),
            }
        else:
            result = {
                "level": "beginner",
                "model": "groq",
                "mode": "chat",
                "allowed": False,
                "weak_points": [],
                "recent_topics": [],
            }
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
            if key in ("weak_points", "recent_topics", "dialog"):
                val = json.dumps(val) if not isinstance(val, str) else val
            fields.append(f"{key} = ?")
            values.append(val)
        values.append(user_id)
        conn.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?", values
        )
        conn.commit()
        conn.close()


def is_user_allowed(user_id: int) -> bool:
    with _lock:
        conn = _get_conn()
        row = conn.execute("SELECT allowed FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            result = bool(row["allowed"])
        else:
            conn.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            result = False
        conn.commit()
        conn.close()
        return result


def approve_user(user_id: int):
    with _lock:
        conn = _get_conn()
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        conn.execute("UPDATE users SET allowed = 1 WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM pending_requests WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


def reject_user(user_id: int):
    with _lock:
        conn = _get_conn()
        conn.execute("DELETE FROM pending_requests WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


def add_pending_request(user_id: int, username: str, full_name: str):
    with _lock:
        conn = _get_conn()
        conn.execute(
            "INSERT OR IGNORE INTO pending_requests (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name),
        )
        conn.commit()
        conn.close()


def get_pending_requests() -> list[dict]:
    with _lock:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT user_id, username, full_name, created_at FROM pending_requests ORDER BY created_at ASC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_level(user_id: int) -> str:
    return get_user(user_id)["level"]


def set_level(user_id: int, level: str):
    update_user(user_id, level=level)


def get_model(user_id: int) -> str:
    return get_user(user_id).get("model", "groq")


def set_model(user_id: int, model: str):
    update_user(user_id, model=model)


def get_mode(user_id: int) -> str:
    return get_user(user_id).get("mode", "chat")


def set_mode(user_id: int, mode: str):
    update_user(user_id, mode=mode)


DIALOG_KEY = "dialog"


def get_dialog(user_id: int) -> list:
    return json.loads(get_user(user_id).get(DIALOG_KEY, "[]"))


def set_dialog(user_id: int, messages: list):
    update_user(user_id, **{DIALOG_KEY: json.dumps(messages)})


def clear_dialog(user_id: int):
    update_user(user_id, **{DIALOG_KEY: "[]"})
