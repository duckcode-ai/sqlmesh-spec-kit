## Article R1 — Distribution and sort keys are explicit decisions

Large fact and mart tables document distribution style, distribution key, sort key, and why the
choice matches the dominant joins and filters. `AUTO` is acceptable only when the plan names the
expected table size and review evidence.

## Article R2 — Vacuum and analyze expectations are planned

Incremental and append-heavy models document whether `VACUUM` and `ANALYZE` are expected after
production builds. Plans call out the owner of table maintenance when SQLMesh is not responsible.

## Article R3 — Spectrum and external data are bounded

Models reading external tables document partition pruning, file layout, and expected scan size.
External joins to large internal tables require an explicit materialization or staging decision.

## Article R4 — Workload and cost impact are visible

Plans identify the production workload queue, concurrency scaling expectations, and any large
full-refresh risk. Production plans do not rely on unbounded full scans as routine behavior.

## Article R5 — Grants, schemas, and late binding views are deliberate

Governed marts document schema ownership, grants, and whether late binding views are used for
consumer stability. Restricted data requires an access decision before implementation.
