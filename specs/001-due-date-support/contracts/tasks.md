# Task API Contract: Due-Date Support

## Compatibility Rule

Existing `/tasks` requests that omit due-date functionality retain their current
paths, status codes, defaults, error behavior, and existing response fields.
The optional `due_date` response field is additive.

## `POST /tasks`

Accepts the existing task creation JSON object plus optional `due_date`.

- `due_date` omitted: create an undated task and return `due_date: null`.
- `due_date` supplied: require `YYYY-MM-DD` and reject a date before today.

Success: HTTP `201 Created`; response is the created task with `due_date`.
Invalid or past due dates: HTTP `400 Bad Request` using the existing validation
error shape.

## `PUT /tasks/{task_id}`

Accepts the existing partial task update object plus optional `due_date`.

- Omitted: preserve the existing due date.
- Valid `YYYY-MM-DD`: set or replace the due date.
- `null`: clear the due date.

Success: HTTP `200 OK`; response is the updated task with `due_date`.
Invalid date format: HTTP `400 Bad Request` using the existing validation error
shape. Missing task: HTTP `404 Not Found` using the existing task-not-found
detail shape. An empty update body remains HTTP `400 Bad Request`.

## `GET /tasks`

Accepts the existing optional filters plus:

- `due_before=<YYYY-MM-DD>`: return only tasks with due dates strictly earlier
  than the cutoff. Undated tasks and tasks on or after the cutoff are excluded.

Success: HTTP `200 OK` with the existing task array response shape plus the
optional `due_date` field. Invalid `due_before`: HTTP `400 Bad Request` using
the existing validation error shape. With no matches, return an empty array.

## Other Endpoints

`GET /tasks/{task_id}`, `DELETE /tasks/{task_id}`, and `GET /health` retain their
existing contracts. Single-task responses include the additive `due_date` field
when applicable; not-found behavior remains HTTP 404.
