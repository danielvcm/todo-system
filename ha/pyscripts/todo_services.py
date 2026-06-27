"""Simple service dispatcher for todo-system pyscripts.

This module provides a minimal `handle_request(action, params, emit)` function
that callers (or a Home Assistant integration) can use to invoke actions and
receive responses via the `emit(event_type, payload)` callback.
"""
from typing import Any, Callable, Optional
from .todo_db import run_migrations
from .recurrence import expand
from ._utils import with_db, safe_json_loads
from datetime import datetime
import json
import logging

logger = logging.getLogger("todo_system")


EventEmitter = Callable[[str, dict], Any]


def initialize(db_path: str | None = None):
    """Initialize backend (run migrations)."""
    try:
        run_migrations(db_path)
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.exception("backend initialization failed", extra={"db_path": db_path})
        raise RuntimeError(f"backend initialization failed: {exc}") from exc


def list_due(date: str, db_path: Optional[str] = None) -> dict:
    """Return deduped list of occurrences and tasks applicable for `date`.

    Result format: {"date": date, "occurrences": [ ... ]}
    Each occurrence: {"occurrence_id": int|None, "task_id": int, "due_date": date, "completed_at": str|None, "task": {...}}
    """
    occurrences_out = []
    seen = set()
    with with_db(db_path) as conn:
        cur = conn.cursor()
        # persisted occurrences for date
        cur.execute(
            "SELECT id, task_id, due_date, completed_at, data FROM occurrences WHERE due_date = ?",
            (date,),
        )
        for row in cur.fetchall():
            occ_id, task_id, due_date, completed_at, data = row
            # fetch task
            cur.execute("SELECT id, title, description, assignee_ha_user_id, due_date, start_due_date, end_due_date, recurrence_rule, meta FROM tasks WHERE id = ?", (task_id,))
            trow = cur.fetchone()
            task = None
            if trow:
                task = {
                    "id": trow[0],
                    "title": trow[1],
                    "description": trow[2],
                    "assignee_ha_user_id": trow[3],
                    "due_date": trow[4],
                    "start_due_date": trow[5],
                    "end_due_date": trow[6],
                    "recurrence_rule": trow[7],
                    "meta": safe_json_loads(trow[8]) if trow[8] else None,
                }
            key = (task_id, due_date)
            if key in seen:
                continue
            seen.add(key)
            occurrences_out.append({
                "occurrence_id": occ_id,
                "task_id": task_id,
                "due_date": due_date,
                "completed_at": completed_at,
                "task": task,
            })

        # now scan tasks to find implicit occurrences
        cur.execute(
            "SELECT id, title, description, assignee_ha_user_id, due_date, start_due_date, end_due_date, recurrence_rule, meta FROM tasks"
        )
        for trow in cur.fetchall():
            task = {
                "id": trow[0],
                "title": trow[1],
                "description": trow[2],
                "assignee_ha_user_id": trow[3],
                "due_date": trow[4],
                "start_due_date": trow[5],
                "end_due_date": trow[6],
                "recurrence_rule": trow[7],
                "meta": safe_json_loads(trow[8]) if trow[8] else None,
            }

            # explicit single due_date
            if task.get("due_date") == date:
                key = (task["id"], date)
                if key not in seen:
                    seen.add(key)
                    occurrences_out.append({
                        "occurrence_id": None,
                        "task_id": task["id"],
                        "due_date": date,
                        "completed_at": None,
                        "task": task,
                    })
                continue

            # interval support: start_due_date <= date <= end_due_date
            if task.get("start_due_date") and task.get("end_due_date"):
                try:
                    from datetime import date as _date, datetime as _dt

                    start = _dt.fromisoformat(task["start_due_date"]).date()
                    end = _dt.fromisoformat(task["end_due_date"]).date()
                    target = _dt.fromisoformat(date).date()
                    if start <= target <= end:
                        key = (task["id"], date)
                        if key not in seen:
                            seen.add(key)
                            occurrences_out.append({
                                "occurrence_id": None,
                                "task_id": task["id"],
                                "due_date": date,
                                "completed_at": None,
                                "task": task,
                            })
                        continue
                except Exception:
                    pass

            # recurrence rules
            if task.get("recurrence_rule"):
                try:
                    expanded = expand(task, date)
                    if expanded:
                        key = (task["id"], date)
                        if key not in seen:
                            seen.add(key)
                            occurrences_out.append({
                                "occurrence_id": None,
                                "task_id": task["id"],
                                "due_date": date,
                                "completed_at": None,
                                "task": task,
                            })
                except Exception:
                    pass

    return {"date": date, "occurrences": occurrences_out}


def _validate_dates(task: dict) -> None:
    from datetime import datetime

    for key in ("due_date", "start_due_date", "end_due_date"):
        if task.get(key):
            # will raise ValueError if invalid
            datetime.fromisoformat(task[key])


