---
type: "[[change]]"
id: CHG-20260529-07
title: "Library ops + health metrics + MCP conformance + close-out ADRs (Wave 6)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["library-operations", "trojan-horse", "mcp-server", "decisions"]
issues: []
features: ["[[FEAT-0006]]", "[[FEAT-0003]]", "[[FEAT-0002]]"]
related: ["[[TASK-0038]]", "[[TASK-0039]]", "[[TASK-0040]]", "[[TASK-0049]]", "[[TASK-0014]]", "[[TASK-0015]]", "[[TASK-0016]]", "[[TASK-0017]]", "[[TASK-0010]]", "[[TASK-0012]]", "[[TASK-0013]]", "[[TASK-0042]]", "[[ADR-0004]]", "[[ADR-0005]]", "[[TST-0007]]", "[[TST-0008]]"]
---

# Library ops + health + conformance + close-out ADRs (Wave 6)

## Summary
Final v1 wave:
- `library.py` (FEAT-0006) — index, near-duplicate detection, statistics,
  best-efforts-across-history. Tools: `index_library`,
  `find_duplicate_workouts`, `library_statistics`, `best_efforts_across_history`.
- `health.py` (TASK-0017) — aggregate-only operational counters + `get_health`
  tool; a counting `@tool` wrapper instruments all 31 tools (no per-call data).
- MCP conformance test (TASK-0042) driving the protocol via the in-memory client.
- ADR-0004 (default output ZWO + fraction-of-FTP convention, TASK-0014) and
  ADR-0005 (path/base64 file-transfer convention, TASK-0013).
- Closed the attribution copy/integration tasks (TASK-0015/0016) and the
  hosting artefacts already shipped (TASK-0010 systemd, TASK-0012 tool wiring).

FEAT-0003, FEAT-0005, and FEAT-0006 are complete. FEAT-0001 and FEAT-0004 are
functionally complete bar external-asset tasks; FEAT-0002 awaits the actual
VPS deploy (held per the user) plus monitoring/status/perf tasks.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0003, FEAT-0006 → done)
- requirements: not-applicable
- tasks: updated (12 tasks → done)
- issues: not-applicable
- tests: new (TST-0007, TST-0008)
- workflows: not-applicable
- decisions: new (ADR-0004, ADR-0005)
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (statuses, counters, metrics, focus)

## Verification
- `pytest -q` → 118 passed. ruff + mypy clean. 31 tools over the MCP client.

## Follow-ups (remaining for full PHASE-001 exit)
- [ ] VPS deploy at mcp.your-applications.com (held per user; artefacts in deploy/).
- [ ] TASK-0009 provisioning, TASK-0011 monitoring/alerting, TASK-0043 status page,
  TASK-0044 performance baselines — infra tasks needing the live host.
- [ ] TASK-0020/0021 external assets (Garmin/Wahoo/TP FIT samples, TP reference
  corpus TASK-0045), TASK-0041 Hypothesis property tests + golden files.
