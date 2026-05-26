# Databricks guide for sqlmesh-spec-kit

## What `--engine databricks` adds

`sqlmesh-specify init --engine databricks` appends Databricks-specific articles to the constitution and Databricks-specific tables to the plan template. The wedge is the same as for Snowflake: engine-specific patterns SQLMesh Labs intentionally doesn't ship.

## What's covered

| Topic | Where |
|---|---|
| Liquid Clustering | Constitution Article D1 + plan additions + clustering-decisions skill |
| Photon | Constitution Article D2 + plan additions |
| Unity Catalog | Constitution Article D3 + plan additions |
| Materialized Views | Constitution Article D4 |
| Query tags via system tables | Constitution Article D5 |
| AI/ML governance (`ai_query`, Mosaic AI) | Constitution Article D6 |

## Liquid Clustering — the modern default

Liquid Clustering replaces rigid partitioning. Use the `databricks-liquid-clustering-decisions` skill for the decision rules. Short version:

- Use Liquid Clustering for tables >1 GB with selective query predicates
- One column is usually enough; up to 4 supported
- Compose with Predictive Optimization at the schema level

```sql
ALTER SCHEMA <catalog>.<schema> ENABLE PREDICTIVE OPTIMIZATION;
```

## Unity Catalog placement

All models use three-part names:

```sql
{{ config(
    materialized='table',
    catalog='analytics',
    schema='marts'
) }}
```

Grants live in `models/_governance/grants.sql` and apply as a post-hook:

```yaml
on-run-end:
  - "{{ apply_grants() }}"
```

## Materialized Views over hand-rolled incrementals

Where the engine supports it, prefer:

```python
{{ config(materialized='materialized_view') }}
```

Over:

```python
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='sync_all_columns'
) }}
```

The plan must justify any choice of `incremental` over `materialized_view`.

## Query tags via system tables

Databricks doesn't have inline `query_tag` like Snowflake. Use SQL engine tags + `system.access.audit`:

```sql
SELECT
  request_params:statement AS sql,
  request_params:engine_id AS engine,
  request_params:statement_id AS statement_id
FROM system.access.audit
WHERE service_name = 'databrickssql'
  AND date_trunc('day', event_time) = current_date();
```

Pair with workspace-level tags applied to the engine for full attribution.
