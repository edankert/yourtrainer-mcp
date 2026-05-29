---
type: "[[change]]"
id: CHG-20260529-13
title: "Verify + correct app-acceptance constraints (sourced) before publish"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["capability-tools", "knowledge-registry"]
issues: []
features: ["[[FEAT-0004]]"]
related: ["[[TASK-0057]]", "[[TASK-0024]]"]
---

# Verify + correct app-acceptance constraints

## Summary
Pre-publish verification of the `app_acceptance_check` constraint data against
vendor/reference docs. The previous v1 seed contained guesses — two of which
were **wrong**, not merely unverified:
- Garmin was marked `supports_ramp: True`; in fact Garmin has **no native ramp**
  (ramps expand into discrete steps). Corrected to a ramp-expansion **warning**.
- Garmin `max_steps` 50 — **verified** and kept (real upload error message).
- Garmin 99-repeat cap — added (sourced).
- Zwift `max_steps: 1000` — invented; **removed** (no documented limit). Zwift's
  native Ramp + FreeRide support **verified** (canonical ZWO reference).
- Wahoo `max_steps: 200` — unverifiable; the **app was removed** rather than ship
  a fabricated number.
- Garmin `max_name_chars: 32` — not vendor-confirmed; **removed** from the hard
  checker, kept only as a hedged caution note in the registry.

Every shipped constraint now carries a `source`; the checker returns
`accepted: null` for apps with no verified constraints, and separates hard
`issues` from `warnings`. Verified facts also added to `specs/fit.json` and
`specs/zwo.json`.

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0004)
- requirements: not-applicable
- tasks: new (TASK-0057, fixes TASK-0024)
- issues: not-applicable
- tests: updated (test_workout acceptance tests rewritten to verified behaviour)
- workflows: not-applicable
- decisions: not-applicable (within ADR-0003 scope)
- risks: RISK-0003 — sourced constraints reduce drift/inaccuracy
- changes: new (this note)
- snapshot: updated (TASK 56→57, metrics 53/57)

## Verification
- `pytest -q` → 181 passed. ruff + mypy clean.
- Sources: Garmin 50-step upload error (trainerday/garmin forums);
  github.com/h4l/zwift-workout-file-reference (Ramp + FreeRide native, no cap).

## Follow-ups
- [ ] Source Wahoo / TrainerRoad / other vendor limits before re-adding them.
