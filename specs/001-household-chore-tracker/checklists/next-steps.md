# Next Steps Checklist (Requirements Quality)

**Purpose**: Ensure the specification, data model, contracts, and deployment plan are complete, clear, and measurable prior to implementation. This checklist tests the written artifacts (not the implementation) and surfaces gaps that become concrete next steps.

**Created**: 2026-06-13
**Feature**: specs/001-household-chore-tracker/spec.md

## Requirement Completeness

- [ ] CHK001 - Are storage location, backup, and migration requirements for the SQLite database explicitly specified? [Completeness, Spec §Assumptions, Gap]
- [ ] CHK002 - Is the recurrence rule format (JSON vs RRULE) selected and documented for all recurrence-related requirements? [Clarity, Spec §FR-002, Gap]
- [ ] CHK003 - Are deduplication requirements for overlapping intervals and recurrence-produced duplicates specified with expected behavior? [Completeness, Spec §Edge Cases]

## Requirement Clarity

- [ ] CHK004 - Is the "Due Today" inclusion logic (timezones, inclusive/exclusive bounds) precisely defined and traceable to examples? [Clarity, Spec §FR-004]
- [ ] CHK005 - Is the behavior for completing a recurring occurrence (e.g., whether an occurrence is generated or skipped) explicitly described? [Clarity, Spec §FR-005]

## Acceptance Criteria Quality

- [ ] CHK006 - Are success criteria measurable and mapped to concrete examples (e.g., sample recurrence instances and expected Due Today results)? [Measurability, Spec §Success Criteria]
- [ ] CHK007 - Are performance expectations for DB operations and UI responsiveness stated for the household scale (1–6 members)? [Acceptance Criteria, Spec §Success Criteria]

## Scenario & Edge Case Coverage

- [ ] CHK008 - Are time zone and DST edge cases specified for start/end boundaries and recurring occurrences? [Edge Case, Spec §Edge Cases]
- [ ] CHK009 - Are intended behaviors for deleted or archived tasks documented (impact on past occurrences and history)? [Coverage, Spec §FR-008]

## Non-Functional Requirements

- [ ] CHK010 - Are security, privacy, and access-control requirements for the HA-embedded panel and services documented (who may call services, UI visibility)? [Non-Functional, Spec §Assumptions]
- [ ] CHK011 - Are operational constraints (no external servers, DB path under `/config`, backup recommendations) explicitly documented for deployment? [Non-Functional, Spec §Constraints]

## Dependencies & Assumptions

- [ ] CHK012 - Are assumptions about Pyscript capabilities (e.g., `sqlite3` availability, file access) and HA permissions recorded and validated? [Assumption, Spec §Assumptions]
- [ ] CHK013 - Are integration points with HA (service names, events, panel_custom configuration) specified in `contracts/services.md` and linked from the plan? [Consistency, Spec §Contracts]

## Ambiguities & Conflicts

- [ ] CHK014 - Are any ambiguous terms ("prominent", "fast", "near real-time") quantified or replaced with measurable thresholds? [Ambiguity, Spec §Success Criteria]

## Implementation Readiness (Traceability)

- [ ] CHK015 - Is a minimal migration plan and `schema_version` approach documented in `data-model.md` for safe upgrades? [Traceability, data-model.md]
- [ ] CHK016 - Are explicit acceptance test examples (dates, recurrence rules, expected visible occurrences) documented in `quickstart.md` or `tests/` to serve as concrete validation steps? [Coverage, quickstart.md]
