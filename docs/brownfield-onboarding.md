# Brownfield Onboarding

1. Run `sqlmesh-specify doctor --target .`.
2. Initialize with the closest engine preset:

```bash
sqlmesh-specify init analytics --engine snowflake --target .
```

3. Capture existing conventions in `.sqlmesh-specify/constitution.md` or skills.
4. Start new work under `specs/<NNN>-<slug>/`; do not retroactively force every old model into a spec.
