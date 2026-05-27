---
type: "[[task]]"
id: TASK-0033
aliases: ["TASK-0033"]
title: "Workout decomposition (file → structured intent)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: M
---

# TASK-0033 — Workout decomposition (file → structured intent)

Tool that takes a workout file (ZWO, FIT-workout, ERG/MRC, `.ytw`) and emits the structured intent JSON that `build_workout_from_intent` (TASK-0023) would consume to reproduce it. Closes the symmetry gap in PHASE-001: agents can already build forward (intent → workout) and validate, but cannot read backward (workout → intent). Without decomposition, the common AI-Coach flow *"modify this workout I like"* forces the AI to re-author from scratch — losing the rider's preferences buried in the original. With decomposition, agents read → modify → re-build using the same primitives.

## Acceptance
- [ ] Tool reads valid ZWO / FIT-workout / ERG/MRC / `.ytw` and emits structured intent JSON conforming to the build_workout_from_intent input schema.
- [ ] Round-trips: `decompose(build(intent))` == `intent` for canonical samples (semantic equality, not byte-equality — comments and ordering may differ).
- [ ] Round-trips: `build(decompose(file))` produces a workout equivalent to the original (intervals preserved, targets within FIT quantisation).
- [ ] Reports a `confidence_notes` field for fields the source format doesn't carry cleanly (e.g. ZWO `<FreeRide>` blocks have no canonical intent representation; surface as null with a note rather than guess).
- [ ] Test coverage: ≥10 canonical samples per source format with round-trip assertions.
- [ ] Stateless.
