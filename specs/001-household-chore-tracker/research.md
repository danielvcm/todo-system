# research.md

## Decision

Backend: implement all server-side logic as Pyscript scripts installed via HACS Pyscript on the user's Home Assistant OS instance. Expose a small set of Home Assistant services (domain: `todo_system`) that accept requests and emit response events (`todo_response`) that the frontend can subscribe to.

Frontend: React 18 single-page application built locally. Built static assets are copied to the Home Assistant `www/` directory and registered as a custom panel (`panel_custom`) in `configuration.yaml`.

Storage: SQLite single-file database stored under the HA config directory (recommended: `/config/todo_system/todo.db`) using WAL journaling. Use the standard-library `sqlite3` module to avoid third-party dependency installation within HA.

Rationale: This architecture satisfies the user's constraint of no additional servers — everything runs inside Home Assistant. Pyscript allows Python code execution inside HA, and a static frontend served from HA integrates seamlessly with the HA session and websocket APIs.

## Alternatives Considered

- External HTTP server (Flask/FastAPI) on another machine or container — rejected because the user requested no extra server and prefers all features inside HA.
- AppDaemon or a full custom integration — viable, but heavier: custom integration requires packaging and a deeper HA integration lifecycle. Pyscript provides faster iteration for the MVP.
- Storing data in HA entities or `.storage` — possible, but `.storage` is reserved and not intended for arbitrary custom data. A dedicated SQLite file is simpler and portable.

## Implementation Notes

- Communication pattern: frontend -> call HA service (domain `todo_system`, service `request`) with payload {"id": <uuid>, "action": "list_due" | "create_task" | ... , "params": {...}}. The backend (pyscript) processes the request and fires an event `todo_response` with payload {"id": <uuid>, "status": "ok"|"error", "data": {...}}. The frontend listens for `todo_response` events on the HA websocket and matches `id` to correlate responses.

- Service model rationale: Home Assistant services are callable from the frontend without cross-origin issues and don't require starting a separate HTTP server inside HA.

- SQLite usage: open the database file with `sqlite3.connect(db_path, timeout=5, check_same_thread=False)` and set `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;` on connect. Keep transactions short and use `BEGIN`/`COMMIT` for atomic operations.

- Concurrency: serialize writes with a simple file lock using `fcntl.flock()` (POSIX) or an asyncio-based lock if available. Additionally, keep the critical write section short; reads can be concurrent.

- Boot/migration: on first startup the pyscript module will check for the DB file and run `CREATE TABLE IF NOT EXISTS` statements for schema defined in `data-model.md`.

## Security & Permissions

- Because the frontend is embedded in Home Assistant, all calls originate from authenticated HA sessions; ensure that any external access to the HA instance is protected (long-lived tokens are needed only for out-of-band clients).
- Limit who can access the panel via Home Assistant user roles if desired.

## Verification Steps (how to validate the decisions)

1. Install Pyscript via HACS on a test HAOS instance.
2. Add a minimal pyscript that opens a sqlite DB under `/config/todo_system/test.db`, creates a table, and performs a simple insert and select. Reload Pyscript and verify operations succeed.
3. Build the React app, copy a small `index.html` into `/config/www/test-ui/` and configure a `panel_custom` entry that points to `/local/test-ui/index.html`. Confirm panel loads in HA frontend.

## Open Questions (resolved)

- Does Pyscript support the Python `sqlite3` module? — Yes; Pyscript runs inside Home Assistant's Python environment and can access the standard library. Validate with the verification steps above.
- Where to place the DB file? — Chosen path: `/config/todo_system/todo.db`.

## Result

All clarifications required to proceed with Phase 1 design are resolved by the decisions above. The next step is to author the concrete schema (`data-model.md`), the service contract (`contracts/services.md`) and the quickstart validation guide (`quickstart.md`).
