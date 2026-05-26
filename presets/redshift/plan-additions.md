## Redshift-specific concerns

### Distribution and sort decisions

| Model | Size estimate | Dist style/key | Sort key | Justification |
|---|---|---|---|---|
| <model> | <GB/rows> | AUTO / KEY(`<col>`) / EVEN / ALL | `<col>` or none | <why> |

### Maintenance expectations

| Model | Load pattern | Vacuum needed? | Analyze needed? | Owner |
|---|---|---|---|---|
| <model> | full / incremental / append | yes/no | yes/no | SQLMesh / platform |

### External and Spectrum access

| Source | Partition boundary | File layout risk | Mitigation |
|---|---|---|---|
| <external source> | <partition predicate> | small files / unbounded scan | <plan> |

### Workload and cost guardrails

| Job | Queue/workload | Full-refresh risk | Guardrail |
|---|---|---|---|
| <job> | <queue> | low/medium/high | <mitigation> |
