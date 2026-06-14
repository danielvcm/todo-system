"""SQLite helpers and migration runner for todo-system."""
from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import Optional

from .config import DB_PATH
from ._utils import with_db, safe_json_dumps


MIGRATIONS = []


def _migration_1():
    return (
        1,
        """
        BEGIN;
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ha_user_id TEXT UNIQUE NOT NULL,
            username TEXT,
            data TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            assignee_ha_user_id TEXT,
            due_date TEXT,
            start_due_date TEXT,
            end_due_date TEXT,
            recurrence_rule TEXT,
            meta TEXT
        );

        CREATE TABLE IF NOT EXISTS occurrences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            due_date TEXT NOT NULL,
            completed_at TEXT,
            data TEXT,
            UNIQUE(task_id, due_date),
            FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        -- set initial schema version
        INSERT OR REPLACE INTO meta(key, value) VALUES('schema_version', '1');
        COMMIT;
        """,
    )


MIGRATIONS.append(_migration_1())


def get_schema_version(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);")
    conn.commit()
    cur.execute("SELECT value FROM meta WHERE key='schema_version'")
    row = cur.fetchone()
    if not row:
        return 0
    try:
        return int(row[0])
    except Exception:
        return 0


def run_migrations(db_path: Optional[str | Path] = None) -> int:
    """Apply migrations and return the final schema version."""
    target = Path(db_path) if db_path else Path(DB_PATH)
    with with_db(target) as conn:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);")
        conn.commit()
        cur_version = get_schema_version(conn)
        for ver, sql in sorted(MIGRATIONS, key=lambda x: x[0]):
            if ver <= cur_version:
                continue
            cur.executescript(sql)
            conn.commit()
            cur_version = ver
    return cur_version


if __name__ == "__main__":
    v = run_migrations()
    print(f"migrations complete, schema_version={v}")
