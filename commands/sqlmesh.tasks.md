# /sqlmesh.tasks

Create `tasks.md` only when `plan.md` status is exactly `approved`.

1. Convert the approved plan into bounded implementation tasks.
2. Include tasks for SQLMesh models, audits/tests, `sqlmesh plan dev`, and review evidence.
3. Add stop conditions for unclear plan output, unexpected backfill/restatement, failed audits/tests, or files outside plan.
4. Map every task to AC ids.
5. Set status to `in progress` until all tasks and evidence are complete.
