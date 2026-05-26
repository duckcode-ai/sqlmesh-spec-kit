## Trino-specific concerns

### Catalogs and federation

| Catalog | Connector | Role in this work | Read / write |
|---|---|---|---|
| `iceberg` | Iceberg + S3 | destination for materialized models | read + write |
| `<source_catalog>` | <connector> | source data | read-only |

### Cross-catalog joins (Article T3)

| Model | Catalogs joined | Justification | Estimated rows moved over network |
|---|---|---|---|
| <model> | `<catalog_a>` × `<catalog_b>` | <why this join is necessary here and not earlier> | <estimate> |

If this table is empty, mark "none" — do not omit the table.

### Pushdown plan (Article T4)

| Model | Non-Iceberg sources | Predicates expected to push down | Verified via `EXPLAIN`? |
|---|---|---|---|
| <model> | `<catalog.schema.table>` | `<predicate_a>, <predicate_b>` | yes / no |

### Storage-format concerns

For each model materialized into an Iceberg-backed catalog:

| Model | Partitioning | File format | Compaction concerns |
|---|---|---|---|
| <model> | `<partition_spec>` (e.g., `day(event_ts)`) | parquet / orc | <how/when compaction runs> |

For non-Iceberg destinations, document the equivalent concerns for that table format.

### Session properties

| Property | Value | Justification |
|---|---|---|
| `query_max_run_time` | `<value>` | <why this differs from default> |
| `task_concurrency` | `<value>` | <why this differs from default> |

### Materialization choices

| Model | Materialization | `on_table_exists` | View security | Justification |
|---|---|---|---|---|
| <model> | table / view / incremental / materialized_view | rename / drop / n/a | definer / invoker / n/a | <why> |

### Cost attribution

| Risk | Mitigation |
|---|---|
| Cost of large cross-catalog scan invisible at review time | Add `EXPLAIN` output to the plan for any model with cross-catalog joins |
| Underlying connector (e.g., Hive on EMR) billed separately | Tag query via session property `application_name`; coordinator logs aggregated weekly |
