## Athena-specific concerns

### Table and file layout

| Model | Table format | File format/size | Small-file risk |
|---|---|---|---|
| <model> | Iceberg / Hive external | Parquet/ORC/other, <MB> | low/medium/high |

### Partitioning and pruning

| Model | Partition columns | Projection used? | Expected scan boundary |
|---|---|---|---|
| <model> | <cols> | yes/no | <predicate> |

### Governance

| Output | Glue database/table | Lake Formation/IAM boundary | Sensitive? |
|---|---|---|---|
| <model> | <db.table> | <policy/role> | yes/no |

### Workgroup and cost

| Job | Workgroup | Output location | Scan guardrail |
|---|---|---|---|
| <job> | <workgroup> | s3://... | <limit/mitigation> |
