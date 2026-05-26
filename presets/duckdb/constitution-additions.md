## Article D1 — Local file boundaries are explicit

Plans name every local file, object-store path, or external source read by DuckDB models. Paths must
be reproducible for CI or clearly marked local-only.

## Article D2 — Memory and single-process limits are respected

Large transformations document expected input size, memory risk, and whether data should be staged as
Parquet before downstream models consume it.

## Article D3 — Extensions are deliberate dependencies

Use of DuckDB extensions such as httpfs, spatial, iceberg, or json is named in the plan with install
and CI expectations.

## Article D4 — Outputs are portable or intentionally local

Plans say whether outputs are local development artifacts, CI artifacts, Parquet exports, or inputs
to another engine. Local-only marts are not presented as enterprise serving tables.

## Article D5 — Governance still applies to files

PII in local files, Parquet exports, or CI artifacts requires masking, exclusion, or an explicit
handling decision.
