# SQLMesh AI SDLC Walkthrough

Scenario: add a customer order segmentation model to a small sushi-style SQLMesh project.

1. Run `sqlmesh-specify init sushi --engine duckdb --target .`.
2. Draft `specs/001-customer-segmentation/spec.md`.
3. Approve the spec by setting `**Status:** approved`.
4. Write `plan.md` with changed models, audits/tests, backfill window, and SQLMesh plan evidence requirements.
5. Approve the plan by setting `**Status:** approved`.
6. Write `tasks.md`, implement only the approved files, and run:

```bash
sqlmesh plan dev
sqlmesh test
sqlmesh-specify report --target . --format markdown
```

7. Attach plan/test/audit evidence and mark the spec `shipped` after promotion.

See `examples/sushi-customer-segmentation/` for complete artifacts.
