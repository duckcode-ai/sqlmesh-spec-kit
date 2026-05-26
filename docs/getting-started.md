# Getting Started

## Install

```bash
uvx --from sqlmesh-spec-kit sqlmesh-specify --help
```

## Initialize a SQLMesh repo

Run from a SQLMesh project root with `config.yaml`, `config.yml`, or `config.py` and `models/`.

```bash
sqlmesh-specify init analytics --engine duckdb --target .
sqlmesh-specify doctor --target .
```

`init` writes `.sqlmesh-specify/`, `CLAUDE.md` or `CLAUDE.md.sqlmesh-specify-suggested`, and `specs/.gitkeep`.

## Validate

```bash
sqlmesh-specify validate path/to/spec.md
sqlmesh-specify validate project --target .
sqlmesh-specify validate sqlmesh --target .
sqlmesh-specify report --target . --format markdown
```

Status values are exact, not free-form prose. Use only the legal values shown in the templates.
