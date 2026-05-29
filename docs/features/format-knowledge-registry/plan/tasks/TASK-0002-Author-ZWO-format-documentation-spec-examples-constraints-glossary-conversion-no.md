---
type: "[[task]]"
id: TASK-0002
aliases: ["TASK-0002"]
title: "Author ZWO format documentation (spec + examples + constraints + glossary + conversion notes)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: L
---

> **Done 2026-05-29 (CHG-20260529-05, [[TST-0005]]).** specs/zwo.json: grammar summary, 3 examples, constraints, conversion notes, glossary; served via get_format_* + validate('zwo').

# TASK-0002 — Author ZWO format documentation (spec + examples + constraints + glossary + conversion notes)

Author the full ZWO documentation corpus under `specs/zwo/`. Includes: `spec.md` (block types, attributes, XML structure, version history), `examples/` (≥3 canonical ZWO files: classic VO2max set, sweet-spot, free-ride with intervals), `constraints.json` (per-app limits: Zwift segment count, MyWhoosh quirks, TrainerRoad import behaviour), `glossary.json` (IntervalsT vs IntervalsP, FtpTest semantics, OnPower/OffPower), `conversion_notes/zwo_to_erg.md`, `conversion_notes/zwo_to_fit.md`.

## Acceptance
- [ ] `specs/zwo/spec.md` covers all common block types with examples.
- [ ] ≥3 canonical ZWO example files committed.
- [ ] `constraints.json` covers ≥4 ZWO-consuming apps.
- [ ] `glossary.json` covers ≥20 ZWO terms / attributes.
- [ ] Conversion notes for ZWO → ERG and ZWO → FIT-workout, with documented gotchas.
- [ ] Docs pass schema-validation step in CI.
