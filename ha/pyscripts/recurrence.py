"""Minimal recurrence parsing and expansion utilities."""
from datetime import datetime, timedelta
import json
from typing import List


def parse_recurrence(recurrence_json: str | None):
    """Parse a simple JSON recurrence rule.

    Supported form: {"interval_days": 7}
    Returns dict or None.
    """
    if not recurrence_json:
        return None
    try:
        return json.loads(recurrence_json)
    except Exception:
        return None


def expand(task: dict, date: str) -> List[dict]:
    """Return occurrences for the given ISO date string.

    This is intentionally minimal: supports a single `interval_days` rule
    or a fixed `due_date`.
    """
    out = []
    target = datetime.fromisoformat(date).date()

    # explicit occurrence stored on task
    if task.get("due_date"):
        try:
            d = datetime.fromisoformat(task["due_date"]).date()
            if d == target:
                out.append({"task_id": task.get("id"), "due_date": date})
            return out
        except Exception:
            pass

    rule = parse_recurrence(task.get("recurrence_rule"))
    if not rule:
        return out

    interval = int(rule.get("interval_days", 0))
    if interval <= 0:
        return out

    # If task has a start_due_date, check if target falls on the interval
    try:
        start = task.get("start_due_date")
        if not start:
            return out
        start_date = datetime.fromisoformat(start).date()
        days = (target - start_date).days
        if days >= 0 and days % interval == 0:
            out.append({"task_id": task.get("id"), "due_date": date})
    except Exception:
        return out

    return out
