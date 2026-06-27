import os
import json
from pathlib import Path

# Default DB path: ha/data/todo.sqlite relative to project root
HERE = Path(__file__).resolve().parent
DEFAULT_DB = HERE.parent / "data" / "todo.sqlite"

DB_PATH = Path(os.environ.get("TODO_DB_PATH", DEFAULT_DB)).resolve()

# Recommended PRAGMA defaults for SQLite
# WAL mode reduces contention for small household workloads; keep transactions short.
PRAGMAS = {
    "journal_mode": "WAL",
    "synchronous": "NORMAL",
    "foreign_keys": "ON",
    "temp_store": "MEMORY",
    "cache_size": -2000,
}

# Optional tuning knobs for production-style deployments.
DB_TIMEOUT_SECONDS = int(os.environ.get("TODO_DB_TIMEOUT_SECONDS", "5"))
WAL_AUTOCHECKPOINT = int(os.environ.get("TODO_WAL_AUTOCHECKPOINT", "1000"))


def load_config(path: str | None = None) -> dict:
    """Load optional JSON config for the pyscripts. Returns dict or {}."""
    p = Path(path) if path else HERE / "todo_config.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
