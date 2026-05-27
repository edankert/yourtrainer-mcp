---
type: "[[feature]]"
id: FEAT-0004
aliases: ["FEAT-0004"]
title: "Cycling capability tools (binary + math + linting)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
goal: "Build the narrow set of cycling-data tools that LLMs genuinely cannot do alone. Binary FIT read/write (Garmin SDK-backed), time-series calculations (NP/IF/TSS, peak power curves), workout-from-structured-intent builders, app-acceptance checkers, structure linters, and batch operations. Together with the FEAT-0001 knowledge registry, this gives LLMs full domain capability without us duplicating text-to-text conversion work the LLM does natively."
requirements: []
tasks: ["[[TASK-0019]]", "[[TASK-0020]]", "[[TASK-0021]]", "[[TASK-0022]]", "[[TASK-0023]]", "[[TASK-0024]]", "[[TASK-0025]]", "[[TASK-0026]]", "[[TASK-0027]]", "[[TASK-0028]]", "[[TASK-0033]]", "[[TASK-0035]]", "[[TASK-0036]]", "[[TASK-0037]]", "[[TASK-0046]]", "[[TASK-0047]]", "[[TASK-0050]]", "[[TASK-0051]]", "[[TASK-0052]]", "[[TASK-0053]]", "[[TASK-0054]]"]
release: ""
related: []
tests: []
---

# Cycling capability tools (binary + math + linting)

## Goal
The other half of the LLM gap. Where the knowledge registry (FEAT-0001) gives the LLM authoritative reference material, this feature gives it the operations it cannot perform itself:

- **Binary formats** — FIT is bytes; LLMs see opaque payloads. Tool reads and emits FIT-workout + FIT-activity.
- **Calculation on time series** — NP, IF, TSS, time-in-zone, peak power curves. Math-heavy operations on per-second data points. LLM math on time series is unreliable.
- **Structured-intent authoring** — deterministic workout builder. Takes `{warmup, intervals, cooldown}` JSON → emits valid ZWO + FIT + `.ytw`. More reliable than LLM authoring because intent is structured, output deterministic.
- **Constraint-aware validation** — given a workout file, checks acceptance against the per-app constraints catalogue from FEAT-0001.
- **Linting** — domain-aware static analysis. Flags suspicious patterns (V02 intervals with insufficient recovery, 0-watt segments that crash some apps, text events exceeding hardware limits).
- **Batch operations** — folder-of-files in → aggregated results out. The LLM-can't-loop-50-files gap.
- **Training-load math** — CTL / ATL / TSB curves from a folder of activities; HR–power decoupling for endurance-ride pace-quality assessment. Time-series math LLMs can't reliably do in-context.

## Scope

### In scope
- Capability tools scope ADR (what's in for v1, what's deferred to future phases).
- FIT-workout read/write (Garmin SDK Python or TS bindings).
- FIT-activity inspector → JSON summary with NP, IF, TSS, time-in-zone, peak power curve.
- Peak power curve calculator (1s, 5s, 30s, 1min, 5min, 20min, 60min mean-max).
- Workout builder from structured intent (JSON → ZWO + FIT + `.ytw`).
- App-acceptance checker (consumes FEAT-0001 constraints catalogue).
- Workout structure linter.
- Batch operations adapter.
- Training-load curve (CTL / ATL / TSB) from a folder of activities.
- HR–power decoupling for endurance rides.
- Workout decomposition (file → structured intent — symmetric inverse of the builder).
- Workout scaling (duration / FTP / intensity).
- Lap / interval auto-detection on unstructured activities.
- Lightweight file inspector + format detection.
- FTP detection from a ride (multiple methods, auto-selected).
- Power Duration Curve / mFTP fitting (CP, W', stamina — WKO5-style).
- Workout difficulty score (multi-zone breakdown).
- Recovery time estimator (composes training-load math).
- Cadence analysis (distribution, dead-spots, drift).
- HR drift / aerobic threshold estimator (MAF-style).
- Single-ride segment efforts (local peak-effort detection).

### Out of scope (v1 — future phase candidates)
- Strava OAuth pull. Real protocol integration; deserves its own design pass.
- BLE direct push to cycling computers. Hardware access; large scope.
- TrainingPeaks workout library API.
- Vision-language pre-processor (screenshot → ZWO via OCR). Different stack.
- Activity privacy / anonymisation (strip GPS-start, strip personal data). High-value but separate scope.

## Acceptance
- [ ] FIT-workout read/write working; round-trips canonical Garmin samples without semantic loss.
- [ ] NP/IF/TSS values validated against TrainingPeaks reference numbers for ≥5 canonical activities.
- [ ] Peak power curve calculated correctly against canonical FIT activity samples.
- [ ] Workout builder produces valid ZWO + FIT + `.ytw` from structured intent; outputs round-trip through their respective parsers.
- [ ] App-acceptance checker consumes the FEAT-0001 constraints catalogue and returns correct accept/reject/warn per app for ≥5 sample workout files.
- [ ] Workout structure linter catches ≥10 documented domain-rule violations on test fixtures.
- [ ] Batch operations adapter handles folders of ≥100 files without memory blow-up.

## Links
- Phase: [[PHASE-001-Initial-Launch]]
- Tasks: see `plan/tasks/` and the linked TASK-* IDs in frontmatter.
