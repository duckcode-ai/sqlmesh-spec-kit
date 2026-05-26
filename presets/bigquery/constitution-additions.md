## Article B1 — Partitioning decisions are explicit

Large fact-like tables declare a partitioning strategy in the model config. Date or timestamp
partitioning is preferred when the model is queried by time range. Tables that are not partitioned
must justify that choice in the plan.

## Article B2 — Clustering supports the dominant access path

Cluster columns are chosen from high-cardinality filter or join columns. Clustering is documented in
the plan with the expected query pattern it supports.

## Article B3 — Cost guardrails are mandatory

Plans for large models document the expected scan boundary and require partition filters where
applicable. Queries must not rely on unbounded full-table scans for routine transformations.

## Article B4 — Materialized views and incremental models are deliberate choices

If the model can be represented as a BigQuery materialized view, the plan explains why that is or is
not the right choice. Hand-rolled incremental models document the unique key, partition filter, and
late-arriving data behavior.

## Article B5 — Governance lives in policy tags and authorized views

Columns carrying PII or restricted data use BigQuery policy tags or authorized views. The plan lists
the tag or view boundary and the test evidence for masked or restricted access.

## Article B6 — BI Engine and semantic consumers are called out

Models serving dashboards or semantic-layer metrics document whether BI Engine acceleration is
expected, unnecessary, or explicitly out of scope.
