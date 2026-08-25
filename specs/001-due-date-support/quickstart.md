# Quickstart: Task Due-Date Support

## Prerequisites

From the repository root, use the existing virtual environment and installed
project dependencies.

## Automated Validation

Run the focused task API suite:

```bash
pytest tests/test_tasks.py
```

Run the complete suite:

```bash
pytest -q
```

Expected result: all existing tests and due-date tests pass.

## Manual Scenarios

Start the existing service with:

```bash
uvicorn app.main:app --reload
```

Validate these scenarios using the API documentation at `/docs` or an HTTP
client:

1. Create a task with `due_date` set to today. Expect HTTP 201 and the same
   date in the response.
2. Create a task without `due_date`. Expect HTTP 201 and `due_date: null`.
3. Create a task with yesterday's date. Expect HTTP 400.
4. Update an existing task with a due date, then update it with `null`. Expect
   HTTP 200 and the field cleared.
5. Create tasks before, on, and after a cutoff plus an undated task. Request
   `GET /tasks?due_before=<cutoff>`. Expect only tasks strictly before the
   cutoff.
6. Request the filter with an invalid date. Expect HTTP 400.

The complete endpoint contract is documented in [contracts/tasks.md](contracts/tasks.md),
and the field rules are documented in [data-model.md](data-model.md).
