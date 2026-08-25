---

description: "Task list for implementing Task Due-Date Support"
---

# Tasks: Task Due-Date Support

**Input**: Design documents from `specs/001-due-date-support/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and
`contracts/tasks.md`

**Tests**: Included because the constitution mandates test-first development and
`spec.md` requires creation, update, filter, validation, and regression coverage.

**Organization**: Tasks are grouped by user story so each story can be tested as
an independently valuable increment.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing project and test entry points are ready; no
new project dependencies or storage infrastructure are required.

- [X] T001 [P] Verify the existing Python dependencies and pytest entry point in `requirements.txt` and `pytest.ini`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared optional field shape and fixture default required by
all user stories before story-specific behavior is implemented.

- [X] T002 Add the optional `due_date` default to the shared task creation fixture in `tests/test_tasks.py`
- [X] T003 [P] Add optional `due_date` fields to `Task`, `TaskCreate`, and `TaskUpdate` in `app/models.py`, using an ISO calendar-date type and preserving existing defaults
- [X] T004 Add create-time validation for supplied dates before today in `app/models.py` while leaving update date assignment and clearing behavior unrestricted

**Checkpoint**: Shared schema and fixture support is ready; user story tests
can now be written against the intended contract.

---

## Phase 3: User Story 1 - Set a Task Due Date (Priority: P1) 🎯 MVP

**Goal**: Create tasks with an optional due date, accept today or future dates,
reject past or malformed dates, and preserve undated-task behavior.

**Independent Test**: Run the US1 tests in `tests/test_tasks.py` to create tasks
with today, future, missing, past, and malformed due dates; verify status,
response value, and HTTP 400 validation behavior.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [US1] Add creation tests for valid today and future `due_date` values in `tests/test_tasks.py`
- [X] T006 [US1] Add creation regression and validation tests for omitted, past, and malformed `due_date` values in `tests/test_tasks.py`

### Implementation for User Story 1

- [X] T007 [US1] Wire `due_date` explicitly into `TaskRepository.create_task` in `app/repository.py` without unpacking `task_data`
- [X] T008 [US1] Verify the `POST /tasks` response exposes `due_date` and retains existing create defaults in `app/routes.py` and `tests/test_tasks.py`

**Checkpoint**: User Story 1 is independently functional and provides the MVP
for recording task due dates.

---

## Phase 4: User Story 2 - Update a Task Due Date (Priority: P2)

**Goal**: Set, replace, clear, and preserve `due_date` through partial task
updates without changing unrelated fields.

**Independent Test**: Create a task, update only its due date, clear it with
`null`, and update an unrelated field while confirming the due date behavior.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [US2] Add tests for setting and replacing only `due_date` through `PUT /tasks/{task_id}` in `tests/test_tasks.py`
- [X] T010 [US2] Add tests for clearing `due_date` with `null`, preserving it when omitted, and retaining unrelated fields in `tests/test_tasks.py`
- [X] T011 [US2] Add update validation and missing-task regression tests for due-date updates in `tests/test_tasks.py`

### Implementation for User Story 2

- [X] T012 [US2] Confirm `TaskUpdate` omission, date assignment, and `null` clearing flow through `model_dump(exclude_unset=True)` and `TaskRepository.update_task` in `app/models.py` and `app/repository.py`
- [X] T013 [US2] Verify `PUT /tasks/{task_id}` returns the updated due date and preserves existing HTTP 400/404 behavior in `app/routes.py` and `tests/test_tasks.py`

**Checkpoint**: User Stories 1 and 2 are independently functional; due dates
can be maintained after task creation.

---

## Phase 5: User Story 3 - Find Tasks Due Before a Date (Priority: P2)

**Goal**: Filter the task list by an exclusive `due_before` date while excluding
undated tasks and preserving existing filters and ordering.

**Independent Test**: Create tasks before, on, and after a cutoff plus an
undated task, request `GET /tasks?due_before=<date>`, and verify only strictly
earlier dates are returned.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [US3] Add list-filter tests for dates before, equal to, and after the cutoff and for undated tasks in `tests/test_tasks.py`
- [X] T015 [US3] Add tests for empty due-date filter results, invalid `due_before`, and composition with existing status/assignee filters in `tests/test_tasks.py`

### Implementation for User Story 3

- [X] T016 [US3] Add an optional `due_before` parameter and exclusive date filtering to `TaskRepository.get_all_tasks` in `app/repository.py`
- [X] T017 [US3] Expose `due_before` as a validated optional query parameter on `GET /tasks` and pass it to the repository in `app/routes.py`
- [X] T018 [US3] Verify due-date-filter responses retain ascending task ID ordering and existing filter behavior in `tests/test_tasks.py`

**Checkpoint**: All user stories are independently functional and the complete
due-date contract is covered.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Run the complete compatibility and quality checks across all stories.

- [X] T019 [P] Update the task API documentation and quickstart references for due-date behavior in `README.md` and `specs/001-due-date-support/quickstart.md`
- [X] T020 Run the focused due-date and existing task tests in `tests/test_tasks.py` and confirm all tests pass
- [X] T021 Run the full pytest suite with `pytest -q` and verify no existing endpoint regression in `tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 can start immediately.
- **Foundational (Phase 2)**: T002-T004 depend on the existing setup and block all user stories.
- **User Story 1 (Phase 3)**: Depends on T002-T004; this is the MVP increment.
- **User Story 2 (Phase 4)**: Depends on T002-T004 and the shared Task schema; its tests may be developed after the schema foundation and validated independently.
- **User Story 3 (Phase 5)**: Depends on T002-T004 and the shared Task schema; its filter implementation depends on the due-date repository value being stored by US1.
- **Polish (Phase 6)**: Depends on all desired user story work being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on another user story after foundational schema work.
- **US2 (P2)**: Uses the shared due-date field from the foundation; update merging follows the existing partial-update behavior.
- **US3 (P2)**: Uses stored due dates from US1 and the shared schema; it can be tested with seeded repository data but is delivered after the create path for a coherent increment.

### Within Each User Story

- Tests MUST be written first and fail before the corresponding implementation.
- Model/schema work precedes repository work; repository work precedes route wiring.
- Each story checkpoint requires its focused tests to pass before moving to the next story.
- Existing endpoint behavior MUST be checked after each story because backward compatibility is non-negotiable.

### Parallel Opportunities

- T001 and T003 touch different files and can be prepared in parallel when the setup prerequisite is already satisfied.
- T005 and T006 are separate test additions but share `tests/test_tasks.py`; parallel work requires coordination to avoid edit conflicts.
- T009-T011 are logically parallel test cases but share `tests/test_tasks.py`.
- T014 and T015 are logically parallel filter test cases but share `tests/test_tasks.py`.
- Different user-story test design can proceed in parallel after foundational schema decisions, but implementation should integrate in priority order to minimize conflicts in shared files.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001-T004.
2. Write and fail T005-T006.
3. Implement T007-T008.
4. Run the US1-focused tests and confirm create-time date validation and response compatibility.
5. Stop at the US1 checkpoint for an independently usable MVP.

### Incremental Delivery

1. Add US2 update behavior and its focused tests.
2. Add US3 exclusive filtering and its focused tests.
3. Run the complete regression suite and quickstart validation.
4. Each increment preserves existing endpoints and response behavior for clients that do not send due-date fields.

### Notes

- Every task uses the required checkbox, sequential ID, optional `[P]` marker, story label where applicable, and an exact file path.
- No task introduces a dependency, external service, or non-memory storage.
- Security review is not required because this feature introduces no authentication, secret, or external-call change.
