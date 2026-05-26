# /sqlmesh.plan

Create `plan.md` only when `spec.md` status is exactly `approved` or `shipped`.

1. Read `spec.md`, `.sqlmesh-specify/constitution.md`, and engine additions.
2. Identify target SQLMesh environment, changed models, snapshots, audits, tests, backfill window, and downstream impact.
3. List every file to add, modify, or delete.
4. Map every planned change and test to AC ids.
5. Include the `sqlmesh plan <env>` command that must be run and the evidence reviewers need.
6. Set status to `proposed` until a human approves it.
