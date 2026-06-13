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

## Local development cycle (recommended)

- Develop the frontend locally and test UI in the browser using `npm run dev` (Vite/CRA). For fastest validation, build and copy the production build to HA for integration testing; the frontend must run inside HA to access the logged-in HA session and call services without CORS issues.

## Notes and troubleshooting

- If the panel shows a blank page after configuring `panel_custom`, check `home-assistant.log` for errors and ensure the `index.html` path is correct under `/config/www/todo-system/`.
- Ensure the pyscript integration is enabled and that `pyscripts/` files have no syntax errors; check the Pyscript log output in HA.