---
type: "[[change]]"
id: CHG-20260529-10
title: "Real FIT fixtures (MIT) + NP/IF/TSS reference corpus (Wave 9)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["capability-tools", "tests", "fixtures"]
issues: []
features: ["[[FEAT-0004]]", "[[FEAT-0001]]"]
related: ["[[TASK-0020]]", "[[TASK-0021]]", "[[TASK-0045]]", "[[TST-0011]]"]
---

# Real FIT fixtures + reference corpus (Wave 9)

## Summary
Sourced real, license-clear assets to validate the FIT path and NP/IF/TSS:
- **Vendored MIT FIT files** from python-fitparse (David Cooper / Carey
  Metcalfe) into `tests/fixtures/external/` with a NOTICE retaining the MIT
  attribution: a real Edge 810 + Vector power ride, a small `Activity.fit`, and
  three real Garmin **workout** files.
- **Reference corpus** `tests/fixtures/reference_values.json` — analytic anchors
  (1 h @ FTP = 100 TSS; 30 min @ 0.8 = 32 TSS) plus the real ride — driven by
  `tests/test_reference_corpus.py`.
- **Real-file tests** `tests/test_fit_real_files.py`: our codec reads the real
  workout/activity files; the ride's NP (301.05 W) is agreed three ways (our
  engine, a naive reimplementation, and fitparse).
- Confirmed via TrainingPeaks docs that our NP/IF/TSS formulas match their
  published definitions; filtered a fitparse-internal deprecation warning.

## Impact
- Materially advances (still `doing`) TASK-0020 (now reads real Garmin workout
  files), TASK-0021 (NP/IF/TSS validated on a real ride), and TASK-0045
  (reference corpus started). None fully close: TASK-0020 needs ≥10 samples + an
  on-device Edge import test; TASK-0021/0045 need ≥5 activities validated against
  TrainingPeaks' *own* published numbers (login-gated).

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0004 real-FIT validation)
- requirements: not-applicable
- tasks: updated (TASK-0045 → doing; TASK-0020/0021 progress notes)
- issues: not-applicable
- tests: new (TST-0011)
- workflows: not-applicable
- decisions: not-applicable
- risks: RISK-0003 (format drift) — real-file coverage reduces this
- changes: new (this note)
- snapshot: updated (counters, metrics, focus)

## Verification
- `pytest -q` → 153 passed. ruff + mypy clean.

## Follow-ups
- [ ] Grow the workout-sample corpus to ≥10 and add an on-device Edge import check.
- [ ] If TrainingPeaks/Intervals.icu per-activity numbers become available,
  add ≥5 with vendor-published NP/TSS to fully close TASK-0021/0045.
