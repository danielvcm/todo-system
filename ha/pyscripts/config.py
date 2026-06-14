import os
import json
from pathlib import Path

# Default DB path: ha/data/todo.sqlite relative to project root
HERE = Path(__file__).resolve().parent
DEFAULT_DB = HERE.parent / "data" / "todo.sqlite"

DB_PATH = Path(os.environ.get("TODO_DB_PATH", DEFAULT_DB)).resolve()

# Recommended PRAGMA defaults for SQLite
PRAGMAS = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
    "foreign_keys": "ON",
}


def load_config(path: str | None = None) -> dict:
    """Load optional JSON config for the pyscripts. Returns dict or {}."""
    p = Path(path) if path else HERE / "todo_config.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
