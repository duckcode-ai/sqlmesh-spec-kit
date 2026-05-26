# BigQuery guide

The BigQuery preset adds planning requirements for partitioning, clustering, materialization, cost,
policy tags, authorized views, and BI Engine expectations.

Use it with:

```bash
sqlmesh-specify init analytics --engine bigquery
```

## Partitioning

Large fact-like tables should partition by the date or timestamp column that bounds routine
production scans. If the model is not partitioned, document the size estimate and why partitioning is
not useful.

```sql
{{ config(
    materialized='incremental',
    partition_by={"field": "event_date", "data_type": "date"},
    cluster_by=["customer_id", "region"]
) }}
```

## Cost guardrails

Plans for large tables should name the normal scan boundary. Incremental models should document the
incremental predicate, unique key, and late-arriving data behavior.

## Governance

Restricted columns should use BigQuery policy tags or be exposed through authorized views. The plan
should list the protected column or view and how access behavior is tested.

## Semantic consumers

If a model supports dashboards or semantic-layer metrics, call out whether BI Engine acceleration is
expected, unnecessary, or out of scope.
