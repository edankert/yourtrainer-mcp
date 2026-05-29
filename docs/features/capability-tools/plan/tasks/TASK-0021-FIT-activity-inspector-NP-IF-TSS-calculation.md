---
type: "[[task]]"
id: TASK-0021
aliases: ["TASK-0021"]
title: "FIT-activity inspector + NP/IF/TSS calculation"
status: doing
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: L
---

# TASK-0021 — FIT-activity inspector + NP/IF/TSS calculation

Read a recorded ride (FIT-activity), emit a structured JSON summary: duration, distance, elevation gain, peak power, average power, NP (normalised power, Coggan's 30s-rolling-mean-fourth-root), IF (intensity factor = NP/FTP), TSS (training-stress score = (duration × NP × IF) / (FTP × 3600) × 100), time-in-zone breakdown, peak HR, average HR, peak cadence, average cadence, average speed.

## Acceptance
- [~] Reads FIT, TCX, GPX activity files. TCX + GPX implemented & tested (stdlib);
  FIT implemented via the optional `fitparse` extra but not yet covered by a fixture.
- [x] Emits structured JSON summary with documented schema (`activity.inspect_activity`).
- [~] NP / IF / TSS validated: canonical anchors hold in unit tests (constant ⇒ NP==power;
  1 h at FTP ⇒ IF 1.0 / TSS 100; variable ⇒ NP>avg). TrainingPeaks ≥5-activity corpus
  pending [[TASK-0045]].
- [~] Time-in-zone breakdown by FTP (Coggan 7-zone default). Selectable zone presets pending.

> **In progress 2026-05-29 (CHG-20260529-01).** Engine + TCX/GPX inspector landed and
> verified by [[TST-0001]]. Remaining for `done`: FIT fixtures, TP reference corpus
> ([[TASK-0045]]), configurable zone presets.
