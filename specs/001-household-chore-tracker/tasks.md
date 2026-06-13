
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

- [ ] T021 Implement `list_users` action and `users` table helpers that map application users 1:1 to Home Assistant users (use HA `user_id`/username). Seed and synchronize the `users` table from existing HA users on startup; do not treat app users as separate accounts.
- [ ] T022 Implement `create_user` only as an explicit admin convenience (if required) and document behavior; prefer syncing from HA. Ensure service handlers associate actions with the calling HA user (use HA auth context) and enforce expected permission checks.
- [ ] T023 Add tests `tests/unit/test_users.py` for user synchronization, assignment lookups, and permission/identity enforcement (simulate HA user context where possible)

## Phase 6: Frontend (React) - Skeleton to MVP

- [ ] T024 Initialize frontend project: `frontend/` with Vite + React 18, TypeScript, ESLint, Prettier, and Vitest. Add `package.json` scripts: `dev`, `build`, `test`, `lint`.
- [ ] T025 Create frontend folder layout: `src/components/`, `src/pages/`, `src/services/`, `src/hooks/`, `src/styles/`, `src/i18n/` and `public/` for static assets.
- [ ] T026 Implement `frontend/src/services/haConnector.ts`: wrapper to call Home Assistant services with correlation UUID and subscribe to `todo_response` events. Provide `request(action, params): Promise`.
- [ ] T027 Build `DueToday` page scaffold (`src/pages/DueToday`) with header, date picker, and list placeholder; wire routing so panel loads at `/local/todo-system/index.html` within HA panel.
- [ ] T028 Implement `OccurrenceRow` component (`src/components/OccurrenceRow`) showing title, assignee badge, due info (date/interval), recurrence indicator, and completion control. Make controls keyboard-focusable and aria-labeled.
- [ ] T029 Implement `DueList` component that fetches `list_due` via `haConnector.request` and renders `OccurrenceRow` items with loading/empty states and error handling.
- [ ] T030 Implement `CreateTask` page/form (`src/pages/CreateTask`): title, description, assignee selector (populated from HA), due date OR start/end interval, recurrence presets and advanced editor, client-side validation, and submit via `create_task`.
- [ ] T031 Implement `TaskDetail` modal/panel for editing a task (reuses CreateTask fields) with `update_task` and `delete_task` actions and confirmation flows.
- [ ] T032 Styling & theme integration: create `src/styles/ha-theme.css` that references Home Assistant CSS variables and design tokens (e.g., `--ha-card-background`, `--mdc-theme-primary`). Ensure components use HA spacing, typography, and card-like containers.
- [ ] T033 Accessibility & i18n: add keyboard navigation, ARIA attributes, and i18n scaffolding (`src/i18n/`) with English strings; write basic i18n tests.
- [ ] T034 Tests: add Vitest + React Testing Library tests for `OccurrenceRow`, `DueList`, and `CreateTask`. Add mocks for `haConnector` and snapshot tests.
- [ ] T035 Storybook (optional): scaffold `frontend/.storybook/` and add component stories for visual testing and design review.


## Phase 7: Integration, E2E & CI

- [ ] T036 Add `tests/e2e/` skeleton for Playwright tests and at least one E2E scenario that verifies the Due Today flow end-to-end inside HA (document HA setup steps for E2E)
- [ ] T037 Add GitHub Actions workflow `ci.yaml` to run Python unit tests, frontend unit tests, and lint checks on push/PR
- [ ] T038 Add local integration script `scripts/deploy_to_ha.sh` for dev: build frontend, copy `dist/` to HA `/config/www/todo-system/`, copy `ha/pyscripts/*.py` to `/config/pyscripts/` (provide scp/rsync examples)


## Phase 8: Packaging, Docs & Quickstart

- [ ] T039 Document `panel_custom` config snippet and deployment steps in `specs/001-household-chore-tracker/quickstart.md`
- [ ] T040 Add `docs/deployment.md` with backup and DB migration guidance (include `schema_version` strategy)
- [ ] T041 Add `docs/security.md` with HA-specific notes about user roles and restricting access to the panel

## Phase 9: Polish & Cross-Cutting Concerns

- [ ] T042 [P] Add PRAGMA and WAL tuning notes to `ha/pyscripts/config.py` and `data-model.md`
- [ ] T043 Add structured logging and error handling across Pyscript modules
- [ ] T044 Add acceptance test scripts and sample test data under `tests/fixtures/`
- [ ] T045 Finalize MVP scope and create release checklist in `docs/release.md`

---

Dependencies & ordering notes:

- Backend foundation (T005–T009) must exist before most backend feature tasks (T010–T020).
- Frontend (T024–T028) can be scaffolded in parallel with backend work; integration requires T029 and T031.
- CI (T030) depends on having unit tests present for each layer.

Parallel opportunities:

- [P] `recurrence.py`, `todo_db.py`, and `_utils.py` development can be parallelized by different contributors.
- [P] Frontend scaffolding and backend migration work can proceed concurrently.

Suggested MVP scope: deliver T001–T012, T018, T024–T034, T037, T039 for a working Due Today experience with completion support and an HA-styled frontend.

Total tasks: 45 (T001–T045)

