# data-model.md

## Overview

This document defines the SQLite schema for the Household Chore Tracker MVP. The schema is intentionally small and optimized for correctness and simplicity. The application stores task templates (`tasks`) and explicit persisted occurrences (`occurrences`) to make queries for "Due Today" fast and deterministic.

## Tables

### users

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `ha_user_id` TEXT NOT NULL UNIQUE
- `name` TEXT NOT NULL
- `display_name` TEXT

Purpose: store household member identities for assignment and history.

### tasks

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `title` TEXT NOT NULL
- `description` TEXT
- `assignee_id` INTEGER NULL REFERENCES users(id)
- `start_due_date` DATE NULL -- inclusive start of interval
- `end_due_date` DATE NULL -- inclusive end of interval
- `recurrence_rule` TEXT NULL -- RFC5545/JSON representation (implementation detail)
- `active` INTEGER NOT NULL DEFAULT 1
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` TIMESTAMP

Indexes: index on `assignee_id` to support filtering.

Purpose: canonical chore template data.

### occurrences

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `task_id` INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE
- `date` DATE NOT NULL
- `status` TEXT NOT NULL CHECK(status IN ('open','completed')) DEFAULT 'open'
- `completed_at` TIMESTAMP NULL

Constraints:
- `UNIQUE(task_id, date)` to guarantee deduplication per date.

Indexes: index on `date` to make Due Today queries efficient.

Purpose: persisted occurrences for a given date. For recurring tasks we may generate occurrences lazily or on demand; storing occurrences simplifies queries and history.

## Recurrence representation

For MVP the `recurrence_rule` field may contain either a simple JSON object documenting type and params (e.g., `{ "freq": "weekly", "byweekday": [1] }`) or a compact RFC-5545 `RRULE` string. Implementation code should provide a small compatibility layer to read and write the chosen format.

## Example SQL (SQLite)

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ha_user_id TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  display_name TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  assignee_id INTEGER,
  start_due_date DATE,
  end_due_date DATE,
  recurrence_rule TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY(assignee_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id);

CREATE TABLE IF NOT EXISTS occurrences (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  date DATE NOT NULL,
  status TEXT NOT NULL DEFAULT 'open',
  completed_at TIMESTAMP,
  FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  UNIQUE(task_id, date)
);

CREATE INDEX IF NOT EXISTS idx_occurrences_date ON occurrences(date);
```

## Migration strategy

On startup the pyscript code should run migrations (CREATE TABLE IF NOT EXISTS...). If future schema changes are required, include a simple migration/version table or store a `schema_version` integer in a `meta` table and perform in-code migrations.
