# Writing Incremental Model Specs

Use this when a SQLMesh change may affect incremental behavior.

Checklist:

- Define the incremental key, time column, late-arriving data policy, and backfill window.
- Call out forward-only changes and restatement risk.
- Require SQLMesh plan evidence that shows expected snapshot and backfill behavior.
- Add audits/tests for uniqueness, freshness, null handling, and boundary dates.
