# Research: Task Due-Date Support

## Decision 1: Represent due dates as calendar dates

- **Decision**: Model `due_date` and `due_before` as ISO 8601 calendar dates in
  `YYYY-MM-DD` form, with no time or timezone component.
- **Rationale**: The feature describes a due date rather than a timestamp. A
  calendar date avoids timezone-dependent comparisons and matches the requested
  input format.
- **Alternatives considered**: Date-time values were rejected because they add
  precision and timezone behavior not required by the feature. Free-form strings
  were rejected because malformed values could not be reliably validated or
  compared.

## Decision 2: Apply the past-date rule on creation only

- **Decision**: Accept today and future dates on creation; reject dates before
  today. Updates may set, replace, or clear the field without an additional
  temporal restriction.
- **Rationale**: The feature explicitly scopes the validation rule to create
  requests. Keeping update behavior unrestricted supports schedule corrections
  and avoids adding an unstated constraint.
- **Alternatives considered**: Applying the same rule to updates was rejected
  because it would expand the stated requirement and prevent recording a past
  date when correcting historical task data.

## Decision 3: Use an exclusive list cutoff

- **Decision**: `due_before` returns tasks whose due date is strictly earlier
  than the supplied cutoff and excludes tasks without a due date.
- **Rationale**: The field name says “before,” and an exclusive boundary gives a
  precise, predictable contract for date-based filtering.
- **Alternatives considered**: Inclusive filtering was rejected because it would
  include tasks due exactly on the cutoff and would not match the specified
  “strictly before” behavior.

## Decision 4: Preserve the existing architecture

- **Decision**: Extend the existing Pydantic schemas, explicitly construct the
  task in the repository, add repository filtering, and expose the filter from
  the existing list route. Add no dependencies and keep in-memory storage.
- **Rationale**: This is the smallest design consistent with the repository
  convention and the constitution's backward-compatibility and dependency
  requirements.
- **Alternatives considered**: A new storage layer, external date service, or
  dependency was rejected because the feature does not require them and they
  would increase scope and compatibility risk.
