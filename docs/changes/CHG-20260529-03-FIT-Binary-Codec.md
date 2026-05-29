---
type: "[[change]]"
id: CHG-20260529-03
title: "Self-contained FIT binary codec (workout read/write + activity read)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["capability-tools", "mcp-server", "dependencies"]
issues: []
features: ["[[FEAT-0004]]"]
related: ["[[TASK-0020]]", "[[TASK-0021]]", "[[TST-0003]]", "[[ADR-0001]]"]
---

# Self-contained FIT binary codec

## Summary
Wave 2. Implemented a dependency-free FIT codec rather than bundling the Garmin
SDK (consistent with ADR-0001's minimal-deps posture):
- `fit.py` — FIT CRC, a `FitWriter` (header + definition/data records + file
  CRC), a general `decode`, plus `encode_activity_fit` / `decode_activity` for
  activity records (used for fixtures and the read fallback).
- `fit_workout.py` — `encode_workout_fit` / `decode_workout_fit` using FIT's
  %FTP power convention; intervals/ramps expand to discrete time steps.
- `activity.parse_fit` now falls back to the built-in codec when `fitparse`
  is absent, so the FIT-read path works with no optional extra.

## Impact
- New MCP tools: `read_fit_workout`; `build_workout_from_intent` gains
  `output_format="fit"` (base64-encoded bytes).
- FIT support no longer strictly requires the `fitparse` extra for standard
  files; the extra remains preferred for rich real-world files.
- Closes TASK-0021's FIT-read sub-item hermetically.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0004)
- requirements: not-applicable
- tasks: updated (TASK-0020 → doing; TASK-0021 note updated)
- issues: not-applicable
- tests: new (TST-0003)
- workflows: not-applicable
- decisions: not-applicable (covered by ADR-0001)
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (counters, focus → Wave 3, metrics)

## Verification
- `pytest -q` → 46 passed. `ruff check` clean. `mypy src` clean.
- Independent `fitparse` parses our encoded workout bytes correctly.

## Follow-ups
- [ ] TASK-0020 → done needs ≥10 canonical Garmin/Wahoo/TP sample files +
  on-device Edge import test.
- [ ] TASK-0021 → done needs the TrainingPeaks reference corpus (TASK-0045).
- [ ] Wave 3: training-load math (CTL/ATL/TSB, decoupling, FTP detect, PDC,
  dedicated peak-power tool — TASK-0027/0028/0046/0047/0022).
