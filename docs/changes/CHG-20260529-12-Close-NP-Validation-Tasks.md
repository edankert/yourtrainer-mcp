---
type: "[[change]]"
id: CHG-20260529-12
title: "Close TASK-0021/0045 (NP/IF/TSS validation) + FEAT-0001 complete"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["capability-tools", "knowledge-registry"]
issues: []
features: ["[[FEAT-0001]]", "[[FEAT-0004]]"]
related: ["[[TASK-0021]]", "[[TASK-0045]]", "[[TST-0011]]"]
---

# Close NP/IF/TSS validation tasks; FEAT-0001 complete

## Summary
Per the user's decision, TASK-0021 (FIT-activity inspector NP/IF/TSS) and
TASK-0045 (reference corpus) are marked **done** on the basis that the metrics
are validated against:
- TrainingPeaks' **published formula** (confirmed against their help-centre docs);
- the universal anchors (1 h @ FTP = 100 TSS; constant ⇒ NP == power); and
- a **real ride cross-validated three ways** — our codec, fitparse, and an
  independent naive reimplementation (all 301.05 W).

TrainingPeaks' own per-activity numbers are login-gated and were **not** used;
this caveat is recorded in `tests/fixtures/reference_values.json` and the task notes.

With TASK-0045 closed, **FEAT-0001 (knowledge registry) is complete** (all tasks
done). FEAT-0004 remains in-progress only because TASK-0020 awaits an on-device
Garmin Edge import test.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0001 → done)
- requirements: not-applicable
- tasks: updated (TASK-0021, TASK-0045 → done)
- issues: not-applicable
- tests: covered by TST-0011 (real FIT + reference corpus)
- workflows: not-applicable
- decisions: not-applicable
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (statuses, metrics 52/56 tasks, 4/6 features)

## Verification
- `pytest -q` → 178 passed (unchanged; this is a status/decision close-out).
