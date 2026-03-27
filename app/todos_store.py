"""
All SQL for todos lives here. Each function documents the intended ordering:

- Incomplete items first, newest-at-top within that group (`created_at` DESC).
- Completed items after that; newest-at-top (`completed_at` ASC).

Sorting is done in Python after one `SELECT *` so it's database-agnostic and
easier to maintain.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from app.db import get_connection


def _now_iso() -> str:
    """UTC timestamp string safe for SQLite TEXT comparisons and JSON."""
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row into a plain dict with a real Python bool."""
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
        "completed_at": row["completed_at"],
    }


def get_all_todos() -> list[dict]:
    """Return every todo in display order."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM todos").fetchall()

    incomplete = [r for r in rows if r["completed"] == 0]
    complete = [r for r in rows if r["completed"] == 1]

    # Newest active todos first.
    incomplete.sort(key=lambda r: r["created_at"], reverse=True)
    # Completed section.
    complete.sort(key=lambda r: r["completed_at"] or "")

    ordered = incomplete + complete
    return [_row_to_dict(r) for r in ordered]


def create_todo(title: str) -> dict:
    """Insert a new active todo and return it as a dict."""
    clean = title.strip()
    created_at = _now_iso()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO todos (title, completed, created_at, completed_at)
            VALUES (?, 0, ?, NULL)
            """,
            (clean, created_at),
        )
        conn.commit()
        new_id = cur.lastrowid

        row = conn.execute("SELECT * FROM todos WHERE id = ?", (new_id,)).fetchone()

    if row is None:
        raise RuntimeError("Insert succeeded but row could not be re-read")
    return _row_to_dict(row)


def update_todo_completed(todo_id: int, completed: bool) -> dict | None:
    """
    Set completion; set or clear `completed_at`. Returns None if id missing.
    """
    completed_at = _now_iso() if completed else None
    completed_int = 1 if completed else 0

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE todos
            SET completed = ?, completed_at = ?
            WHERE id = ?
            """,
            (completed_int, completed_at, todo_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()

    if row is None:
        return None
    return _row_to_dict(row)


def delete_todo(todo_id: int) -> bool:
    """Delete by id. Returns True if a row was removed."""
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        return cur.rowcount > 0
