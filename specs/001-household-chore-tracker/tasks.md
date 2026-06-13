
# tasks.md

## Phase 1: Setup & Project Scaffolding

- [ ] T001 Create repository scaffolding: `frontend/`, `ha/pyscripts/`, `ha/www/todo-system/`, `tests/`, `docs/`
- [ ] T002 [P] Add developer notes `specs/001-household-chore-tracker/quickstart.md` with HA access, Pyscript, and DB path recommendations
- [ ] T003 Add `README.md` stub describing development workflow and deploy steps
- [ ] T004 Create `ha/pyscripts/config.py` with constants: `DB_PATH`, PRAGMA defaults, and minimal config loader

## Phase 2: Backend Foundations (Pyscript)

- [ ] T005 Create `ha/pyscripts/todo_db.py` with DB connection helpers and migration runner (creates `users`, `tasks`, `occurrences`, `meta`)
- [ ] T006 [P] Create `ha/pyscripts/_utils.py` with `with_db()` context manager, small file-lock helper, and JSON helper for recurrence rules
- [ ] T007 Create `ha/pyscripts/recurrence.py` with parsing and simple expansion utilities (JSON and/or RRULE minimal support)
- [ ] T008 Create `ha/pyscripts/todo_services.py` that registers the `todo_system.request` service and dispatches actions; emits `todo_response` events
- [ ] T009 Implement DB schema migration and `schema_version` meta table in `todo_db.py`

## Phase 3: Backend Core Features (stories)

### US1 - Due Today (P1)

- [ ] T010 [US1] Implement `list_due(date)` service action: returns deduped list of occurrences and tasks applicable for `date`
- [ ] T011 [US1] Implement occurrence generation logic: check persisted `occurrences`, include tasks with intervals, consult `recurrence.expand(task, date)` for recurring occurrences
- [ ] T012 [US1] Add unit tests `tests/unit/test_list_due.py` covering single-date, interval, and recurrence cases

### US2 - Create Recurring Task (P1)

- [ ] T013 [US2] Implement `create_task` action to insert into `tasks` with validation for dates and recurrence_rule
- [ ] T014 [US2] Implement `update_task` and `delete_task` actions (delete cascades occurrences)
- [ ] T015 [US2] Add unit tests `tests/unit/test_recurrence.py` validating parsing and example expansions

### US3 - Flexible Due Interval (P2)

- [ ] T016 [US3] Ensure `create_task` supports `start_due_date` and `end_due_date` and that `list_due` includes tasks for all dates in range
- [ ] T017 [US3] Add unit tests `tests/unit/test_intervals.py` for interval behavior

## Phase 4: Occurrence Completion & History

- [ ] T018 Implement `complete_occurrence` action: mark occurrence completed (create occurrence if missing), set `completed_at`, return updated occurrence
- [ ] T019 [P] Add history-query action `get_task_history(task_id, limit, offset)` returning past occurrences
- [ ] T020 Add unit tests `tests/unit/test_complete_occurrence.py` verifying completion and history

## Phase 5: Users, Assignment & Permissions

- [ ] T021 Implement `list_users` and `create_user` service actions and add `users` table helpers
- [ ] T022 Ensure service handlers enforce basic HA user checks where appropriate (document expected behavior)
- [ ] T023 Add tests `tests/unit/test_users.py` for user management

## Phase 6: Frontend (React) - Skeleton to MVP

- [ ] T024 Scaffold `frontend/` React app with Vite + React 18; basic routing and `Due Today` page
- [ ] T025 Implement `hass` connector in frontend to call `todo_system.request` service and listen for `todo_response` events
- [ ] T026 Implement `DueToday` component that calls `list_due` on mount and renders occurrences
- [ ] T027 Implement `CreateTask` form supporting title, description, assignee, due date/interval, recurrence rule
- [ ] T028 Add frontend unit tests (Vitest) for core components

## Phase 7: Integration, E2E & CI

- [ ] T029 Add `tests/e2e/` skeleton for Playwright tests (optional) and at least one E2E scenario for Due Today
- [ ] T030 Add GitHub Actions workflow `ci.yaml` to run Python unit tests and frontend unit tests on push/PR
- [ ] T031 Add local integration script `scripts/deploy_to_ha.sh` for dev: build frontend, scp `dist/` to HA `/config/www/todo-system/`, copy `ha/pyscripts/*.py` to `/config/pyscripts/`

## Phase 8: Packaging, Docs & Quickstart

- [ ] T032 Document `panel_custom` config snippet and deployment steps in `specs/001-household-chore-tracker/quickstart.md`
- [ ] T033 Add `docs/deployment.md` with backup and DB migration guidance (include `schema_version` strategy)
- [ ] T034 Add `docs/security.md` with HA-specific notes about user roles and restricting access to the panel

## Phase 9: Polish & Cross-Cutting Concerns

- [ ] T035 [P] Add PRAGMA and WAL tuning notes to `ha/pyscripts/config.py` and `data-model.md`
- [ ] T036 Add structured logging and error handling across Pyscript modules
- [ ] T037 Add acceptance test scripts and sample test data under `tests/fixtures/`
- [ ] T038 Finalize MVP scope and create release checklist in `docs/release.md`

---

Dependencies & ordering notes:

- Backend foundation (T005–T009) must exist before most backend feature tasks (T010–T020).
- Frontend (T024–T028) can be scaffolded in parallel with backend work; integration requires T029 and T031.
- CI (T030) depends on having unit tests present for each layer.

Parallel opportunities:

- [P] `recurrence.py`, `todo_db.py`, and `_utils.py` development can be parallelized by different contributors.
- [P] Frontend scaffolding and backend migration work can proceed concurrently.

Suggested MVP scope: deliver T001–T012, T018, T024–T026, T031, T032 for a working Due Today experience with completion support.

Total tasks: 38 (T001–T038)

