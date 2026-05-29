---
type: "[[test]]"
id: TST-0003
title: "FIT codec round-trip + FIT-activity read suite"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0020]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_fit.py"
requirements: []
features: ["[[FEAT-0004]]"]
issues: []
tasks: ["[[TASK-0020]]", "[[TASK-0021]]"]
artifacts: ["tests/test_fit.py", "src/yourtrainer_mcp/fit.py", "src/yourtrainer_mcp/fit_workout.py"]
evidence: ["46 passed (full suite); fitparse cross-check parses our bytes"]
last_run: "2026-05-29"
related: ["[[ADR-0001]]"]
---

# FIT codec round-trip + FIT-activity read suite

## Purpose
Verify the self-contained FIT binary codec: valid header/CRC, workout
encode→decode round-trip, and that the FIT-activity read path feeds the
inspector correctly (closing TASK-0021's FIT-read sub-item hermetically).

## Procedure
- `pytest -q tests/test_fit.py`
- Optional external cross-check: install `fitparse` and parse encoded bytes.

## Expected results
- Encoded files carry the `.FIT` signature and correct header + file CRC.
- Write→read preserves the per-second power profile within ≤0.5% FTP (integer
  %FTP quantisation); interval/ramp expansion is lossless under this check.
- A generated FIT activity (1 h @ 250 W) reads back through the built-in
  fallback to NP 250 / IF 1.0 / TSS 100; distance & altitude scaling correct.
- `fit.decode` rejects non-FIT input.

## Evidence
- `46 passed in 0.76s`; ruff + mypy clean.
- Cross-validation: `fitparse.FitFile` parses our encoded workout — correct
  `workout_step` count, `intensity` values (warmup/active), and `wkt_name`.

## Notes
- Compressed-timestamp headers and developer fields are out of scope for the
  built-in codec (use the `fitparse` extra). Real-world Garmin/Wahoo/TP sample
  validation + on-device import remain open for TASK-0020.
