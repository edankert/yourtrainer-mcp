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
**Early alpha (v0.1.0)**. PHASE-001 is underway. Landed so far:
- Python package + CI + MIT licence (TASK-0001); architecture decided in [ADR-0001](docs/decisions/ADR-0001-MCP-Server-Architecture.md).
- FastMCP server exposing `list_supported_formats` and `inspect_activity_file`.
- Capability engine: NP / IF / TSS, peak-power curve, time-in-zone; FIT (optional extra) / TCX / GPX activity parsing (TASK-0021, in progress).

The project-os under `docs/` describes the full planned scope (6 features, 50+ tasks). Remaining code lands as the phase is executed.

## Install & run
```bash
pip install -e ".[dev]"        # add ".[fit]" for FIT-binary support
pytest -q                      # run the test suite
yourtrainer-mcp                # stdio transport (local MCP clients)
YTMCP_TRANSPORT=http yourtrainer-mcp   # streamable-HTTP on 127.0.0.1:8080/your-trainer
```
Deploy to a VPS: see [`deploy/README.md`](deploy/README.md).

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
