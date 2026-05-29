---
type: "[[task]]"
id: TASK-0004
aliases: ["TASK-0004"]
title: "Author FIT format documentation (workout + activity)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: L
---

> **Done 2026-05-29 (CHG-20260529-05, [[TST-0005]]).** specs/fit.json: binary container (header/definition/data/CRC), workout + activity messages, %FTP target convention, examples.

# TASK-0004 — Author FIT format documentation (workout + activity)

Document Garmin's FIT format — the universal binary format covering both workout plans and recorded activities. Spec links to Garmin's FIT SDK Profile.xlsx; documentation focuses on the cycling-relevant message types (Workout, WorkoutStep, Activity, Session, Lap, Record), per-app constraints (Garmin Edge 530 text-event limits, Wahoo head-unit handling), and the conversion gotchas with ZWO and TCX.

## Acceptance
- [ ] `specs/fit/workout.md` and `specs/fit/activity.md` covering the cycling-relevant message types.
- [ ] ≥3 canonical FIT examples per type (workout + activity).
- [ ] `constraints.json` covers ≥5 FIT-consuming apps/devices (Garmin Edge variants, Wahoo Bolt/Roam, TrainerRoad).
- [ ] Conversion notes for FIT-workout ⟷ ZWO with documented field-mapping decisions.
- [ ] Cross-link to FEAT-0004 capability layer for actual FIT read/write.
