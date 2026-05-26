## Article P1 — Production analytics do not harm OLTP systems

Plans identify whether Postgres is an analytics engine, replica, or operational source. Heavy SQLMesh
models must run on an analytics-safe database or replica, not an unconstrained production OLTP
primary.

## Article P2 — Index and materialization choices are explicit

Tables, incremental models, and materialized views document indexes needed for joins, filters, and
refresh behavior. Views over expensive joins require a justification.

## Article P3 — Locking and transaction impact are reviewed

Plans for large table rebuilds, materialized view refreshes, or schema changes document lock risk and
deployment timing. Blocking production workloads is not acceptable without an approved window.

## Article P4 — Grants and schemas are part of the plan

Marts document schema ownership, grants, and whether access is through direct tables, views, or a
serving schema. Sensitive columns require an access decision.

## Article P5 — Extensions and non-portable SQL are called out

Use of Postgres-specific extensions, custom functions, JSON operators, or advanced indexes is named
in the plan with compatibility and maintenance expectations.
