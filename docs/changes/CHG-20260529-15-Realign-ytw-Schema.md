---
type: "[[change]]"
id: CHG-20260529-15
title: "Realign workout model + .ytw to the canonical Your Trainer schema (ISS-0001)"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["capability-tools", "mcp-server", "knowledge-registry"]
issues: ["[[ISS-0001]]"]
features: ["[[FEAT-0004]]"]
related: ["[[TASK-0063]]", "[[ADR-0004]]"]
---

# Realign workout model + .ytw to the canonical schema

## Summary
Rewrote the workout model and serialisers to the canonical Your Trainer schema,
fixing ISS-0001 (MCP-built `.ytw` previously used a made-up shape that would not
import into the app).

- **Model** (`workout.py`): `Block` / `Repeat` / `Cue` / `Workout`; power as
  **integer % FTP**; flat `intervals` of blocks + **nestable** repeat groups;
  warmup/cooldown via `intervalType`.
- **build_workout** input now mirrors `workout-intent.json`
  (`warmup`/`intervals`/`cooldown`).
- **to_ytw** emits canonical `.ytw` (`programId`, `programName`, `totalDuration`,
  `workoutType`, `variant`, `intervals` with `intervalType`/`targetPowerPercent`/
  repeat groups, per-locale `strings`); **from_ytw** parses it.
- ZWO / FIT / difficulty / scale / lint / app-acceptance / adherence adapted;
  `fit_workout` rewritten (integer %FTP ⇒ exact FIT round-trips).
- `specs/ytw.json`, `docs/INTEGRATION.md`, and `examples/client_demo.py` updated
  to the real schema; `decompose_workout` / `read_fit_workout` now return `.ytw`.

## Verification (canonical)
Cross-checked field-for-field against `your-trainer/docs/ytw-schema.json`, the
`generate_workout_library.py` translator, and the published
`your-applications.com/your-trainer/workout-schema.html`. The published page
resolved two stale points in `ytw-schema.json`:
- **workoutType (POWER/HR_ZONE/ROUTE) and variant (STANDARD/RAMP_TEST) are
  separate fields** — implemented as such.
- **Repeat groups can nest** — now supported recursively across build / .ytw /
  ZWO / FIT / difficulty / scale / adherence.

Difficulty matches the website manifest (sweet-spot-3x10 ⇒ TSS 58.4, IF 0.764).

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0004)
- requirements: not-applicable
- tasks: new (TASK-0063, done; fixes ISS-0001)
- issues: updated (ISS-0001 → fixed)
- tests: updated (test_workout/_fit/_fit_workout_corpus/_properties/_golden/
  _workflows/_registry/_conformance rewritten to the new schema; golden regenerated)
- workflows: not-applicable
- decisions: not-applicable (within ADR-0004 scope)
- risks: not-applicable
- changes: new (this note)
- snapshot: updated (TASK 62→63, ISS-0001 fixed, metrics 59/63)

## Verification
- `pytest -q` → 192 passed. ruff + mypy clean. Example client runs against the
  new schema; ytw/zwo/fit round-trips exact incl. nested repeats.

## Follow-ups
- Non-primary-locale label/cue translation stays the website generator's job;
  the MCP emits primary-locale `strings` (+ supplied name_i18n/description_i18n).
