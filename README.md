# yourtrainer-mcp

A self-hosted Model Context Protocol (MCP) server giving any MCP-aware LLM the reference material and computational tools to work with indoor-cycling data: workout formats, route formats, activity files, training-load math, pacing, library operations.

**Endpoint**: `mcp.your-applications.com/your-trainer`

Maintained alongside [Your Trainer](https://www.your-applications.com/your-trainer/), an indoor-cycling app for Android tablets.

## What it does

Two layers:

### Knowledge registry
Structured documentation for the cycling-format ecosystem: ZWO, ERG/MRC, FIT (workout + activity), GPX, TCX, KML, `.ytw`, locale string-bundles. Per-format spec, ≥3 canonical examples, constraints catalogue (per-app limits), conversion notes, glossary. LLMs query the registry as authoritative reference when doing format conversions themselves.

### Capability tools
The operations LLMs can't reliably do alone:
- Binary FIT read/write (workout + activity)
- Time-series math (NP/IF/TSS, peak power curves, CTL/ATL/TSB, HR–power decoupling, FTP detection, Power Duration Curve fitting)
- Structured-intent workout authoring (deterministic ZWO + FIT + `.ytw` from JSON brief)
- Workout decomposition (file → structured intent — symmetric to the builder)
- Workout scaling (duration / FTP / intensity)
- Lap / interval auto-detection on unstructured activities
- App-acceptance checker (will this workout load on Garmin Edge / Zwift / TR / …)
- Workout structure linter (domain-aware static analysis)
- Plan-vs-actual adherence scorecard
- Pacing strategy generator (GPX route + FTP → per-segment targets)
- Climb analysis on a GPX route
- Activity privacy / anonymisation
- Library migration helper, deduplication, indexing, statistics
- Roundtrip test harness (lets agents self-correct conversions)
- Batch operations adapter
- Plus more capability tools — see `docs/features/`

## Stateless by design
- No accounts, no per-user state, no usage telemetry.
- Every tool call is independent; files are processed in memory and discarded.
- Operational health metrics aggregate only.
- No OAuth-mediated integrations (Strava pull, Garmin Connect, etc.). Users export their files; the MCP processes them.

## Status
**Scaffolding phase**. The project-os under `docs/` describes the planned scope (6 features, 50+ tasks). Code lands as the phase is executed.

## Project-os structure
- `SNAPSHOT.yaml` — canonical machine-readable state.
- `docs/phases/` — phase notes.
- `docs/features/` — feature notes (one directory per feature; tasks under `plan/tasks/`).
- `docs/decisions/` — ADRs.
- `docs/risks/` — risk register.
- `docs/changes/` — change notes (close-out records).
- `tools/instructions/` — lifecycle / status / quality conventions.

## Licence
MIT (planned). Publication governed by the open-source ADR (PHASE-001 deliverable).

## Related repos
- [`your-applications.com`](https://github.com/...) — website that hosts the MCP and surfaces it via integrator docs.
- [`your-trainer`](https://github.com/...) — Android app that consumes the MCP via upstream FEAT-0086.
