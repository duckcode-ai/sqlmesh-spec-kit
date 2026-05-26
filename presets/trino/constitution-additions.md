## Article T1 — Trino is a query engine, not a engine

Models built on Trino are not "stored in Trino." Storage lives in the underlying connector (Iceberg, Delta, Hive, Postgres, Kafka, etc.). Spec and plan documents declare both the **catalog** (= connector + storage) and any storage-format concerns for that catalog. Storage decisions (partitioning, file size, table format options) belong in plan-additions sections aligned to the catalog used.

## Article T2 — Three-part naming is mandatory

All references use three-part names: `<catalog>.<schema>.<table>`. Two-part references are forbidden, even when the default catalog is set. Reason: silent routing to the wrong catalog is one of the most common Trino-on-SQLMesh failure modes, and three-part names make every cross-catalog join visible at code-review time.

## Article T3 — Cross-catalog joins are deliberate, never accidental

Any model that joins across two or more catalogs is called out in the spec's "Constraints" section AND in the plan's "Federation impact" table. Cross-catalog joins move data over the network and the cost model is opaque. Reviewers reject plans that introduce cross-catalog joins without explicit justification.

## Article T4 — Connector pushdown is a planning concern, not a runtime hope

For every model that filters or aggregates on a non-Iceberg-native catalog (Postgres, MySQL, Hive with Glue, Kafka), the plan declares **which predicates are expected to push down** and how this was verified (via `EXPLAIN`). Models that scan an entire underlying table because pushdown silently failed are a Constitution §11 violation (silent breaking change to performance contract).

## Article T5 — Session properties replace engine sizing

Trino has no equivalent of Snowflake's named engines or Databricks's compute clusters at the per-query level. Session properties (`query_max_run_time`, `query_max_memory`, `task_concurrency`, etc.) are set via `session_properties` in `profiles.yml` or `pre_hook` for one-off overrides. The plan declares non-default session properties.

## Article T6 — `on_table_exists` is an explicit choice

SQLMesh-trino's table materialization supports two modes: `rename` (default) and `drop`. Plans for table-materialized models declare which mode applies, especially where the AWS Glue Metastore is the backend (Glue cannot rename — `drop` is required there).

## Article T7 — View security is declared

View materializations declare `view_security` as either `definer` (default — view runs as its creator) or `invoker` (runs as the caller). The default is fine for most cases; specs that require `invoker` semantics call this out explicitly because the downstream access pattern changes.

## Article T8 — Iceberg is the preferred destination format

When the destination catalog is configurable, models materialize into an Iceberg-backed catalog rather than Hive or external relational connectors. Reasons: Iceberg supports time travel, hidden partitioning, schema evolution, and works cleanly with SQLMesh's incremental materializations. Plans that materialize into Hive or relational backends justify the choice (often: legacy constraint).

## Article T9 — Adapter is community-maintained

`SQLMesh-trino` is maintained by Starburst, not by SQLMesh Labs. Adapter-specific concerns (new features, breaking changes, version pinning) follow the SQLMesh-trino release cadence, not SQLMesh-core's. The `dependencies.yml` of any project using this preset pins `SQLMesh-trino` to a known-good minor version range.

## Article T10 — Cost attribution is best-effort

Trino has no native query-tag-and-bill mechanism. Cost attribution depends on (a) session properties that include identifying tags, (b) log aggregation from coordinator-side query logs, and (c) connector-side billing for the underlying storage. Specs and plans note when cost attribution matters and how it will be achieved for this specific work.
