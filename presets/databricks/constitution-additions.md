## Article D1 — Liquid Clustering, not partitioning

New tables use Liquid Clustering (`CLUSTER BY (col)`), not rigid partition columns. The clustering column is declared in `config(liquid_clustered_by=[...])`. Tables migrated from partitioning to Liquid Clustering call out the migration in the plan.

## Article D2 — Photon is the default execution engine

Production engines use Photon. The spec or plan calls out any model that *must* run on classic compute (e.g., uses a UDF Photon doesn't support).

## Article D3 — Unity Catalog is the governance layer

All models are addressed via three-part names: `<catalog>.<schema>.<model>`. Grants are declared in `_governance/grants.sql` and applied as post-hooks. Hive metastore is not used for new work.

## Article D4 — Materialized Views for incremental work

For incremental processing, prefer Materialized Views (`materialized='materialized_view'`) over hand-rolled incremental SQLMesh models when the engine supports them. Specs that propose `materialized='incremental'` justify why an MV won't work.

## Article D5 — Query tags via system tables

Cost attribution uses Databricks query tags written to `system.access.audit`. The tag schema mirrors Snowflake's: `project`, `model`, `env`, `run_id`.

## Article D6 — AI/ML governance

LLM calls via `ai_query()` or Mosaic AI endpoints are: (a) called out in the spec, (b) tested with deterministic fixtures, (c) governed by per-endpoint cost limits.
