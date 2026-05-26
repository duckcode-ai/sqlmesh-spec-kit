# EARS cheatsheet — testable acceptance criteria for SQLMesh specs

EARS = **Easy Approach to Requirements Syntax**. Five patterns. Every AC in every spec uses one.

## The five patterns

### 1. Ubiquitous — always true

> The system shall <response>.

Use for invariants. The thing is always required, no triggering condition.

**SQLMesh examples:**
- The system shall produce a model named `dim_customers`.
- The system shall enforce `unique` and `not_null` on `customer_sk`.

### 2. Event-driven — triggered by an event

> When <trigger>, the system shall <response>.

Use for "when X happens, do Y."

**SQLMesh examples:**
- When `SQLMesh run` completes, the system shall write a `query_tag` to the audit table.
- When a source row arrives more than 7 days late, the system shall reject it.

### 3. State-driven — true while a state holds

> While <state>, the system shall <response>.

Use for ongoing conditions.

**SQLMesh examples:**
- While the model is materialized as an incremental, the system shall use a `unique_key` of `<col>`.
- While the engine is paused, the system shall not trigger refreshes.

### 4. Unwanted condition — error handling

> If <unwanted>, then the system shall <response>.

Use for failure modes.

**SQLMesh examples:**
- If a source row has `is_test = true`, then the system shall exclude it from the staging output.
- If `SQLMesh parse` fails, then the system shall not deploy.

### 5. Optional — feature-flagged

> Where <feature>, the system shall <response>.

Use for behavior that's conditional on configuration.

**SQLMesh examples:**
- Where Snowflake is the engine, the system shall apply the `mask_email` policy to PII columns.
- Where the semantic layer is enabled, the system shall preserve `<col>` with stable name and type.

## Anti-patterns

- "It should probably work" — not EARS. Not testable.
- "We want a fast model" — not EARS. Define "fast" as a measurable AC.
- "The user can do X" — not EARS. Reword as "When the user does Y, the system shall X."

## Validating

```bash
sqlmesh-specify validate specs/<NNN>-<slug>/spec.md
```

Exits 0 if all AC lines match one of the five patterns. Exits 1 with a list of non-conformant lines otherwise.
