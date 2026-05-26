# 03: Brownfield Enterprise Adoption

Start with diagnostics, not a rewrite.

```bash
sqlmesh-specify doctor --target .
sqlmesh-specify init analytics --engine snowflake --target .
```

Capture only conventions that affect future AI-assisted changes: environment strategy, model ownership, audit/test expectations, and promotion evidence.
