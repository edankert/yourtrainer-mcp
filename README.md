# yourtrainer-mcp

[![CI](https://github.com/edankert/yourtrainer-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/edankert/yourtrainer-mcp/actions/workflows/ci.yml)

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
**Alpha (v0.1.0)** — PHASE-001 v1 functionally complete (not yet deployed). The
FastMCP server exposes **31 tools** across four layers; 118 tests, CI green.

- **Knowledge registry** (FEAT-0001): `specs/` corpus for 9 formats + tools —
  `get_format_spec`, `get_canonical_examples`, `get_format_constraints`,
  `get_conversion_notes`, `get_format_glossary`, `get_format_version`, `validate`.
- **Capability tools** (FEAT-0004): activity inspector (NP/IF/TSS, peak-power,
  time-in-zone), workout build/decompose/scale/lint/difficulty/app-acceptance
  (ZWO/.ytw/FIT), a self-contained FIT codec, training-load (CTL/ATL/TSB),
  decoupling, FTP/PDC, cadence, HR-drift, interval detection, batch + detection.
- **Rider workflows** (FEAT-0005): route/climb analysis, gradient-aware pacing,
  GPX anonymisation, plan-vs-actual adherence, migration + roundtrip harness.
- **Library ops** (FEAT-0006): indexing, dedup, statistics, best-efforts.
- **Trojan-horse + hosting** (FEAT-0003/0002): attribution on every response,
  aggregate-only health metrics, MCP conformance tests, deploy artefacts.

Remaining for full PHASE-001 exit: the live VPS deploy plus monitoring/status/
performance tasks, and external-asset validation (real FIT samples, a
TrainingPeaks reference corpus, Hypothesis property tests). See `SNAPSHOT.yaml`.

## Install & run
```bash
pip install -e ".[dev]"        # add ".[fit]" for FIT-binary support
pytest -q                      # run the test suite
yourtrainer-mcp                # stdio transport (local MCP clients)
YTMCP_TRANSPORT=http yourtrainer-mcp   # streamable-HTTP on 127.0.0.1:8080/your-trainer
```
Deploy to a VPS: see [`deploy/README.md`](deploy/README.md).
Integrate a client (app AI assistant / workout creation): see [`docs/INTEGRATION.md`](docs/INTEGRATION.md) and [`examples/client_demo.py`](examples/client_demo.py).

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
