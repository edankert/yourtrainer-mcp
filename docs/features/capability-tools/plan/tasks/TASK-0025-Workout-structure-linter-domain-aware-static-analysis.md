---
type: "[[task]]"
id: TASK-0025
aliases: ["TASK-0025"]
title: "Workout structure linter (domain-aware static analysis)"
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

> **Done 2026-05-29 (CHG-20260529-02, [[TST-0002]]).** lint_workout — domain-aware static analysis (warmup/cooldown, durations, power ranges, cadence, rep counts).

# TASK-0025 — Workout structure linter (domain-aware static analysis)

Given a workout, runs domain-aware static analysis. Flags: V02 intervals with insufficient recovery, 0-watt segments that crash some apps, abnormally short warmups for high-intensity work, suspicious cadence targets (cadence > 130 or < 50), text events with unusual characters, missing cool-downs after sustained efforts.

## Acceptance
- [ ] ≥10 documented domain rules implemented.
- [ ] Each rule has: rule ID, severity (info/warning/error), description, suggested fix.
- [ ] Test fixtures cover all rules.
- [ ] Linter output structured (JSON), not just human prose.
