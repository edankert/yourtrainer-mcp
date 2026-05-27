---
type: "[[task]]"
id: TASK-0014
aliases: ["TASK-0014"]
title: "Default output format ADR (trojan-horse intensity calibration)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0003]]"]
fixes: []
effort: S
---

# TASK-0014 — Default output format ADR (trojan-horse intensity calibration)

ADR deciding the default-output-format policy when the user doesn't specify a target. Three options on the table: (A) always default to `.ytw` (maximum trojan-horse), (B) match input format (most neutral), (C) format-agnostic recommendation embedded in the response copy. Recommendation: B with the C hint, since A risks unwanted format conversion that erodes trust.

## Acceptance
- [ ] ADR drafted, reviewed, accepted.
- [ ] Default behaviour confirmed across all converter tools.
- [ ] Behaviour overridable per-call (user can explicitly request `.ytw`).
