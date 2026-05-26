# Tasks: <Feature Name>

**Author:** <name>
**Date:** <YYYY-MM-DD>
**Status:** in progress
**Plan:** <relative path to plan.md>

Status must be exactly one of: `in progress`, `done`.

## Task list

- [ ] T-01 - Update SQLMesh models named in the approved plan.
  - **Validates:** AC1
- [ ] T-02 - Add or update SQLMesh audits and tests.
  - **Validates:** AC2
- [ ] T-03 - Run `sqlmesh plan dev` and capture plan output.
  - **Validates:** AC1, AC2
- [ ] T-04 - Run SQLMesh tests/audits and attach evidence.
  - **Validates:** AC1, AC2
- [ ] T-05 - Compare final diff to spec.md, plan.md, tasks.md, and SQLMesh evidence.
  - **Validates:** AC1, AC2, AC3

## Stop Conditions

- The SQLMesh plan shows unexpected backfill, restatement, or forward-only behavior.
- SQLMesh tests or audits fail.
- Implementation requires files outside the approved plan.
- Acceptance criteria are unclear or untraceable.
