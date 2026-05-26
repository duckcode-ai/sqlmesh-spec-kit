# Getting Started

## Install

After the first PyPI release:

```bash
uvx --from sqlmesh-spec-kit sqlmesh-specify --help
```

Before PyPI release, install directly from GitHub:

```bash
uvx --from git+https://github.com/duckcode-ai/sqlmesh-spec-kit.git sqlmesh-specify --help
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

## Try the Verified Example

Use SQLMesh's official sushi example as the quickest end-to-end test target:

```bash
git clone https://github.com/TobikoData/sqlmesh-examples.git
cd sqlmesh-examples/001_sushi/2_moderate
uvx --from git+https://github.com/duckcode-ai/sqlmesh-spec-kit.git sqlmesh-specify init sushi-moderate --engine duckdb --target .
uvx --from git+https://github.com/duckcode-ai/sqlmesh-spec-kit.git sqlmesh-specify ci --target .
```

The full implementation flow is documented in [Tutorial 02: Ship a SQLMesh Change](tutorials/02-ship-a-sqlmesh-change.md).
