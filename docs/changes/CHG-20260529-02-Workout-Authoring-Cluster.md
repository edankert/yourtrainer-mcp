---
type: "[[change]]"
id: CHG-20260529-02
title: "Workout authoring cluster (build/decompose/scale/lint/difficulty/acceptance)"
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
related: ["[[TASK-0023]]", "[[TASK-0033]]", "[[TASK-0035]]", "[[TASK-0025]]", "[[TASK-0050]]", "[[TASK-0024]]", "[[TST-0002]]", "[[ADR-0003]]"]
---

# Workout authoring cluster

## Summary
Wave 1 of the full-PHASE-001 build. Added `src/yourtrainer_mcp/workout.py`: a
structured workout model with build-from-intent, deterministic ZWO and .ytw
rendering, decompose (file → intent), scale (duration/intensity), domain-aware
lint, difficulty scoring (reuses the NP/IF/TSS engine), and an app-acceptance
checker with a v1 constraints seed. Wired six new MCP tools.

This is the authoring cluster the PHASE-001 note flags as a prerequisite for
FEAT-0009 library curation.

## Impact
- New MCP tools: `build_workout_from_intent`, `decompose_workout`,
  `scale_workout`, `lint_workout`, `workout_difficulty`, `app_acceptance_check`.
- Defines the `.ytw` JSON format v1 (formalised later in TASK-0006).
- FIT-workout output (third render target of TASK-0023) is deferred to Wave 2.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0004 in-progress)
- requirements: not-applicable
- tasks: updated (TASK-0023/0024/0025/0033/0035/0050 → done)
- issues: not-applicable
- tests: new (TST-0002)
- workflows: not-applicable
- decisions: not-applicable (covered by ADR-0003)
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (statuses, counters, metrics, focus → Wave 2)

## Verification
- `pytest -q` → 40 passed. `ruff check` clean. `mypy src` clean.

## Follow-ups
- [ ] Wave 2: FIT binary (workout write + activity read round-trip) — TASK-0020,
  finishes TASK-0021 and the third TASK-0023 render target.
- [ ] Replace the v1 app-constraints seed with the FEAT-0001 catalogue when authored.
