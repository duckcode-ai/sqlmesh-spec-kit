# 05: Jira to Spec Workflow

```bash
sqlmesh-specify jira pull DATA-123 --target .
sqlmesh-specify jira attach DATA-123 --spec specs/001-change/spec.md --plan specs/001-change/plan.md
sqlmesh-specify jira create-tasks DATA-123 --from specs/001-change/tasks.md --dry-run
```

Review and redact generated specs before attaching them back to Jira.
