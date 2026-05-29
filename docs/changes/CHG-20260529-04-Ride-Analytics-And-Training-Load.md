---
type: "[[change]]"
id: CHG-20260529-04
title: "Ride analytics + training-load + detection + batch (Wave 3)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["capability-tools", "mcp-server"]
issues: []
features: ["[[FEAT-0004]]"]
related: ["[[TASK-0022]]", "[[TASK-0026]]", "[[TASK-0027]]", "[[TASK-0028]]", "[[TASK-0036]]", "[[TASK-0037]]", "[[TASK-0046]]", "[[TASK-0047]]", "[[TASK-0051]]", "[[TASK-0052]]", "[[TASK-0053]]", "[[TASK-0054]]", "[[TST-0004]]"]
---

# Ride analytics + training-load + detection + batch (Wave 3)

## Summary
Added the analytics layer of FEAT-0004:
- `training_load.py` — CTL/ATL/TSB (EWMA of daily TSS) + recovery heuristic.
- `analysis.py` — peak-power curve, best efforts (with timing), FTP estimate,
  2-parameter critical-power model (mFTP), HR–power decoupling, HR drift,
  cadence analysis, interval auto-detection.
- `detect.py` — content-based format detection + lightweight file inspector.
- `batch.py` — batch activity inspection with aggregation + per-file errors.

Wired MCP tools: `analyze_ride`, `training_load`, `recovery_time`,
`detect_file`, `batch_inspect`. This completes the FEAT-0004 capability surface
except TASK-0020/0021, which await external sample files / reference corpus.

Also hardened `activity.parse_fit`: the fitparse branch now only accepts
genuine datetime timestamps (fitparse returns sub-epoch values as raw ints),
falling back to 1 Hz timing otherwise.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0004 — analytics complete)
- requirements: not-applicable
- tasks: updated (12 tasks → done)
- issues: not-applicable
- tests: new (TST-0004)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (statuses, counters, metrics, focus → Wave 4)

## Verification
- `pytest -q` → 74 passed. `ruff check` clean. `mypy src` clean.

## Follow-ups
- [ ] Wave 4: knowledge registry — `specs/` corpus + registry tools (FEAT-0001).
- [ ] Reference-corpus validation of the math (TASK-0045) would further harden
  CTL/ATL/TSB and PDC outputs against canonical numbers.
