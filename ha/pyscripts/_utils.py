import sqlite3
import json
import os
import fcntl
from contextlib import contextmanager
from pathlib import Path
from .config import DB_PATH, PRAGMAS


class FileLock:
    """Simple POSIX file lock using fcntl."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.fd = None

    def acquire(self):
        self.fd = open(self.path, "w+")
        fcntl.flock(self.fd, fcntl.LOCK_EX)

    def release(self):
        if self.fd:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
            finally:
                self.fd.close()
                self.fd = None

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()


def safe_json_dumps(obj) -> str:
    return json.dumps(obj, default=str, ensure_ascii=False)


def safe_json_loads(s: str):
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s


@contextmanager
def with_db(path: str | os.PathLike | None = None):
    """Context manager yielding a sqlite3.Connection with PRAGMAs applied."""
    db_path = Path(path) if path else Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
    try:
        cur = conn.cursor()
        # Apply pragmas
        for k, v in PRAGMAS.items():
            cur.execute(f"PRAGMA {k}={v}")
        conn.commit()
        yield conn
    finally:
        conn.close()
