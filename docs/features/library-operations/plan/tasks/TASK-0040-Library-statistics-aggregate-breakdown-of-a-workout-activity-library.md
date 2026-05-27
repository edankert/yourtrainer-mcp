---
type: "[[task]]"
id: TASK-0040
aliases: ["TASK-0040"]
title: "Library statistics — aggregate breakdown of a workout / activity library"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: M
---

# TASK-0040 — Library statistics — aggregate breakdown of a workout / activity library

Given a library (or index from TASK-0038), return aggregate stats: workout type distribution, FTP-target distribution, duration histogram, intensity-factor histogram, count of workouts per primary purpose (recovery / endurance / sweet-spot / threshold / V02max / sprint). Useful for *"what's actually in my library?"* and gap-spotting (*"I have no recovery workouts"*).

## Acceptance
- [ ] Output: structured aggregate JSON; readable in one glance by the agent.
- [ ] Handles libraries up to ≥1000 files.
- [ ] Stateless.
