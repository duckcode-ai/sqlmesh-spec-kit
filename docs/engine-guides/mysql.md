# MySQL guide

Use this preset when SQLMesh reads from or writes to MySQL and operational safety matters.

## What the preset adds

- primary versus replica versus analytics database review
- index and `EXPLAIN` expectations for heavy joins
- incremental watermark, batch size, and lock planning
- engine, charset, collation, and timezone assumptions
- grants and PII access review

## Good fit

- operational-source staging projects
- MySQL replicas used for analytics
- teams that need to prevent AI agents from overloading OLTP databases

## Use

```bash
sqlmesh-specify init analytics --engine mysql
```

sqlmesh-spec-kit does not run MySQL queries. SQLMesh and the selected adapter own execution.
