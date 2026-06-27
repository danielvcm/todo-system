# Release checklist

## Pre-release

- [ ] Run backend unit tests
- [ ] Run frontend unit tests
- [ ] Run Playwright smoke test
- [ ] Verify the database path and permissions
- [ ] Confirm the panel_custom entry is present
- [ ] Back up the current database and config files

## Release

- [ ] Deploy the latest frontend build and Pyscript modules
- [ ] Reload Home Assistant and verify the panel loads
- [ ] Create a sample task and confirm it appears in the Due Today view
- [ ] Validate completion history and recurring behavior

## Post-release

- [ ] Review logs for warnings or errors
- [ ] Capture any follow-up issues for the next iteration
