# Methodology

sqlmesh-spec-kit treats AI SDLC artifacts as durable repo memory.

## Spec

`spec.md` is the contract. It describes the problem, users, SQLMesh-facing constraints, and EARS acceptance criteria. A plan may exist only when the spec status is exactly `approved` or `shipped`.

## Plan

`plan.md` is the implementation boundary. It names target environment, changed models, snapshots, audits/tests, backfill window, forward-only/restatement decision, downstream impact, and required SQLMesh evidence. Tasks may exist only when the plan status is exactly `approved`.

## Tasks

`tasks.md` is the bounded implementation checklist. Agents implement only approved files and stop when SQLMesh plan output, audit/test results, or AC traceability is unclear.

## Evidence

The v0.1 validators do not execute SQLMesh. Teams run `sqlmesh plan <env>`, SQLMesh tests, audits, apply, and promote commands in their normal workflow and attach evidence to the PR or spec directory.
