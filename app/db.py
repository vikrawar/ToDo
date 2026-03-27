"""
SQLite connection helpers.

We use the standard library module `sqlite3`. The database file
lives under `data/todos.db` relative to the project root so it stays separate
from source code.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

# `__file__` is this file's path. `.parent` is the `app/` folder; one more
# `.parent` is the project root (the directory that contains `app/`).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = _PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "todos.db"


def get_connection() -> sqlite3.Connection:
    """
    Open a new connection to the SQLite file, creating the `data/` folder if
    needed.

    `row_factory = sqlite3.Row` lets us access columns by name (`row["title"]`)
    instead of by numeric index.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enforce foreign keys if we add relations later; harmless today.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema() -> None:
    """
    Create the `todos` table if it does not exist yet.

    SQLite uses INTEGER 0/1 for booleans. We store timestamps as ISO-8601
    strings so they sort correctly as plain text and are readable in tools.
    """
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )
        conn.commit()
