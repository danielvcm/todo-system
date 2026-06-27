# Security notes

## Home Assistant-specific guidance

- Restrict access to the custom panel to trusted household users only.
- Keep the panel behind Home Assistant's normal authentication and role-based access controls.
- Do not expose the database file or Pyscript directory through public network access.

## Data-at-rest

- Store the SQLite database on encrypted storage when running in production.
- Use file permissions such as `chmod 600` for the database file.
- Keep backups encrypted when possible.

## Access control

- Treat the Home Assistant account used to operate the panel as a privileged account.
- Limit administrative access to the Home Assistant host and the config directory.
- Review the panel and service permissions periodically, especially when adding new household members.