def create_task(task: dict, db_path: Optional[str] = None) -> dict:
    """Insert a new task with basic validation and return created record."""
    if not task.get("title"):
        raise ValueError("title is required")
    # validate dates
    _validate_dates(task)
    # validate start <= end when both provided
    if task.get("start_due_date") and task.get("end_due_date"):
        from datetime import datetime as _dt

        s = _dt.fromisoformat(task["start_due_date"]).date()
        e = _dt.fromisoformat(task["end_due_date"]).date()
        if s > e:
            raise ValueError("start_due_date must be <= end_due_date")
    # validate recurrence_rule is JSON if present
    if task.get("recurrence_rule"):
        try:
            json.loads(task["recurrence_rule"])
        except Exception:
            raise ValueError("invalid recurrence_rule: must be JSON")

    with with_db(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks(title, description, assignee_ha_user_id, due_date, start_due_date, end_due_date, recurrence_rule, meta) VALUES(?,?,?,?,?,?,?,?)",
            (
                task.get("title"),
                task.get("description"),
                task.get("assignee_ha_user_id"),
                task.get("due_date"),
                task.get("start_due_date"),
                task.get("end_due_date"),
                task.get("recurrence_rule"),
                json.dumps(task.get("meta")) if task.get("meta") is not None else None,
            ),
        )
        conn.commit()
        task_id = cur.lastrowid
    return {"created_id": task_id, "task": {**task, "id": task_id}}


def update_task(task_id: int, fields: dict, db_path: Optional[str] = None) -> dict:
    if not task_id:
        raise ValueError("task_id required")
    # validate dates if present
    _validate_dates(fields)
    # if both start and end included in fields, validate ordering
    if fields.get("start_due_date") and fields.get("end_due_date"):
        from datetime import datetime as _dt

        s = _dt.fromisoformat(fields["start_due_date"]).date()
        e = _dt.fromisoformat(fields["end_due_date"]).date()
        if s > e:
            raise ValueError("start_due_date must be <= end_due_date")

    if fields.get("recurrence_rule"):
        try:
            json.loads(fields["recurrence_rule"])
        except Exception:
            raise ValueError("invalid recurrence_rule: must be JSON")

    cols = []
    vals = []
    for k, v in fields.items():
        cols.append(f"{k} = ?")
        if k == "meta":
            vals.append(json.dumps(v) if v is not None else None)
        else:
            vals.append(v)
    vals.append(task_id)
    sql = f"UPDATE tasks SET {', '.join(cols)} WHERE id = ?"
    with with_db(db_path) as conn:
        cur = conn.cursor()
        cur.execute(sql, tuple(vals))
        conn.commit()
    return {"updated_id": task_id, "fields": fields}


