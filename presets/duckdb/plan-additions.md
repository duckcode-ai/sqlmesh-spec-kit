## DuckDB-specific concerns

### File and source boundaries

| Input/output | Location | Reproducible in CI? | Notes |
|---|---|---|---|
| <path/source> | local / object storage / generated | yes/no | <notes> |

### Memory and data size

| Model | Input size estimate | Memory risk | Mitigation |
|---|---|---|---|
| <model> | <rows/GB> | low/medium/high | <plan> |

### Extensions

| Extension | Why needed | CI install covered? |
|---|---|---|
| <extension> | <reason> | yes/no |

### Governance for file outputs

| File/model | Sensitive data? | Handling decision |
|---|---|---|
| <output> | yes/no | mask / exclude / approved |
