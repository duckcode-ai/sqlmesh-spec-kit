## Databricks-specific concerns

### Liquid Clustering decisions

| Model | Size estimate | Clustering key | Justification |
|---|---|---|---|
| <model> | <GB> | `<col>` or none | <why> |

### Materialization choice

| Model | Materialization | Justification |
|---|---|---|
| <model> | view / table / materialized_view / streaming_table | <why this and not an MV> |

### Unity Catalog placement

| Model | Catalog | Schema | Grants |
|---|---|---|---|
| <model> | <catalog> | <schema> | `_governance/grants.sql` entry: <line ref> |

### Photon compatibility

| Model | Photon-compatible? | If no, why |
|---|---|---|
| <model> | yes / no | <reason> |

### Cost guardrails

| Risk | Mitigation |
|---|---|
| Predictive Optimization not enabled on changed tables | Verify via `DESCRIBE TABLE EXTENDED` after first build |
| Streaming Table without watermark | Plan declares watermark column explicitly |
