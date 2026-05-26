## Article M1 — Operational source safety comes first

Plans identify whether MySQL is a production OLTP source, replica, or analytics database. Heavy SQLMesh
work must not run against an unprotected production primary.

## Article M2 — Indexes and explain plans support every heavy model

Large joins and filters document required indexes and `EXPLAIN` evidence or expected plan behavior.
Views over heavy joins require a justification.

## Article M3 — Incremental loads avoid large locks

Incremental models document watermark, primary/unique key, batch size, and lock impact. Full refreshes
of large tables require an approved window.

## Article M4 — Engine, charset, collation, and timezone assumptions are visible

Plans call out InnoDB assumptions, collation-sensitive comparisons, and timezone/date handling when
they affect business logic.

## Article M5 — Grants and PII access are reviewed

Governed marts document schemas/databases, grants, serving views, and sensitive columns before
implementation.
