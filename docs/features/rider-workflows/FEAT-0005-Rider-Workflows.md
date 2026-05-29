---
type: "[[feature]]"
id: FEAT-0005
aliases: ["FEAT-0005"]
title: "Cycling rider workflow tools"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
goal: "Higher-level rider-facing capabilities that compose the knowledge registry (FEAT-0001) and capability tools (FEAT-0004): pacing strategy generation, activity privacy / anonymisation, library migration across cycling apps, and LLM self-correction via roundtrip testing. All stateless — every tool call is independent; no rider data retained."
requirements: []
tasks: ["[[TASK-0029]]", "[[TASK-0030]]", "[[TASK-0031]]", "[[TASK-0032]]", "[[TASK-0034]]", "[[TASK-0048]]"]
release: ""
related: []
tests: []
---

# Cycling rider workflow tools

## Goal
Where FEAT-0001 ships reference material and FEAT-0004 ships primitive capabilities, this feature ships the workflows riders actually want when an LLM is helping them. Pacing a route, sharing an activity privately, migrating libraries between apps, validating LLM-generated conversions for self-correction.

All four tools compose the primitives from the other features. Each call is stateless — files go in, results come out, nothing is retained.

## Scope

### In scope
- Pacing strategy generator (GPX + FTP + target effort → per-segment pacing plan; exportable as `.ytw` / FIT-workout).
- Activity privacy / anonymisation tool (geofence-aware coordinate fuzzing, device-ID stripping, optional HR/timestamp removal).
- Library migration helper (LLM-orchestrated batch conversion between app libraries; tool prepares plan, LLM iterates, batch ops aggregates).
- Format-conversion roundtrip test harness (LLM converts X→Y; tool re-converts Y→X; diff vs original; structured loss report).
- Plan-vs-actual adherence scorecard (workout file + activity file → per-interval scorecard; closes the planning-execution loop).
- Climb analysis on a GPX route (detect + categorise climbs by FIETS index; pairs with pacing strategy generator).

### Out of scope
- Direct app-library access (no Strava OAuth, no Garmin Connect API). Riders export their data themselves and feed it in.
- Pacing plans that account for weather / wind / temperature. Weather data is a separate problem; could be a future addition once a clean stateless weather-API integration is found.
- Multi-rider analysis (compare two riders' activities). Out of scope under strict statelessness — no per-rider context to compare against.
- Coaching prescriptions (*"do this workout next"*). Generating pacing for a route is fine; recommending what to do tomorrow crosses into AI Coach territory that lives in the `your-trainer` app, not the MCP.

## Acceptance
- [ ] Pacing strategy generator produces valid plans for ≥5 canonical GPX routes; outputs exportable to `.ytw` + FIT-workout.
- [ ] Privacy tool produces cleaned FIT/GPX files that import cleanly into Strava / Garmin Connect / Komoot.
- [ ] Library migration helper end-to-end test: LLM orchestrates conversion of 10 TrainerRoad ERG files → 10 valid Zwift ZWO files via the plan + batch ops + validators.
- [ ] Roundtrip test harness produces correct loss reports for ZWO ⟷ ERG, ZWO ⟷ FIT-workout, GPX ⟷ TCX canonical pairs.
- [ ] All tools stateless: code audit confirms no input data retained beyond the call.

## Links
- Phase: [[PHASE-001-Initial-Launch]]
- Tasks: see `plan/tasks/` and the linked TASK-* IDs in frontmatter.
