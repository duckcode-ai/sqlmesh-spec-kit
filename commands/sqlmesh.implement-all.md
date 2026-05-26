# /sqlmesh.implement-all

Implement all tasks in `tasks.md` after `plan.md` is exactly `approved`.

Required loop:

1. Implement only approved file changes.
2. Run or document the project SQLMesh parse/test/audit commands.
3. Run `sqlmesh plan <env>` and inspect changed snapshots, backfill scope, restatement scope, and forward-only behavior.
4. Stop on failed tests/audits, unexpected plan output, unclear evidence, or files outside the approved plan.
5. Update task checkboxes only after evidence exists.
