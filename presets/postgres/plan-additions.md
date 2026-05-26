## Postgres-specific concerns

### OLTP safety

| Model/source | Database role | Workload risk | Mitigation |
|---|---|---|---|
| <model/source> | analytics / replica / primary | low/medium/high | <plan> |

### Index and materialization plan

| Model | Materialization | Indexes | Refresh/load behavior |
|---|---|---|---|
| <model> | view / table / incremental / materialized view | `<cols>` or none | <behavior> |

### Locking and deployment

| Change | Lock risk | Deployment window needed? | Mitigation |
|---|---|---|---|
| <change> | low/medium/high | yes/no | <plan> |

### Grants and schemas

| Output | Schema | Grant/access path | Sensitive columns |
|---|---|---|---|
| <model> | <schema> | table / view / role | <columns or none> |
