# <Feature Name>

**Author:** <name>
**Date:** <YYYY-MM-DD>
**Status:** draft

Status must be exactly one of: `draft`, `approved`, `shipped`, `superseded`.

## Problem

<Describe the business or data problem.>

## Users

| User | Job to be done |
|---|---|
| <persona> | <job> |

## What this is

<Describe the outcome without prescribing implementation.>

## Acceptance Criteria

<!-- Comments are allowed here. Every real line below must be one EARS requirement. -->

- AC1: When <event>, the system shall <required response>.
- AC2: If <precondition>, then the system shall <required response>.
- AC3: Where <feature/context>, the system shall <required response>.

## Out of Scope

- <Explicitly excluded work>

## Constraints

- SQLMesh environment: <dev|staging|prod>
- Affected models: <model names>
- Grain: <one row means ...>
- Audits/tests expected: <audit/test summary>
- Downstream consumers: <dashboards, exports, ML features, semantic layer>

## Open Questions

- [ ] <Question requiring human approval>
