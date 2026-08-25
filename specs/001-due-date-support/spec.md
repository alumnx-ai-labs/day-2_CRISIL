# Feature Specification: Task Due-Date Support

**Feature Branch**: `001-due-date-support`

**Created**: 2026-08-25

**Status**: Draft

**Input**: User description: "Add due-date support to tasks: an optional due_date field (ISO 8601 date), filterable via GET /tasks?due_before=<date>, with validation that due_date (if provided on create) must be today or later. Must not break any existing endpoint."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set a task due date (Priority: P1)

As a task manager, I want to assign an optional due date when creating a task so that the task's expected completion date is recorded and visible.

**Why this priority**: Recording the due date is the core value of the feature and enables all date-based task planning.

**Independent Test**: Create a task with a valid future or current date and verify the task is accepted and the returned task contains that date. Create a task without a due date and verify existing creation behavior remains valid.

**Acceptance Scenarios**:

1. **Given** a valid task creation request with an ISO 8601 calendar date that is today or later, **When** the task is created, **Then** the request succeeds and the returned task contains the supplied `due_date`.
2. **Given** a task creation request without `due_date`, **When** the task is created, **Then** the request succeeds and the returned task has no due date.
3. **Given** a task creation request with a due date before today, **When** the task is submitted, **Then** the request is rejected as invalid with the API's existing 400 validation response.

---

### User Story 2 - Update a task due date (Priority: P2)

As a task manager, I want to add, change, or clear a task's due date after creation so that schedules remain accurate as plans change.

**Why this priority**: Tasks often change after creation, and maintaining the date is necessary for the field to remain useful.

**Independent Test**: Create a task, update only its due date, verify the new value, then clear it and verify the task has no due date while its other fields remain unchanged.

**Acceptance Scenarios**:

1. **Given** an existing task, **When** an update supplies a valid `due_date`, **Then** the task is updated and the response contains the new date.
2. **Given** an existing task with a due date, **When** an update supplies `due_date: null`, **Then** the due date is cleared and unrelated task fields remain unchanged.
3. **Given** an existing task, **When** an update omits `due_date`, **Then** the existing due date remains unchanged.

---

### User Story 3 - Find tasks due before a date (Priority: P2)

As a task manager, I want to filter tasks by a due-date cutoff so that I can focus on work due before a selected date.

**Why this priority**: Date filtering turns stored due dates into an actionable planning view.

**Independent Test**: Create tasks with dates before, on, and after a cutoff, plus a task without a due date; query the cutoff and verify only tasks with dates strictly before it are returned.

**Acceptance Scenarios**:

1. **Given** tasks with due dates before, equal to, and after a supplied date, **When** `GET /tasks?due_before=<date>` is requested, **Then** only tasks with due dates strictly before the supplied date are returned.
2. **Given** a task without a due date, **When** a `due_before` filter is requested, **Then** that task is excluded from the filtered results.
3. **Given** no tasks match the cutoff, **When** the filter is requested, **Then** the response succeeds with an empty list.
4. **Given** an invalid `due_before` value, **When** the list endpoint is requested, **Then** the request is rejected as invalid with the API's existing 400 validation response.

---

### Edge Cases

- A due date equal to today is valid on task creation.
- A due date one day before today is invalid on task creation.
- `due_date` is omitted on creation and is represented as absent/null in the task response, consistent with existing optional task fields.
- `due_date: null` clears an existing due date during update.
- An update that omits `due_date` does not clear or alter the existing value.
- A task without a due date does not match `due_before`.
- A task whose due date equals the `due_before` cutoff does not match, because the cutoff is exclusive.
- Existing task fields, defaults, endpoint paths, status codes, and response fields remain unchanged apart from the additive optional due-date field.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support an optional `due_date` field on task entities and task responses.
- **FR-002**: The system MUST accept `due_date` as an ISO 8601 calendar date and reject malformed date values with the existing HTTP 400 validation contract.
- **FR-003**: The system MUST allow task creation without `due_date`; omitted due dates MUST retain the existing create-task success behavior and be returned as absent/null according to the established optional-field response convention.
- **FR-004**: When `due_date` is provided during task creation, the system MUST accept today or any later date and MUST reject dates before today with HTTP 400.
- **FR-005**: The system MUST allow an existing task's `due_date` to be set or replaced through task update without changing omitted fields.
- **FR-006**: The system MUST allow an existing task's `due_date` to be cleared by sending `null` in an update.
- **FR-007**: The system MUST preserve an existing `due_date` when an update omits that field.
- **FR-008**: `GET /tasks` MUST accept an optional `due_before` date filter.
- **FR-009**: The `due_before` filter MUST return only tasks whose due date is strictly earlier than the supplied date; tasks without a due date MUST be excluded.
- **FR-010**: Invalid `due_before` values MUST return HTTP 400 using the existing request-validation error shape.
- **FR-011**: Existing `/tasks` endpoint paths, request behavior, response shapes, defaults, status codes, and existing error behavior MUST remain compatible for clients that do not use due-date functionality.
- **FR-012**: The feature MUST include the existing test fixture's due-date default, creation coverage, update coverage, filter coverage, and applicable 400 edge-case coverage for invalid dates and past create dates.

### Key Entities

- **Task**: An existing unit of work, extended with an optional calendar `due_date` that identifies the date by which the task is intended to be completed.
- **Due-date filter**: A list-query cutoff date used to select tasks with due dates strictly earlier than the supplied date.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of task creation requests with a valid due date equal to today or later return the due date unchanged in the created task response.
- **SC-002**: 100% of task creation requests with a due date before today are rejected with HTTP 400, and 100% of malformed due-date inputs are rejected with HTTP 400.
- **SC-003**: For a test set containing tasks before, on, and after a cutoff plus undated tasks, 100% of returned filtered tasks have dates strictly before the cutoff and no qualifying task is omitted.
- **SC-004**: 100% of existing endpoint regression tests continue to pass for requests that do not use due-date functionality, with no changes to their response status or established fields.
- **SC-005**: A user can create, revise, clear, and filter task due dates through the documented task workflows without needing a separate task-management process.

## Assumptions

- The date is a calendar date without a time or timezone component; ISO 8601 date means the `YYYY-MM-DD` form.
- “Before” is an exclusive cutoff: a task dated exactly on `due_before` is not returned.
- The create-time rule is the only explicitly required temporal validation. Updates may set or clear the optional field, including a past date, unless a future clarification or approved specification adds the same restriction to updates.
- Existing task responses use `null` for unset optional scalar fields; the new unset `due_date` follows that convention.
- No new storage system, external service, authentication behavior, or dependency is required.
- Existing `/tasks` behavior remains the compatibility baseline, and due-date support is additive.
