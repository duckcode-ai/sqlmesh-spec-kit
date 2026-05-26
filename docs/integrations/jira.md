# Jira Integration

Set `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`.

```bash
sqlmesh-specify jira pull DATA-123 --target .
sqlmesh-specify jira attach DATA-123 --spec specs/001-change/spec.md
sqlmesh-specify jira create-tasks DATA-123 --from specs/001-change/tasks.md
sqlmesh-specify jira sync DATA-123 --spec-dir specs/001-change --dry-run
```

Generated specs mention SQLMesh models, audits, environments, and plan evidence. Redact sensitive context before syncing externally.
