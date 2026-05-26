## Article A1 — S3 file layout is part of model design

Athena models document table format, file format, target file size, and small-file risk. Plans for
large tables explain how files are compacted or kept query-efficient.

## Article A2 — Partitioning and projection are explicit

Large fact-like tables document partition columns, partition projection usage, and expected partition
pruning. Unpartitioned large scans require an approved justification.

## Article A3 — Glue and Lake Formation governance is reviewed

Plans identify Glue catalog/database/table ownership and Lake Formation or IAM access boundaries for
governed outputs.

## Article A4 — Workgroups and query cost guardrails are required

Plans name the Athena workgroup, expected scanned data, output location, and cost guardrails for
large models.

## Article A5 — Iceberg versus Hive table format is deliberate

Plans choose Iceberg, Hive-style external tables, or another format deliberately and document
incremental, compaction, and schema evolution behavior.
