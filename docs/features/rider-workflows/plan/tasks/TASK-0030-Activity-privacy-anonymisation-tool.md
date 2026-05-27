---
type: "[[task]]"
id: TASK-0030
aliases: ["TASK-0030"]
title: "Activity privacy / anonymisation tool"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0005]]"]
fixes: []
effort: M
---

# TASK-0030 — Activity privacy / anonymisation tool

Given a FIT / GPX activity file + an optional config (geofence around home, fuzz radius), emit a cleaned version with: start/end coordinates fuzzed to ~1km if within the geofence, device IDs stripped, optional HR-stream removal, optional timestamp fuzzing (date preserved, time-of-day randomised). Lets riders safely share activities publicly without leaking location/personal data. Stateless.

## Acceptance
- [ ] Fuzzes coordinates correctly: ≥1km perturbation within configured geofence; passes through unchanged outside.
- [ ] Strips device IDs, serial numbers, personal-data fields per the FIT spec.
- [ ] Optional HR-stream removal works on FIT + GPX.
- [ ] Output file imports cleanly into Strava / Garmin Connect / Komoot (manual verification on samples).
- [ ] Stateless: input file in, cleaned file out, no retention.
