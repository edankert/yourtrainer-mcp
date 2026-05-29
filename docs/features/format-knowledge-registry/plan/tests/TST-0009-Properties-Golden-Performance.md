---
type: "[[test]]"
id: TST-0009
title: "Property-based, golden-file & performance suite"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0041]]"]
scope: system
kind: automated
level: unit
entrypoint: "pytest -q tests/test_properties.py tests/test_golden.py tests/test_performance.py"
requirements: []
features: ["[[FEAT-0001]]", "[[FEAT-0004]]", "[[FEAT-0002]]"]
issues: []
tasks: ["[[TASK-0041]]", "[[TASK-0044]]"]
artifacts: ["tests/test_properties.py", "tests/test_golden.py", "tests/test_performance.py", "tests/golden/", "scripts/benchmark.py"]
evidence: ["137 passed (full suite); benchmark sub-3ms on 1h inputs"]
last_run: "2026-05-29"
related: []
---

# Property-based, golden-file & performance suite

## Purpose
System-wide hardening: Hypothesis property tests for invariants, golden-file
regression locks on rendered output, and performance budgets (TASK-0041,
TASK-0044).

## Expected results
- **Properties** (all inputs): ZWO and .ytw roundtrips preserve the power
  series exactly for 2-decimal FTP fractions; FIT roundtrip within ±1.25 W;
  difficulty is FTP-independent; NP ≥ average and NP(constant)=constant; scale
  is proportional within per-block rounding slack.
- **Golden**: the canonical workout's ZWO/.ytw/difficulty match committed
  fixtures byte-for-byte; the golden ZWO still parses back.
- **Performance**: NP/peak-curve/inspect/interval-detection on a 1-hour ride
  and build+score complete well under generous budgets; NP stays linear to 5 h
  (guards against O(n²)).

## Evidence
- `137 passed in 1.93s`; ruff + mypy clean.
- `scripts/benchmark.py`: NP 0.32 ms, peak-curve 0.97 ms, inspect 2.30 ms,
  interval-detect 0.55 ms, build+score 0.58 ms (best of 5, 1-hour inputs).
