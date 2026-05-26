# /sqlmesh.review

Review a completed SQLMesh change.

Compare:

1. final diff
2. `spec.md`
3. `plan.md`
4. `tasks.md`
5. SQLMesh plan/audit/test evidence

Block when:

- final files are outside the approved plan
- an AC lacks implementation or evidence
- `sqlmesh plan <env>` shows unexpected backfill, restatement, or forward-only behavior
- audits/tests failed or are missing
- downstream impact is undocumented
