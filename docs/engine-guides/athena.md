# Athena guide

Use this preset when SQLMesh targets Amazon Athena and S3-backed tables.

## What the preset adds

- S3 table and file-layout planning
- partitioning and partition-projection decisions
- Glue catalog and Lake Formation/IAM governance review
- workgroup, output location, and scan-cost guardrails
- Iceberg versus Hive-style table format decisions

## Good fit

- lakehouse tables queried through Athena
- Iceberg or external Hive-style datasets
- teams that need scan-cost and S3 layout evidence in PRs

## Use

```bash
sqlmesh-specify init analytics --engine athena
```

sqlmesh-spec-kit does not query Athena. SQLMesh, the adapter, AWS credentials, and workgroup configuration
remain outside this toolkit.