def delete_task(task_id: int, db_path: Optional[str] = None) -> dict:
    if not task_id:
        raise ValueError("task_id required")
    with with_db(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return {"deleted_id": task_id}


def complete_occurrence(task_id: int, due_date: str, db_path: Optional[str] = None) -> dict:
    """Mark an occurrence completed; create if missing. Return updated occurrence."""
    if not task_id:
        raise ValueError("task_id required")
    if not due_date:
        raise ValueError("due_date required")

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()

    with with_db(db_path) as conn:
        cur = conn.cursor()
        # check if occurrence exists
        cur.execute(
            "SELECT id, completed_at FROM occurrences WHERE task_id = ? AND due_date = ?",
            (task_id, due_date),
        )
        row = cur.fetchone()

        if row:
            occ_id = row[0]
            # update existing
            cur.execute(
                "UPDATE occurrences SET completed_at = ? WHERE id = ?",
                (now, occ_id),
            )
        else:
            # create new
            cur.execute(
                "INSERT INTO occurrences(task_id, due_date, completed_at) VALUES(?,?,?)",
                (task_id, due_date, now),
            )
            occ_id = cur.lastrowid

        conn.commit()

        # fetch and return
        cur.execute(
            "SELECT id, task_id, due_date, completed_at FROM occurrences WHERE id = ?",
            (occ_id,),
        )
        occ = cur.fetchone()
        return {
            "completed": {
                "occurrence_id": occ[0],
                "task_id": occ[1],
                "due_date": occ[2],
                "completed_at": occ[3],
            }
        }


def get_task_history(
    task_id: int, limit: int = 50, offset: int = 0, db_path: Optional[str] = None
) -> dict:
    """Return paginated completed occurrences for a task."""
    if not task_id:
        raise ValueError("task_id required")
    if limit <= 0:
        limit = 50

    with with_db(db_path) as conn:
        cur = conn.cursor()
        # fetch completed occurrences
        cur.execute(
            "SELECT id, task_id, due_date, completed_at FROM occurrences WHERE task_id = ? AND completed_at IS NOT NULL ORDER BY due_date DESC LIMIT ? OFFSET ?",
            (task_id, limit, offset),
        )
        rows = cur.fetchall()
        occurrences = [
            {
                "occurrence_id": r[0],
                "task_id": r[1],
                "due_date": r[2],
                "completed_at": r[3],
            }
            for r in rows
        ]
        # also get total count
        cur.execute(
            "SELECT COUNT(*) FROM occurrences WHERE task_id = ? AND completed_at IS NOT NULL",
            (task_id,),
        )
        total = cur.fetchone()[0]

    return {"task_id": task_id, "total": total, "limit": limit, "offset": offset, "occurrences": occurrences}


def list_users(db_path: Optional[str] = None) -> dict:
    """Return all users from the users table."""
    with with_db(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, ha_user_id, username, data FROM users ORDER BY username")
        rows = cur.fetchall()
        users = [
            {
                "id": r[0],
                "ha_user_id": r[1],
                "username": r[2],
                "data": safe_json_loads(r[3]) if r[3] else None,
            }
            for r in rows
        ]
    return {"users": users}


def sync_users_from_ha(ha_users: list, db_path: Optional[str] = None) -> dict:
    """Sync users from HA into the users table.

    ha_users: list of {"user_id": str, "username": str} dicts (simulates HA user context).
    Returns count of upserted users.
    """
    if not isinstance(ha_users, list):
        raise ValueError("ha_users must be a list")

    count = 0
    with with_db(db_path) as conn:
        cur = conn.cursor()
        for u in ha_users:
            ha_id = u.get("user_id")
            username = u.get("username")
            if not ha_id or not username:
                continue
            # upsert: if exists, update; else insert
            cur.execute(
                "SELECT id FROM users WHERE ha_user_id = ?", (ha_id,)
            )
            if cur.fetchone():
                cur.execute(
                    "UPDATE users SET username = ? WHERE ha_user_id = ?",
                    (username, ha_id),
                )
            else:
                cur.execute(
                    "INSERT INTO users(ha_user_id, username) VALUES(?,?)",
                    (ha_id, username),
                )
            count += 1
        conn.commit()
    return {"synced": count}


def create_user(ha_user_id: str, username: str, db_path: Optional[str] = None) -> dict:
    """Create a user explicitly (admin convenience). Normally sync from HA instead."""
    if not ha_user_id or not username:
        raise ValueError("ha_user_id and username required")
    with with_db(db_path) as conn:
        cur = conn.cursor()
        # check for duplicates
        cur.execute(
            "SELECT id FROM users WHERE ha_user_id = ?", (ha_user_id,)
        )
        if cur.fetchone():
            raise ValueError(f"User with ha_user_id {ha_user_id} already exists")
        cur.execute(
            "INSERT INTO users(ha_user_id, username) VALUES(?,?)",
            (ha_user_id, username),
        )
        conn.commit()
        user_id = cur.lastrowid
    return {"created_id": user_id, "ha_user_id": ha_user_id, "username": username}


def get_user_by_ha_id(ha_user_id: str, db_path: Optional[str] = None) -> Optional[dict]:
    """Look up a user by HA user_id. Returns user dict or None."""
    with with_db(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, ha_user_id, username, data FROM users WHERE ha_user_id = ?",
            (ha_user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "ha_user_id": row[1],
            "username": row[2],
            "data": safe_json_loads(row[3]) if row[3] else None,
        }


def handle_request(action: str, params: dict, emit: EventEmitter | None = None, calling_user_id: Optional[str] = None):
    """Dispatch action and optionally emit events.

    calling_user_id: optional HA user_id for permission context.
    Supported actions: list_due, create_task, update_task, delete_task, complete_occurrence,
                       get_task_history, list_users, sync_users_from_ha, create_user.
    """
    logger.info(
        "dispatching todo request",
        extra={"action": action, "calling_user_id": calling_user_id, "params": params},
    )

    try:
        if action == "list_due":
            date = params.get("date")
            payload = list_due(date, params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        if action == "create_task":
            task = params.get("task") or {}
            payload = create_task(task, params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        if action == "update_task":
            task_id = params.get("task_id")
            fields = params.get("fields") or {}
            payload = update_task(task_id, fields, params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        if action == "delete_task":
            task_id = params.get("task_id")
            payload = delete_task(task_id, params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        if action == "complete_occurrence":
            task_id = params.get("task_id")
            due_date = params.get("due_date")
            payload = complete_occurrence(task_id, due_date, params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        if action == "get_task_history":
            task_id = params.get("task_id")
            limit = int(params.get("limit", 50))
            offset = int(params.get("offset", 0))
            payload = get_task_history(task_id, limit, offset, params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        if action == "list_users":
            payload = list_users(params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        if action == "sync_users_from_ha":
            ha_users = params.get("ha_users", [])
            payload = sync_users_from_ha(ha_users, params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        if action == "create_user":
            ha_user_id = params.get("ha_user_id")
            username = params.get("username")
            payload = create_user(ha_user_id, username, params.get("db_path"))
            if emit:
                emit("todo_response", payload)
            return payload

        raise ValueError(f"Unknown action: {action}")
    except Exception as exc:
        logger.exception("todo request failed", extra={"action": action, "params": params})
        raise RuntimeError(f"todo request failed for {action}: {exc}") from exc
