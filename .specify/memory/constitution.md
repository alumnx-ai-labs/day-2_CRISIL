<!--
Sync Impact Report
- Version change: template placeholders -> 1.0.0
- Modified principles: none; initial project constitution created
- Added sections: Core Principles, Technical Constraints, Development Workflow
- Removed sections: none
- Follow-up TODOs: original ratification date is not recorded in the repository
-->

# Task Management API Constitution

## Core Principles

### I. Test-First (NON-NEGOTIABLE)
Pytest MUST pass before any change is considered done. New behavior MUST be
covered by tests before implementation is accepted, including success paths,
validation failures, and applicable not-found cases. This keeps the API contract
executable and prevents regressions from being accepted as completed work.

### II. Backward Compatibility
Existing `/tasks` endpoints and response shapes MUST NOT break. Changes to
existing request or response contracts require explicit specification and
corresponding migration or compatibility treatment. Existing defaults and
optional fields MUST remain usable by current clients unless a deliberate
breaking change is approved under Governance.

### III. Repository and API Conventions
Implementation MUST follow the conventions in
`.github/skills/task-management-api.skill.md`. Task persistence MUST use the
repository pattern, Pydantic schemas MUST represent optional fields with
appropriate `Optional[...]` or defaults, and missing task IDs MUST raise
`TaskNotFoundError` in the repository and be translated to HTTP 404 by routes.
Invalid request validation MUST use the application's HTTP 400 contract.

### IV. Minimal Dependencies and In-Memory Storage
New dependencies MUST NOT be added without written justification and a review
of their maintenance and runtime impact. Storage MUST remain in memory unless
an approved feature specification explicitly changes that requirement. The
implementation MUST favor the existing FastAPI, Pydantic, repository, and
pytest stack for the current API.

### V. Complete Contract Tests for Additions
Every new field or endpoint MUST include a fixture default, a creation test, an
update test, a filter test when the field or endpoint is filterable, and an
applicable 404 or 400 edge-case test. Tests MUST verify both the public request
and response contract and the relevant failure behavior so additions remain
compatible with the API's established conventions.

## Technical Constraints

The application is a FastAPI Task Management REST API with Pydantic models, an
in-memory repository, and pytest tests. Changes MUST preserve the existing
module boundaries: models define schemas, the repository owns storage and task
lookup, routes define HTTP contracts, and the application owns global request
validation handling. External calls, authentication, and secrets are
security-sensitive changes and are governed by the security review requirement
below.

## Development Workflow

Changes MUST be implemented in the smallest appropriate module set and checked
with the focused pytest tests before the full suite is considered. A change is
complete only when its required tests pass, its request-validation and
not-found behavior are covered where applicable, and its compatibility impact
has been reviewed. Security-sensitive changes involving authentication,
secrets, or external calls MUST be reviewed by `security-agent` before merge.

## Governance

This constitution governs changes to the Task Management API. When a proposed
implementation conflicts with it, the conflict MUST be resolved by amending
the constitution or changing the implementation; silently bypassing a
principle is not permitted.

Amendments MUST state the affected principle or section, the reason for the
change, and its compatibility impact. An amendment MUST update the Sync Impact
Report, the version, and the last-amended date. The constitution owner or
maintainer MUST review the amendment before it is merged.

Versioning follows semantic versioning. A MAJOR increment is required for a
backward-incompatible governance change or removal/redefinition of a principle.
A MINOR increment is required for a new principle or materially expanded
governance requirement. A PATCH increment is required for clarifications,
wording corrections, or other non-semantic refinements.

Every change review MUST verify compliance with this constitution, including
test evidence and compatibility impact. Security-sensitive changes MUST include
the required `security-agent` review before merge. The constitution MUST be
reviewed whenever the API contract, storage model, dependency set, or security
posture changes materially.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date is not recorded | **Last Amended**: 2026-08-25
