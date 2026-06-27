# Deployment guide

## Overview

This project is designed for deployment as a Home Assistant custom panel plus Pyscript handlers. The frontend is a static React/Vite build, and the backend is a set of Python modules copied into Home Assistant's Pyscript directory.

## Recommended deployment flow

1. Build the frontend locally:

```bash
cd frontend
npm install
npm run build
```

2. Copy the built assets to Home Assistant:

```bash
scp -r frontend/dist/* user@homeassistant:/config/www/todo-system/
```

3. Copy the backend modules:

```bash
scp ha/pyscripts/*.py user@homeassistant:/config/pyscripts/
```

4. Reload Home Assistant and verify the panel loads.

## Database and migration strategy

- The SQLite database should live under the Home Assistant config directory, for example `/config/todo_system/todo.db`.
- The backend should run migrations on startup and maintain a `meta` table with a `schema_version` entry.
- When changing the schema, bump the version and add an explicit migration in the backend module before deploying the new scripts.
- Preserve the database during upgrades and take a backup before any schema change.

## Backup recommendations

- Back up the database file and the `pyscripts/` directory regularly.
- Keep copies of the frontend build artifacts in source control or an internal artifact store.
- For production deployments, test the restore procedure before relying on it.

## Operational notes

- Use WAL mode and keep transactions short.
- Restrict file access to the database file with strict permissions.
- Monitor Home Assistant logs after deployment for syntax or runtime failures.
