# services.md

This file documents the service contract between the frontend (React custom panel) and the backend (Pyscript handlers running inside Home Assistant). Communication is implemented as:

- Frontend calls a Home Assistant service: `todo_system.request` with payload `{ id, action, params }`.
- Backend processes the request and fires an event `todo_response` with payload `{ id, status, data, error? }`.

Note: HA services do not return HTTP responses; the event-based response pattern provides an asynchronous, same-origin friendly way for the frontend to receive results.

---

Service: `todo_system.request`

Payload (JSON):

- `id` (string, required): client-generated UUID to correlate request/response.
- `action` (string, required): one of `list_due`, `create_task`, `update_task`, `delete_task`, `complete_occurrence`, `get_task`, `list_users`.
- `params` (object, optional): action-specific parameters.

Action-specific params and expected `data` in the response:

- `list_due`:
  - params: `{ date?: "YYYY-MM-DD" }` (defaults to today)
  - response.data: `{ occurrences: [ { occurrence_id, task: { id, title, assignee_id }, date, status } ] }`

- `create_task`:
  - params: `{ title: string, description?: string, assignee_id?: int, start_due_date?: "YYYY-MM-DD", end_due_date?: "YYYY-MM-DD", recurrence_rule?: object }
  - response.data: `{ task_id: int }`

- `update_task`:
  - params: `{ task_id: int, fields: { ... } }
  - response.data: `{ success: true }`

- `delete_task`:
  - params: `{ task_id: int }
  - response.data: `{ success: true }`

- `complete_occurrence`:
  - params: `{ task_id: int, date: "YYYY-MM-DD", completed_by?: int }
  - response.data: `{ occurrence_id: int, status: "completed" }`

- `get_task`:
  - params: `{ task_id: int }
  - response.data: `{ task: { ... } }`

- `list_users`:
  - params: none
  - response.data: `{ users: [ { id, name, display_name } ] }`

Error responses: `status` is `error` and `error` is a string describing the failure.

---

Frontend example (pseudo-code):

```js
const id = crypto.randomUUID();
// send service request
await hass.callService('todo_system', 'request', { id, action: 'list_due', params: { date: '2026-06-16' } });

// listen for response events (subscribe once and match id)
const handle = (event) => {
  if (event.detail && event.detail.id === id) {
    // process event.detail.data or event.detail.error
    unsubscribe();
  }
};
window.addEventListener('ha-event-todo_response', handle);
```

Backend contract notes:

- Canonical recurrence format: `recurrence_rule` MUST be a JSON object in requests and persisted records (MVP canonical form). Example:

```json
{ "freq": "weekly", "interval": 1, "byweekday": [1], "until": "2026-12-31" }
```

- The pyscript handler MUST fire an event named `todo_response` with the JSON payload described above. The frontend will receive events via the Home Assistant websocket layer.
- The pyscript handler MUST never block HA's event loop for long periods. Use short DB transactions, file locks, or offload heavy work to an executor.

- Validation: service handlers MUST validate `recurrence_rule` JSON (shape and allowed values) and return `status: "error"` with a descriptive `error` string when validation fails. Unit tests must cover invalid recurrence payloads.
