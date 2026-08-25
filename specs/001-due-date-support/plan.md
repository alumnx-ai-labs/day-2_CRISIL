# Implementation Plan: Task Due-Date Support

**Branch**: `001-due-date-support` | **Date**: 2026-08-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-due-date-support/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add an optional ISO 8601 calendar `due_date` to tasks, validate it as today or
later on creation, support setting and clearing it during updates, and add an
exclusive `due_before` filter to `GET /tasks`. Extend the existing Pydantic
schemas, explicitly wire the field through the in-memory repository, and pass
the filter through the existing route and repository layers. No new dependency
or storage system is required.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 (repository runtime)

**Primary Dependencies**: FastAPI, Pydantic, pytest; no new dependencies

**Storage**: In-memory `TaskRepository` singleton

**Testing**: pytest with FastAPI `TestClient`

**Target Platform**: Python web service

**Project Type**: REST web service

**Performance Goals**: Preserve current in-memory list/filter behavior; no new target specified

**Constraints**: Preserve existing endpoint paths, response shapes, defaults,
status codes, and error contracts. Storage stays in memory. `create_task` MUST
build `Task` explicitly rather than unpacking `task_data`.

**Scale/Scope**: One additive task field and one list filter across `app/models.py`,
`app/repository.py`, `app/routes.py`, and the task API tests.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Test-first**: PASS. Add creation, update, filter, validation, and regression
  tests; pytest MUST pass before completion.
- **Backward compatibility**: PASS. `due_date` is optional and existing
  requests retain current behavior; existing response fields remain unchanged.
- **Repository/API conventions**: PASS. Use existing Pydantic schemas, explicit
  repository construction, optional filter parameters, and HTTP 400/404 handling.
- **Minimal dependencies/storage**: PASS. No dependency changes; storage remains
  in memory.
- **Complete contract tests**: PASS. Include fixture default, creation, update,
  filter, and applicable 400 edge-case coverage.

## Project Structure

### Documentation (this feature)

```text
specs/001-due-date-support/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
```text
app/
├── models.py       # Task schemas and date validation
├── repository.py   # Explicit Task construction and due-date filtering
└── routes.py       # Task routes and due_before query

tests/
├── conftest.py     # Repository reset and fixture payload
└── test_tasks.py   # API contract and regression tests
```

**Structure Decision**: Extend the existing FastAPI service in `app/` and its
API test suite in `tests/`. Keep design artifacts under this feature directory.

## Phase 0: Research

Research decisions are recorded in [research.md](research.md). The design uses
calendar dates, applies the past-date rule on creation only, treats `due_before`
as an exclusive cutoff, and preserves the existing architecture without new
dependencies or storage.

## Phase 1: Design Artifacts

- [data-model.md](data-model.md) defines the optional Task field and date rules.
- [contracts/tasks.md](contracts/tasks.md) defines create, update, list, and
  compatibility behavior.
- [quickstart.md](quickstart.md) defines automated and manual validation steps.

## Post-Design Constitution Check

- **Test-first**: PASS. The design maps directly to fixture, creation, update,
  filter, validation, and regression tests.
- **Backward compatibility**: PASS. The feature is additive; existing requests
  and response fields remain compatible.
- **Repository/API conventions**: PASS. The design preserves schema, explicit
  repository construction, route filtering, and existing 400/404 contracts.
- **Minimal dependencies/storage**: PASS. No dependency or storage changes are
  proposed.
- **Complete contract tests**: PASS. Every required test category is identified
  in the spec and quickstart.

## Complexity Tracking

No constitution violations. No additional complexity requires justification.
