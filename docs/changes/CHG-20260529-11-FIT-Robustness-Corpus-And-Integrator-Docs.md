---
type: "[[change]]"
id: CHG-20260529-11
title: "FIT invalid-sentinel fix + ≥10 workout corpus + integrator docs (Wave 10)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["capability-tools", "mcp-server", "docs", "packaging"]
issues: []
features: ["[[FEAT-0004]]", "[[FEAT-0002]]"]
related: ["[[TASK-0020]]", "[[TASK-0056]]", "[[RISK-0003]]"]
---

# FIT robustness + workout corpus + integrator docs (Wave 10)

## Summary
- **Bug fix (FIT invalid sentinels):** `fit._decode_value` now maps a field's
  per-base-type "invalid" value (e.g. uint16 `0xFFFF`) to `None`. Found while
  hunting real assets — an Edge 500 with no power meter records power `0xFFFF`,
  which we had read as 65535 W. `decode_activity` / `decode_workout_fit` updated
  to skip/coalesce `None`. Reduces format-drift risk (RISK-0003).
- **≥10 FIT-workout sample corpus (TASK-0020):** `tests/test_fit_workout_corpus.py`
  exercises 10 diverse generated workouts (round-trip + independent fitparse
  parse) plus the 3 real Garmin workout files.
- **Real HR-only fixture:** vendored `garmin-edge-500-activity.fit` (MIT);
  test asserts no phantom power + HR stats present.
- **Publish-readiness:** `python -m build` + `twine check` PASS (sdist + wheel;
  9 specs packaged).
- **Integrator docs (TASK-0056):** `docs/INTEGRATION.md` + runnable
  `examples/client_demo.py` (AI-assistant build, workout-creation convert/scale,
  ride analysis), linked from the README — satisfies the PHASE-001 integrator-docs
  exit item.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0004 robustness; FEAT-0002 integrator docs)
- requirements: not-applicable
- tasks: updated (TASK-0056 → done; TASK-0020 corpus item satisfied — see note)
- issues: not-applicable
- tests: updated (test_fit_workout_corpus, real HR-only test); no new TST note (covered by TST-0011 scope)
- workflows: not-applicable
- decisions: not-applicable
- risks: RISK-0003 reduced (sentinel handling on real files)
- changes: new (this note)
- snapshot: updated (TASK counter 55→56, statuses, metrics, focus)

## Verification
- `pytest -q` → 178 passed. ruff + mypy clean. `twine check` PASSED.
- `examples/client_demo.py` runs the three flows end-to-end (real ride NP 301.1 W).

## Remaining hard blockers (need the user)
- **TASK-0009 / live half of TASK-0011, TASK-0043** — need SSH to the VPS.
- **TASK-0020** — on-device Garmin Edge import test (needs hardware).
- **TASK-0021 / TASK-0045** — ≥5 activities vs TrainingPeaks' *published* numbers
  (login-gated); our values match TP's published formula + are cross-validated.
