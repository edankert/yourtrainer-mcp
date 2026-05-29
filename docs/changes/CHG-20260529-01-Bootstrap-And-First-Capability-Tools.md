---
type: "[[change]]"
id: CHG-20260529-01
title: "Bootstrap package + first capability tools + MCP server skeleton"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["repo-layout", "ci", "mcp-server", "capability-tools", "licence"]
issues: []
features: ["[[FEAT-0001]]", "[[FEAT-0002]]", "[[FEAT-0003]]", "[[FEAT-0004]]"]
related: ["[[ADR-0001]]", "[[ADR-0002]]", "[[ADR-0003]]", "[[TASK-0001]]", "[[TASK-0008]]", "[[TASK-0018]]", "[[TASK-0019]]", "[[TASK-0021]]", "[[TST-0001]]"]
---

# Bootstrap package + first capability tools + MCP server skeleton

## Summary
Stood up the previously docs-only repo as a working Python package and ran the
first slice of PHASE-001. Decided the three open ADRs (architecture, OSS,
capability scope), scaffolded the package, and implemented the first real
capability tools behind a FastMCP server.

**Decisions**
- [[ADR-0001]] — Python 3.10+ + FastMCP, streamable-HTTP transport, subpath URL.
- [[ADR-0002]] — OSS under MIT; hosted instance canonical.
- [[ADR-0003]] — capability-tools v1 scope + deferral list.

**Code (new)**
- `pyproject.toml` (hatchling, `src/` layout), `LICENSE` (MIT), `.github/workflows/ci.yml`.
- `src/yourtrainer_mcp/`:
  - `power.py` — NP / IF / TSS, rolling average, peak-power curve, time-in-zone (pure Python).
  - `activity.py` — TCX/GPX parsing (stdlib) + FIT (optional `fitparse`) + `inspect_activity` summary.
  - `formats.py` — supported-formats catalogue (FEAT-0001 seed).
  - `attribution.py` — attribution + `.ytw` hint invariant (FEAT-0003).
  - `server.py` — FastMCP server: `list_supported_formats`, `inspect_activity_file`.
- `tests/` — 26 tests (power math, parsing, inspector, attribution, server wiring).
- `deploy/` — systemd unit, Caddyfile, deploy guide for `mcp.your-applications.com/your-trainer`.

## Impact
- Repo is no longer docs-only: `pip install -e .` and `yourtrainer-mcp` now work.
- Adds a runtime dependency surface (FastMCP) and an optional one (`fitparse`) — see RISK note below.
- New env-var configuration surface for the server: `YTMCP_TRANSPORT`, `YTMCP_HOST`, `YTMCP_PORT`, `YTMCP_PATH`.
- New artifact paths: `src/`, `tests/`, `deploy/`, `.github/`.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0001/0002/0003/0004 → in-progress)
- requirements: not-applicable
- tasks: updated (TASK-0001/0008/0018/0019 → done; TASK-0021 → doing)
- issues: not-applicable
- tests: new (TST-0001)
- workflows: not-applicable
- decisions: new (ADR-0001, ADR-0002, ADR-0003)
- risks: updated (RISK-0001 deploy surface, RISK-0002 OSS, RISK-0003 format-spec — all still open; new dependency surface noted here)
- changes: new (this note)
- snapshot: updated (counters, focus, statuses, metrics)

## Verification
- `pytest -q` → 26 passed. `ruff check src tests` → clean. `mypy src` → clean.
- HTTP transport smoke: `initialize` over streamable-HTTP returns 200 + valid
  JSON-RPC result naming `yourtrainer-mcp`.

## Follow-ups
- [ ] Publish public GitHub repo + push (this session).
- [ ] VPS deploy at `mcp.your-applications.com/your-trainer` — needs SSH access; artefacts ready in `deploy/`.
- [ ] FIT-binary test fixtures; TrainingPeaks reference corpus ([[TASK-0045]]) to take TASK-0021 → done.
- [ ] `MAINTAINERS.md` (OSS contribution expectations) per [[ADR-0002]] / [[RISK-0002]].
- [ ] New dependency surface (FastMCP/fitparse) — fold into [[RISK-0001]] deploy review.
