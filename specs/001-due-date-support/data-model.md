# Data Model: Task Due-Date Support

## Task

The existing Task entity gains one optional field:

| Field | Type | Required | Default | Rules |
| --- | --- | --- | --- | --- |
| `due_date` | ISO 8601 calendar date (`YYYY-MM-DD`) or null | No | `null` | On creation, if provided, MUST be today or later. |

All existing Task fields, defaults, generated identity, and creation timestamp
remain unchanged.

## Create Task

`due_date` is optional. Omission creates an undated task. A supplied value must
be a valid ISO 8601 calendar date and must not be before the current calendar
date.

## Update Task

`due_date` is optional and supports three distinct operations:

- Omitted: preserve the current value.
- A valid date: set or replace the current value.
- `null`: clear the current value.

The feature specification adds no past-date restriction to updates.

## Due-Date Filter

`due_before` is an optional list filter represented by a valid ISO 8601 calendar
date. It selects tasks with `due_date` strictly earlier than the cutoff. Tasks
with `due_date: null` are excluded when the filter is present.

## Relationships and State

No new entity or relationship is introduced. The due date has no effect on the
existing task status or priority state transitions.
