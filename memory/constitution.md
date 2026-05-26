# sqlmesh-spec-kit Constitution

This file is durable project memory for AI-assisted SQLMesh development.

## Lifecycle

- `spec.md` status must be exactly `draft`, `approved`, `shipped`, or `superseded`.
- `plan.md` status must be exactly `proposed`, `approved`, or `superseded`.
- `tasks.md` status must be exactly `in progress` or `done`.
- `plan.md` may exist only after an approved or shipped spec.
- `tasks.md` may exist only after an approved plan.

## SQLMesh Evidence

- Approved plans identify target environment, changed models, snapshots, audits/tests, backfill scope, forward-only decision, restatement decision, and downstream impact.
- Implementations attach `sqlmesh plan <env>` evidence before review.
- Unexpected backfills, restatements, or forward-only changes require human review before continuing.

## Boundaries

- Agents implement only files listed in the approved plan.
- Every acceptance criterion must be traceable through plan, tasks, implementation, and evidence.
- Jira and Confluence publishing must redact secrets, credentials, customer data, and unnecessary PII.
