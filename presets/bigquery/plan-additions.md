## BigQuery-specific concerns

### Partitioning and clustering decisions

| Model | Size estimate | Partitioning | Clustering | Justification |
|---|---|---|---|---|
| <model> | <GB/TB> | `<date_col>` or none | `[col1, col2]` or none | <why> |

### Cost guardrails

| Model/job | Scan boundary | Guardrail | Tested? |
|---|---|---|---|
| <model> | <partition/date predicate> | require partition filter / incremental predicate | yes/no |

### Materialization strategy

| Model | Materialization | Alternative considered | Why this choice |
|---|---|---|---|
| <model> | table / incremental / materialized_view / view | <alternative> | <why> |

### Policy tags and authorized views

| Column/view | Source | Policy tag or authorized view | Tested? |
|---|---|---|---|
| <col> | <source.table.col> | <policy_tag_or_view> | yes/no |

### BI Engine and semantic consumers

| Consumer | BI Engine expected? | Impact |
|---|---|---|
| <dashboard/metric> | yes/no | <latency/cost expectation> |
