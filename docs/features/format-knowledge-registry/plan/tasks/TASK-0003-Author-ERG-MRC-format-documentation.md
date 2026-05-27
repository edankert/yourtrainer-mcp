---
type: "[[task]]"
id: TASK-0003
aliases: ["TASK-0003"]
title: "Author ERG/MRC format documentation"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

# TASK-0003 — Author ERG/MRC format documentation

Document the CompuTrainer-era ERG and MRC workout formats. Both are minute-by-minute power (ERG = absolute watts; MRC = %FTP). Documentation includes the dialect differences across consumers (TrainerRoad legacy, PerfPro, ERG Editor) and the ramp-interpolation gotcha.

## Acceptance
- [ ] `specs/erg/spec.md` and `specs/mrc/spec.md` covering syntax + header conventions.
- [ ] ≥3 canonical examples per format.
- [ ] `constraints.json` covers ≥3 consuming apps.
- [ ] Conversion notes for ERG → ZWO and MRC → ZWO with ramp-interpolation details.
