# /sqlmesh.analyze

Analyze a SQLMesh repo or proposed change without editing files.

Report:

- SQLMesh config and model inventory
- missing audits/tests
- downstream model and semantic impact
- likely backfill/restatement risk
- gaps in spec, plan, tasks, or SQLMesh evidence

Useful commands:

```bash
sqlmesh-specify doctor --target .
sqlmesh-specify validate project --target .
sqlmesh-specify validate sqlmesh --target .
```
