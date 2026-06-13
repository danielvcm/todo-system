# Feature Specification: Household Chore Tracker

**Feature Branch**: `001-household-chore-tracker`

**Created**: 2026-06-13

**Status**: Draft

**Input**: User description: "I want an web app to track me and my wife's house chores. I want to be able to set recurrent tasks and to set a due date or a due interval (like it can be completed from june 14th until june 17th). I'd also like to have a due today view, so I would not be overwhelmed by the backlog."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Due Today (Priority: P1)

As a household member, I want a focused "Due Today" view so I only see tasks I need to address today and am not overwhelmed by older backlog items.

**Why this priority**: Reduces cognitive load and makes daily chores actionable.

**Independent Test**: Open the app on a given date where tasks exist with various due ranges and recur patterns; confirm the Due Today view shows exactly those tasks whose due interval includes the date or whose recurrence yields an occurrence on that date.

**Acceptance Scenarios**:

1. **Given** several tasks (single-date, interval, recurring), **When** viewing "Due Today", **Then** only tasks applicable to today's date are listed.
2. **Given** a task with an interval (start = 2026-06-14, end = 2026-06-17), **When** date is 2026-06-16, **Then** the task appears in Due Today and can be completed.

---

### User Story 2 - Create Recurrent Task (Priority: P1)

As a household member, I want to create tasks that recur (daily, weekly, monthly, or custom) so I don't have to recreate routine chores.

**Why this priority**: Core time-saver and central to household chore management.

**Independent Test**: Create a recurring task with a simple rule (e.g., every Monday) and verify that occurrences are generated for future Mondays and the Due Today view includes them when appropriate.

**Acceptance Scenarios**:

1. **Given** a recurring task defined as "every Monday", **When** a Monday arrives, **Then** an occurrence is visible in Due Today or calendar views.

---

### User Story 3 - Flexible Due Interval (Priority: P2)

As a household member, I want to set a due interval (start and end) so a task can be completed anytime within a window rather than a single strict date.

**Why this priority**: Allows flexibility for chores that can be done anytime during a weekend or vacation window.

**Independent Test**: Create a task with a start and end date, confirm it appears in Due Today for each date in the inclusive range.

**Acceptance Scenarios**:

1. **Given** a task with interval 2026-06-14 → 2026-06-17, **When** on any date in that range, **Then** the task is listed as available to complete.

---

### Edge Cases

- Overlapping intervals and recurrence rules producing duplicate visible occurrences — system must dedupe display.
- Recurrence rules with exclusions or end-of-series dates.
- Timezone and DST edge cases for start/end boundaries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to create tasks with: title, optional description, optional assignee (household member), optional end due date OR optional due interval (filling in the start due date information), and optional recurrence rule.
- **FR-002**: System MUST support recurrence patterns: daily, weekly (by weekday), monthly (by day or by weekday-of-month), and custom interval-based recurrence (every N days/weeks/months).
- **FR-003**: System MUST allow setting a due interval where a task is considered "open" on every date from `start_due_date` through `end_due_date` inclusive.
- **FR-004**: System MUST provide a "Due Today" view that lists tasks with explicit due date equal to today, tasks whose interval includes today, and recurring tasks with an occurrence on today.
- **FR-005**: Users MUST be able to mark a task occurrence as completed; for recurring tasks the system MUST record the completion and schedule (or leave) the next occurrence according to the recurrence rule.
- **FR-006**: System MUST deduplicate occurrences so that a single actionable item is shown per task per date.
- **FR-007**: System MUST allow basic assignment to household members (name or identifier) and show assignee in lists and details.
- **FR-008**: System MUST allow viewing task history (completion records) and basic filtering (by assignee, by date, by recurrence).

*Resolved decision*:

- **FR-009**: System MUST support separate user logins with basic household membership and assignment permissions. Rationale: per-user authentication enables clear assignment, completion history per person, and accountability; chosen for MVP to allow distinct profiles for household members.

### Key Entities *(include if feature involves data)*

- **User**: household member identity; attributes: `id`, `name`, `display_name`, `ha_id` for the home assistant user id.
- **Task**: represents a chore template; attributes: `id`, `title`, `description`, `assignee_id` (nullable), `start_due_date` (for tasks with due interval, nullable), `end_due_date` (not nullable), `recurrence_rule` (nullable), `active`.
- **Occurrence**: a computed or persisted occurrence of a `Task` for a specific date; attributes: `task_id`, `date`, `status` (open/completed), `completed_at`.
- **RecurrenceRule**: structured recurrence specification: type, interval, byDay/byMonth, endDate (nullable).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with either a due date or a due interval and see it appear in appropriate views within one interaction.
- **SC-002**: Due Today view shows only items applicable to the current date; pass-rate: 100% for automated tests covering representative cases (single-date, interval, recurrence).
- **SC-003**: Recurring tasks generate occurrences for future dates according to the rule; automated tests validate at least 5 successive occurrences for common recurrence types.
- **SC-004**: Users can mark an occurrence complete and the completion is persisted and visible in history within one minute.

## Assumptions

- This feature targets a small household use case (1–6 members) for v1; scaling to large teams is out of scope for initial release.
- Notifications, rich reminders, mobile push, and external calendar integrations are out of scope for v1 and considered optional future work.
- Authentication model: MVP will use separate user logins with basic household membership and assignment permissions (per FR-009 resolved above).
- Timezones will be handled by storing dates in local household timezone; cross-household timezone sharing is out of scope for v1.

## Clarifications

### Session 2026-06-13

- Q: Which account model should the MVP use (shared household vs separate logins)? → A: Separate user logins with basic household membership and assignment permissions.

## Readiness

This spec is ready for planning. Core flows (create task, recurrence, due-interval, Due Today, complete occurrence) are fully specified with testable acceptance scenarios.
