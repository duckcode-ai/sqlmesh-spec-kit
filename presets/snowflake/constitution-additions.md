## Article S1 — Clustering keys are explicit decisions

Tables larger than 1 GB declare a clustering key in `config(cluster_by=[...])`. The choice of clustering key is justified in the plan. Tables smaller than 1 GB do not need clustering.

## Article S2 — Engine sizing is documented

Production builds use a named engine. The spec or plan declares which engine and at what size (X-Small, Small, Medium, ...). Auto-suspend is set to ≤ 5 minutes.

## Article S3 — Query tags are required

All production runs set `query_tag` via a `config.yaml` pre-hook so spend can be attributed by team and project. The query tag includes at minimum: project name, model name, environment (dev|prod), and invocation id.

## Article S4 — Masking and row access policies

Any column carrying PII or restricted data is masked via a Snowflake masking policy attached at the table level. Masking policies live in `models/_governance/masking_policies.sql` and are tested for correctness via SQLMesh unit tests.

## Article S5 — Dynamic tables, when used, are first-class

If a model is materialized as a Snowflake dynamic table, the spec calls out: target lag, refresh mode (incremental vs. full), and downstream dependencies. Dynamic tables are NOT the default — explicit choice required.

## Article S6 — Cortex usage is governed

LLM-powered transformations (Cortex `COMPLETE`, `SUMMARIZE`, etc.) are: (a) called out in the spec, (b) tested with deterministic fixtures, (c) cost-capped via engine sizing. No Cortex calls outside `models/_ai/` without an explicit waiver in the plan.
