---
type: "[[task]]"
id: TASK-0023
aliases: ["TASK-0023"]
title: "Workout builder from structured intent (JSON → ZWO + FIT + .ytw deterministically)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: L
---

# TASK-0023 — Workout builder from structured intent (JSON → ZWO + FIT + .ytw deterministically)

Take a structured workout description as JSON (`{name, warmup: {minutes, target}, intervals: [{count, on: {minutes, target}, off: {minutes, target}}], cooldown: ...}`) and emit valid ZWO + FIT-workout + `.ytw` all at once. Deterministic; same input always produces the same output. Lets LLMs author workouts via structured intent rather than hallucinating XML.

## Acceptance
- [ ] JSON schema for structured intent documented + validated.
- [ ] Emits valid ZWO, FIT-workout, `.ytw` for the same input.
- [ ] Outputs pass the FEAT-0001 validators for each format.
- [ ] Deterministic: same JSON → byte-identical output across runs.
- [ ] Round-trips: emit ZWO → parse back → matches structured intent.
