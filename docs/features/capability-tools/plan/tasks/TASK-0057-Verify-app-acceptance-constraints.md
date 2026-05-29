---
type: "[[task]]"
id: TASK-0057
aliases: ["TASK-0057"]
title: "Verify + correct app-acceptance constraints against vendor docs (sourced)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
implements: ["[[FEAT-0004]]"]
fixes: ["[[TASK-0024]]"]
effort: S
---

# TASK-0057 — Verify + correct app-acceptance constraints

The v1 `app_acceptance_check` (TASK-0024) shipped a hardcoded seed with several
**unverified or wrong** values. Before publishing the MCP, verify each datum
against vendor/reference documentation and keep only sourced facts.

## What verification found
- **Garmin max 50 steps** — VERIFIED (real upload error "maximum expected
  number of 50 steps"; forums). Kept.
- **Garmin has NO native ramp** — VERIFIED; ramps expand into discrete steps.
  The seed wrongly had `supports_ramp: True`. Corrected → warning on ramps.
- **Garmin 99-repeat cap** — sourced; added as a check.
- **Zwift natively supports Ramp + FreeRide; no documented step/size cap** —
  VERIFIED (h4l/zwift-workout-file-reference). The seed's `max_steps: 1000` was
  invented → removed.
- **Wahoo `max_steps: 200`** — could NOT be verified anywhere → app removed
  rather than ship a fabricated limit.
- **Garmin `max_name_chars: 32`** — not vendor-confirmed → removed from the hard
  checker; kept only as a hedged "soft caution" note in the registry.

## Acceptance
- [x] Each shipped constraint carries a source; unverifiable ones omitted.
- [x] Checker emits hard `issues` only for documented limits; `warnings` for
  caveats (ramp expansion). Unknown apps return `accepted: null`.
- [x] Registry (`specs/fit.json`, `specs/zwo.json`) updated with the verified facts.
- [x] Tests updated to the verified behaviour.

> **Done 2026-05-29 (CHG-20260529-13).** Sources: Garmin 50-step upload error
> (trainerday/garmin forums); `github.com/h4l/zwift-workout-file-reference`.
> Future: source Wahoo/TrainerRoad/other limits before re-adding them.
