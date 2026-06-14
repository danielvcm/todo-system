## Quickstart (developer notes)

- Home Assistant: copy built frontend to `/config/www/todo-system/` and pyscripts to `/config/pyscripts/` for local testing.
- Pyscript DB path: default is `ha/data/todo.sqlite`. Override with `TODO_DB_PATH` env var during dev.
- Recommended PRAGMAs: WAL journal, `synchronous=NORMAL`, `foreign_keys=ON`.
- For local dev, run `python3 -m ha.pyscripts.todo_db` to apply migrations.
# quickstart.md

This quickstart describes the minimal steps to validate the feature end-to-end in Home Assistant OS (HAOS). It assumes you have access to the HA UI (HACS installed or installable) and permission to copy files into the HA `config` directory (Samba/SSH add-on or similar).

## Prerequisites

- Home Assistant OS (HAOS) instance reachable (your existing laptop).
- HACS installed in Home Assistant (for Pyscript via HACS) or Pyscript otherwise installed.
- Access to the HA `config` folder (Samba share, SSH, or the file editor add-on).

## Deploy backend (Pyscript)

1. Install Pyscript via HACS (or follow the Pyscript installation docs).

2. Copy the pyscript module(s) to the HA config `pyscripts/` directory. Example path inside HA: `/config/pyscripts/todo_system.py`.

3. Restart Home Assistant or reload Pyscript.

### Verify DB and Storage Security (required for production)

- After deploying the pyscript modules, confirm the database file exists at the configured path (recommended `/config/todo_system/todo.db`). From the HA host or Docker container, run:

```bash
ls -l /config/todo_system/todo.db
```

- Verify file permissions restrict access (recommended `600`):

```bash
chmod 600 /config/todo_system/todo.db
ls -l /config/todo_system/todo.db
```

- Verify underlying storage is encrypted for production systems. Exact steps depend on your HA installation model:
  - HAOS: Prefer enabling HAOS disk encryption where supported; consult HAOS documentation for enabling/disabling encryption for your device.
  - VM-based deployments: ensure the VM disk is encrypted at the hypervisor or host level.
  - Container-based/dev environments: use an encrypted host filesystem or encrypted volume for `/config`.

- Basic host-level checks (may require host/SSH access):

```bash
# show block devices and mountpoints
lsblk -o NAME,MOUNTPOINT,TYPE,SIZE

# on some hosts, check for LUKS devices
sudo cryptsetup status <device-name>
```

- Add a verification entry to your deployment checklist that confirms encryption is enabled for production. The `specs/001-household-chore-tracker/quickstart.md` should document how to perform this verification for your target production environment.

## Deploy frontend (React custom panel)

1. Build the React app locally:

```bash
cd frontend
npm install
npm run build   # produce `dist/` (Vite) or `build/` (CRA)
```

2. Copy the build output to HA `www` directory. Example using `scp` (or use Samba):

```bash
# from your dev machine
scp -r dist/* user@homeassistant:/config/www/todo-system/
```

3. Add a `panel_custom` entry to `configuration.yaml` (reload HA after editing):

```yaml
panel_custom:
  - name: todo-system
    sidebar_title: "Chore Tracker"
    sidebar_icon: mdi:clipboard-check
    url_path: todo-system
    config:
      html_url: /local/todo-system/index.html
```

4. Restart Home Assistant and open the new sidebar entry "Chore Tracker".

## Validate (end-to-end)

1. Open the custom panel in the HA UI.
2. Ensure Pyscript logs show the module loaded and the database migrations ran (if implemented).
3. Use the UI to create a recurring task and confirm it appears in "Due Today" when appropriate.

## Quick verification: Recurrence format

- When creating tasks via the UI or direct service calls, the `recurrence_rule` payload MUST be a JSON object in the canonical format (see `data-model.md`). Example service payload for creating a weekly task on Mondays:

```json
{ "id": "<uuid>", "action": "create_task", "params": { "title": "Take out trash", "recurrence_rule": { "freq": "weekly", "byweekday": [1] } } }
```

The backend will validate the recurrence JSON and return an error if the shape is invalid.

## Local development cycle (recommended)

- Develop the frontend locally and test UI in the browser using `npm run dev` (Vite/CRA). For fastest validation, build and copy the production build to HA for integration testing; the frontend must run inside HA to access the logged-in HA session and call services without CORS issues.

## Notes and troubleshooting

- If the panel shows a blank page after configuring `panel_custom`, check `home-assistant.log` for errors and ensure the `index.html` path is correct under `/config/www/todo-system/`.
- Ensure the pyscript integration is enabled and that `pyscripts/` files have no syntax errors; check the Pyscript log output in HA.