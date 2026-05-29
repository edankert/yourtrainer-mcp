---
type: "[[task]]"
id: TASK-0035
aliases: ["TASK-0035"]
title: "Workout scaling (duration / FTP / intensity)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0004]]"]
fixes: []
effort: M
---

> **Done 2026-05-29 (CHG-20260529-02, [[TST-0002]]).** scale_workout — duration / intensity factors (FTP-rescale is a no-op since power is stored as a fraction of FTP).

# TASK-0035 — Workout scaling (duration / FTP / intensity)

Tool that scales an existing workout by one of three parameters: target duration (minutes), target FTP rebase, or target intensity factor. Common AI-Coach request: *"give me a 30-min version of this 60-min workout"*. Today the AI does this freehand and produces inconsistent results (sometimes proportional scale, sometimes drops an interval, sometimes truncates). Deterministic scaling rules belong in a tool. Composes TASK-0033 (decompose) + scaling transform + TASK-0023 (build).

## Acceptance
- [ ] Tool accepts: input workout file + one of `{target_duration_min, target_ftp, target_intensity_factor}`.
- [ ] Duration scaling: proportional warmup/cooldown shrinkage; intervals scaled by count or duration based on a documented rule (config-driven; rule choice in the response).
- [ ] FTP rebase: all `%FTP` targets rebased; absolute-watt targets recomputed.
- [ ] Intensity-factor scaling: all targets uniformly scaled to hit the target IF.
- [ ] Output validates via TASK-0061 validator.
- [ ] Test fixtures: ≥10 scaling scenarios with expected outputs.
- [ ] Stateless.
