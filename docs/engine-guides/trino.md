# Trino guide for sqlmesh-spec-kit

## What `--engine trino` adds

`sqlmesh-specify init --engine trino` appends Trino-specific articles to the constitution and Trino-specific tables to the plan template.

**Trino is not a engine.** It's a federated query engine. The constitution and plan additions reflect that — concerns center on catalogs, connectors, federation, pushdown, and session properties, not on engines or clustering.

## What's covered

| Topic | Where |
|---|---|
| Three-part naming (`catalog.schema.table`) | Constitution Article T2 + plan additions |
| Federation and cross-catalog joins | Constitution Article T3 + plan additions + federated-query-patterns skill |
| Connector pushdown | Constitution Article T4 + plan additions + skill |
| Session properties | Constitution Article T5 + plan additions |
| `on_table_exists: rename / drop` | Constitution Article T6 + plan additions |
| View security (`definer` / `invoker`) | Constitution Article T7 + plan additions |
| Iceberg as preferred destination | Constitution Article T8 |
| Adapter cadence (Starburst-maintained) | Constitution Article T9 |
| Cost attribution | Constitution Article T10 + plan additions |

## Three-part naming — the single most common Trino-on-SQLMesh mistake

Always reference data with three parts:

```sql
SELECT * FROM iceberg.analytics.fct_orders;          -- right
SELECT * FROM postgresql.public.customers;           -- right
SELECT * FROM fct_orders;                            -- wrong: silent routing risk
```

The constitution enforces this. The plan template's catalog table makes every catalog touched visible.

## Federation — three good questions to ask before any cross-catalog join

1. **Should this join exist in Trino at all, or should one side be landed in Iceberg first?** Materializing the smaller side into Iceberg is often the right answer.
2. **What's the pushdown story?** Run `EXPLAIN (TYPE DISTRIBUTED)` and confirm the predicate appears in a `ScanFilterProject` node, not after the scan.
3. **What's the network cost?** Cross-catalog joins move data over the network. Estimate the rows pulled into Trino.

See `.sqlmesh-specify/skills/trino-federated-query-patterns/SKILL.md` for the full decision rules.

## Session properties — replacing "engine sizing"

Trino doesn't have Snowflake's named engines. Adjust execution behavior via session properties:

```yaml
# profiles.yml
my_SQLMesh_trino_project:
  target: prod
  outputs:
    prod:
      type: trino
      host: trino.example.com
      catalog: iceberg
      schema: analytics
      session_properties:
        query_max_run_time: '30m'
        query_max_memory: '4GB'
        task_concurrency: 8
```

Per-model overrides via `pre_hook`:

```python
{{ config(
    materialized='table',
    pre_hook=["set session query_max_run_time='10m'"]
) }}
```

## `on_table_exists` — choose deliberately, especially on Glue

```python
{{ config(
    materialized='table',
    on_table_exists='rename'   -- default; safer
) }}
```

But if your underlying metastore is AWS Glue and the target catalog is Hive-style:

```python
{{ config(
    materialized='table',
    on_table_exists='drop'     -- required; Glue cannot rename
) }}
```

Constitution Article T6 makes this an explicit choice in the plan, not a default-and-hope.

## View security

```python
{{ config(
    materialized='view',
    view_security='definer'    -- default; view runs as creator
) }}
```

Use `'invoker'` only when downstream users must be enforced against their own access controls. The plan declares the choice.

## Cost attribution (best-effort)

Trino has no native cost-tag mechanism. The viable patterns:

1. Set `application_name` or a custom session property at run time so queries are identifiable in coordinator logs.
2. Aggregate from coordinator query logs into an Iceberg table for analysis.
3. Attribute storage cost separately via the underlying connector's billing (Iceberg/S3 lifecycle policies).

The plan's "Cost attribution" table makes the chosen approach explicit.

## Composition with the lakehouse pattern

The most common Trino-on-SQLMesh deployment is the **lakehouse pattern**: Iceberg tables in S3 (or equivalent object store), Trino as the query engine, SQLMesh as the transformation layer. The constitution and plan additions assume this pattern as default but do not require it — non-Iceberg catalogs are supported with explicit annotation.
