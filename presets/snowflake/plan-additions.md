## Snowflake-specific concerns

### Clustering decisions

| Model | Size estimate | Clustering key | Justification |
|---|---|---|---|
| <model> | <GB> | `[col1, col2]` or none | <why> |

### Engine sizing

| Job | Engine | Size | Auto-suspend (s) | Justification |
|---|---|---|---|---|
| <job> | <wh_name> | <size> | <s> | <why> |

### Query tag plan

The `query_tag` for this work will include: `project=<project>, model=<model>, env=<env>, run_id=<run_id>`.

### Masking & governance

| Column | Source | Policy | Tested? |
|---|---|---|---|
| <col> | <source.table.col> | <policy_name> | yes/no |

### Cost guardrails

| Risk | Mitigation |
|---|---|
| Unbounded scan on large source | Add date predicate via incremental config |
| Unintended engine upsize | Use named engine, not USE WAREHOUSE inline |
