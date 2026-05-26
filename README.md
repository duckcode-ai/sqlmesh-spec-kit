# sqlmesh-spec-kit

AI SDLC and durable memory for SQLMesh teams: specs are contracts, SQLMesh plans are deployment evidence, and agents implement only inside approved task boundaries.

## Install

```bash
uvx --from sqlmesh-spec-kit sqlmesh-specify --help
```

## Initialize

Run inside an existing SQLMesh project with `config.yaml`, `config.yml`, or `config.py` and a `models/` directory.

```bash
sqlmesh-specify init analytics --engine duckdb --target .
sqlmesh-specify doctor --target .
sqlmesh-specify validate project --target .
sqlmesh-specify validate sqlmesh --target .
sqlmesh-specify report --target . --format markdown
```

Supported engine presets: `duckdb`, `snowflake`, `databricks`, `bigquery`, `trino`, `redshift`, `postgres`, `mysql`, `mssql`, `athena`, `spark`, and `clickhouse`.

## Workflow

1. Draft `spec.md` with EARS acceptance criteria.
2. Human approves the spec by setting status exactly to `approved`.
3. Create `plan.md` with SQLMesh environment, changed models, audits/tests, backfill scope, forward-only/restatement decision, and plan/apply evidence expectations.
4. Human approves the plan by setting status exactly to `approved`.
5. Create `tasks.md` and implement only approved files.
6. Review final diff against `spec.md`, `plan.md`, `tasks.md`, and SQLMesh plan/audit/test evidence.

Validators do not execute SQLMesh in v0.1. Run `sqlmesh plan <env>`, tests, and audits in your project workflow and attach the evidence to the spec directory or PR.

## CLI

```bash
sqlmesh-specify init <project-name> --engine <engine> --target . [--force]
sqlmesh-specify doctor --target .
sqlmesh-specify validate <path/to/spec.md>
sqlmesh-specify validate project --target .
sqlmesh-specify validate sqlmesh --target .
sqlmesh-specify report --target . --format markdown
sqlmesh-specify ci --target .
sqlmesh-specify jira pull|attach|create-tasks|sync
sqlmesh-specify confluence pull-page|publish|sync
```

## Docs

- [Getting started](docs/getting-started.md)
- [Methodology](docs/methodology.md)
- [Enterprise CI](docs/enterprise-ci.md)
- [SQLMesh AI SDLC walkthrough](docs/sqlmesh-ai-sdlc-walkthrough.md)
- [Memory and repo hygiene](docs/sqlmesh-memory-and-repo-hygiene.md)
- [Tutorials](docs/tutorials/README.md)
- [Roadmap](ROADMAP.md)
