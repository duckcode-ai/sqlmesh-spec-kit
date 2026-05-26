## MySQL-specific concerns

### Operational safety

| Source/model | Database role | Lock/load risk | Mitigation |
|---|---|---|---|
| <source/model> | primary / replica / analytics | low/medium/high | <plan> |

### Index and query plan

| Model/query | Required indexes | EXPLAIN expected? | Notes |
|---|---|---|---|
| <model> | <cols> | yes/no | <plan> |

### Incremental strategy

| Model | Watermark/key | Batch size | Full-refresh window |
|---|---|---|---|
| <model> | <col/key> | <rows/time> | <window or none> |

### Compatibility assumptions

| Area | Assumption | Risk |
|---|---|---|
| engine/charset/collation/timezone | <assumption> | <risk> |
