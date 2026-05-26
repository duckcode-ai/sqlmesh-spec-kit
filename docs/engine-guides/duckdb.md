# DuckDB guide

Use this preset when SQLMesh targets DuckDB for local analytics, CI fixtures, or file-based workflows.

## What the preset adds

- local file and object-store path review
- memory and single-process limits
- DuckDB extension planning
- Parquet staging and export expectations
- governance handling for local files and CI artifacts

## Good fit

- local development examples
- lightweight analytics projects
- CI smoke tests with deterministic data files

## Use

```bash
sqlmesh-specify init analytics --engine duckdb
```

This preset is useful for AI-agent demos because it makes local file dependencies and reproducibility
explicit.
