# Postgres guide

Use this preset when SQLMesh targets Postgres or uses Postgres as an analytics-safe serving database.

## What the preset adds

- OLTP safety checks for primary versus replica versus analytics database
- index and materialization planning
- lock and transaction impact review
- schema/grant/access planning
- extension and non-portable SQL callouts

## Good fit

- smaller analytics projects on Postgres
- product analytics replicas
- local or self-managed SQLMesh deployments where lock safety matters

## Use

```bash
sqlmesh-specify init analytics --engine postgres
```

The preset does not connect to Postgres. SQLMesh and its adapter handle database execution.
