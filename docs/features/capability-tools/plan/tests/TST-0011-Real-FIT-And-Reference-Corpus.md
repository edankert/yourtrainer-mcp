---
type: "[[test]]"
id: TST-0011
title: "Real-world FIT files + NP/IF/TSS reference corpus"
status: passing
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0045]]"]
scope: feature
kind: automated
level: unit
entrypoint: "pytest -q tests/test_fit_real_files.py tests/test_reference_corpus.py"
requirements: []
features: ["[[FEAT-0004]]"]
issues: []
tasks: ["[[TASK-0020]]", "[[TASK-0021]]", "[[TASK-0045]]"]
artifacts: ["tests/test_fit_real_files.py", "tests/test_reference_corpus.py", "tests/fixtures/reference_values.json", "tests/fixtures/external/"]
evidence: ["153 passed; real ride NP 301.05 W agreed by 3 independent paths"]
last_run: "2026-05-29"
related: ["[[TST-0003]]"]
---

# Real-world FIT files + NP/IF/TSS reference corpus

## Purpose
Validate the FIT reader and the power engine against **real** Garmin files
(MIT-licensed, from python-fitparse) and pin a data-driven reference corpus for
NP/IF/TSS (TASK-0020/0021/0045).

## Fixtures
- `tests/fixtures/external/` — real Garmin FIT files (MIT; see NOTICE.md):
  `Activity.fit`, three `Workout*.fit`, and a real Edge 810 + Vector ride.
- `tests/fixtures/reference_values.json` — analytic anchors + the real ride.

## Expected results
- Our codec reads the real activity and all three real workout files (names +
  steps decoded), without the optional `fitparse` extra.
- The real ride's NP is **301.05 W**, agreed by three independent paths: our
  optimised engine, an O(n·w) naive reimplementation, and the `fitparse`-derived
  power stream (the last skips when `fitparse` is absent).
- End-to-end inspect of the ride @FTP 275: NP 301.1, IF 1.095, TSS 156.5.
- Synthetic anchors hold exactly: 1 h @ FTP ⇒ TSS 100, IF 1.0; 30 min @ 0.8 ⇒
  TSS 32.

## Caveats
Real-activity values follow TrainingPeaks' published NP/TSS *formula* (30 s
Coggan) and are parser-cross-validated, but are not scraped from TrainingPeaks'
own per-activity output. Closing TASK-0045 fully needs ≥5 activities with
vendor-published numbers (login-gated).

## Evidence
- `153 passed in 2.68s`; ruff + mypy clean.
