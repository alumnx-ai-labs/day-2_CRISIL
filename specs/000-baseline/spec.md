# Baseline Specification: Current Task API Behavior

## Scope

This specification records the behavior currently implemented by the task API in `app/models.py`, `app/repository.py`, `app/routes.py`, `app/main.py`, and exercised by `tests/test_tasks.py`. It describes no behavior beyond those files.

## Task Entity

A `Task` response entity contains the following fields:

| Field | Type | Current behavior |
| --- | --- | --- |
| `id` | integer | Assigned by the in-memory repository, starting at 1 and incrementing for each created task. |
| `title` | string | Required by `TaskCreate`; creation validates length from 1 through 200 characters. |
| `description` | string | Defaults to `""` on creation; creation and update validate a maximum length of 2,000 characters. |
| `status` | `TaskStatus` | One of `pending`, `in_progress`, or `completed`; defaults to `pending` on creation and in the entity model. |
| `priority` | `TaskPriority` | One of `low`, `medium`, or `high`; defaults to `medium` on creation and in the entity model. |
| `assigned_to` | string or null | Optional and defaults to `null`; creation and update validate a maximum length of 200 characters. It can be assigned, reassigned, or cleared with `null` during update. |
| `tags` | array of strings | Defaults to `[]`; contains at most 20 values. Each value is stripped of surrounding whitespace and must contain 1 through 50 characters after validation. |
| `created_at` | datetime | Set by the repository at creation time using the current UTC time. It is returned in the task response and is not an update input field. |

The response model is `Task`. The repository stores tasks in memory in a singleton repository instance shared by the application. Listing results are sorted by ascending `id`.

## Enumerations

`status` accepts only:

- `pending`
- `in_progress`
- `completed`

`priority` accepts only:

- `low`
- `medium`
- `high`

Invalid enum values produce a request validation error.

## Create Input

`POST /tasks` accepts a JSON body matching `TaskCreate`:

- `title` is required and must be 1-200 characters.
- `description` is optional and defaults to `""`; maximum 2,000 characters.
- `status` is optional and defaults to `pending`.
- `priority` is optional and defaults to `medium`.
- `assigned_to` is optional and defaults to `null`; maximum 200 characters when provided.
- `tags` is optional and defaults to `[]`; maximum 20 values, with each tag trimmed and constrained to 1-50 characters.

A successful request returns HTTP `201 Created` with the created `Task` entity. The response includes the generated `id` and `created_at`.

## List Tasks

`GET /tasks` returns a JSON array of `Task` entities and HTTP `200 OK`.

Optional query parameters:

- `status`: filters results to tasks whose status exactly matches the supplied `TaskStatus` value.
- `assigned_to`: filters results to tasks whose `assigned_to` exactly matches the supplied string.

When both filters are provided, both filters apply. With no tasks, or when no tasks match, the response is an empty array. Results are ordered by ascending task `id`.

An invalid `status` query value produces HTTP `400 Bad Request` through the application-wide validation handler.

## Get One Task

`GET /tasks/{task_id}` accepts an integer `task_id` path parameter.

- If the task exists, it returns HTTP `200 OK` with that `Task` entity.
- If no task exists for the ID, it returns HTTP `404 Not Found` with a detail message of the form `Task with id {task_id} not found`.
- A path value that cannot be parsed as an integer is a request validation error and is returned as HTTP `400 Bad Request` by the application-wide validation handler.

## Update Task

`PUT /tasks/{task_id}` accepts a JSON body matching `TaskUpdate` and an integer `task_id` path parameter.

The body may provide any of these fields:

- `title`: optional; if provided, 1-200 characters.
- `description`: optional; if provided, maximum 2,000 characters.
- `status`: optional; must be a valid `TaskStatus` when provided.
- `priority`: optional; must be a valid `TaskPriority` when provided.
- `assigned_to`: optional and may be `null`; maximum 200 characters when a string is provided.
- `tags`: optional; maximum 20 values, with each tag trimmed and constrained to 1-50 characters.

Only fields explicitly present in the JSON body are applied. Existing values for omitted fields remain unchanged. In particular, `tags` can be updated by itself, cleared with `[]`, and `assigned_to` can be cleared with `null`.

An empty JSON object produces HTTP `400 Bad Request` with detail:

`At least one field must be provided to update a task`

For a successful update, the response is HTTP `200 OK` with the updated `Task` entity. The task ID and creation timestamp remain those of the existing task.

If the task does not exist, the response is HTTP `404 Not Found` with a detail message of the form `Task with id {task_id} not found`.

Invalid field values, invalid enum values, invalid tag counts or values, invalid path values, and other request-validation failures return HTTP `400 Bad Request` through the application-wide validation handler.

## Delete Task

`DELETE /tasks/{task_id}` accepts an integer `task_id` path parameter.

- If the task exists, it deletes the task and returns HTTP `204 No Content`.
- After successful deletion, retrieving the same task ID returns HTTP `404 Not Found`.
- If no task exists for the ID, it returns HTTP `404 Not Found` with a detail message of the form `Task with id {task_id} not found`.
- A path value that cannot be parsed as an integer is a request validation error and is returned as HTTP `400 Bad Request` by the application-wide validation handler.

## Health Endpoint

`GET /health` returns HTTP `200 OK` with the JSON body:

```json
{"status": "ok"}
```

## Error Responses

The application registers a global handler for FastAPI `RequestValidationError`. It returns HTTP `400 Bad Request` with a JSON body containing the validation errors under the `detail` key:

```json
{"detail": [/* validation error entries */]}
```

The tested validation cases include a missing title, a blank title, invalid create status, invalid create priority, more than 20 create tags, an invalid list status, an invalid update status, and an empty update body.

Repository lookup and deletion failures are represented as HTTP `404 Not Found` responses with a JSON `detail` string. The tested missing-resource cases are get, update, and delete for task ID `9999`.

## Tested Edge Cases

The current tests establish these additional observable cases:

- Creating without `assigned_to` returns `assigned_to: null`.
- Creating without tags returns `tags: []`.
- Tags supplied with surrounding whitespace are stored trimmed, such as `"  alpha  "` becoming `"alpha"`.
- A create request containing 21 tags is rejected with HTTP 400; direct `TaskCreate` construction with 21 tags raises `ValueError`.
- A `TaskUpdate` constructed with only `tags` reports only `tags` in `model_dump(exclude_unset=True)`.
- A tags-only update is accepted.
- Existing description data remains unchanged when an update supplies only status and title.
- Assigned users can be set from `null`, changed from one value to another, and cleared back to `null`.
- Tags can be replaced and cleared.
- Creating two tasks makes both available from `GET /tasks`.
- Listing an empty repository returns `[]`.
