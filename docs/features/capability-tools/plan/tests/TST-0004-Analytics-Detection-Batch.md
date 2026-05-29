---
type: "[[test]]"
id: TST-0004
title: "Training-load, ride-analytics, detection & batch suite"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0027]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_training_load.py tests/test_analysis.py tests/test_detect.py tests/test_batch.py"
requirements: []
features: ["[[FEAT-0004]]"]
issues: []
tasks: ["[[TASK-0022]]", "[[TASK-0026]]", "[[TASK-0027]]", "[[TASK-0028]]", "[[TASK-0036]]", "[[TASK-0037]]", "[[TASK-0046]]", "[[TASK-0047]]", "[[TASK-0051]]", "[[TASK-0052]]", "[[TASK-0053]]", "[[TASK-0054]]"]
artifacts: ["tests/test_training_load.py", "tests/test_analysis.py", "tests/test_detect.py", "tests/test_batch.py", "src/yourtrainer_mcp/training_load.py", "src/yourtrainer_mcp/analysis.py", "src/yourtrainer_mcp/detect.py", "src/yourtrainer_mcp/batch.py"]
evidence: ["74 passed (full suite), Python 3.13.13"]
last_run: "2026-05-29"
related: []
---

# Training-load, ride-analytics, detection & batch suite

## Purpose
Verify the Wave-3 analytics: CTL/ATL/TSB, recovery, peak-power/best-efforts,
FTP estimate, power-duration model, HR–power decoupling, HR drift, cadence,
interval auto-detection, format detection, and the batch adapter.

## Expected results (key anchors)
- Constant 100 TSS/day ⇒ CTL & ATL → 100, TSB → 0; ATL reacts faster than CTL.
- Recovery bands map TSS → strain/hours as specified.
- Constant power ⇒ CP == power, W' ≈ 0; FTP estimate = 95% of best-20-min (or
  best-60-min when present).
- HR drift up in 2nd half ⇒ positive decoupling (~12.5% for the 140→160 case);
  flat HR ⇒ ~0% and well-paced.
- Cadence bands and coasting % computed correctly.
- A single hard block in an easy ride ⇒ exactly one detected interval.
- Format detection identifies FIT (magic), GPX/TCX/ZWO (root), .ytw (JSON);
  extension fallback otherwise.
- Batch aggregates totals and captures per-file errors without aborting.

## Evidence
- `74 passed in 0.98s`; ruff + mypy clean.
