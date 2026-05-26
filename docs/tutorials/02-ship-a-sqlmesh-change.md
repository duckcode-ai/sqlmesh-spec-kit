# 02: Ship a SQLMesh Change

Use the sushi customer segmentation example.

```bash
sqlmesh-specify validate specs/001-customer-segmentation/spec.md
sqlmesh-specify validate project --target .
sqlmesh plan dev
sqlmesh test
sqlmesh-specify report --target . --format markdown
```

Show how the spec becomes a plan, the plan becomes tasks, and SQLMesh plan/test evidence becomes review evidence.
