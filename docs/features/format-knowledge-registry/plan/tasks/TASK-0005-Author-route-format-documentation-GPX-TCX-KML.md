---
type: "[[task]]"
id: TASK-0005
aliases: ["TASK-0005"]
title: "Author route format documentation (GPX + TCX + KML)"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0001]]"]
fixes: []
effort: M
---

> **Done 2026-05-29 (CHG-20260529-05, [[TST-0005]]).** specs/gpx.json + tcx.json + kml.json: route/activity XML formats with examples, constraints (coord order, extensions), conversion notes.

# TASK-0005 — Author route format documentation (GPX + TCX + KML)

Document the three route formats. GPX 1.1 is the universal baseline; TCX is Garmin's training-flavoured XML; KML is Google's geo-format (Google Earth). All three cover tracks with timestamps + elevation + optional HR/cadence streams. Documentation covers the dialect variants (Strava-stripped TCX, Garmin-extended GPX).

## Acceptance
- [ ] `specs/gpx/spec.md`, `specs/tcx/spec.md`, `specs/kml/spec.md`.
- [ ] ≥3 canonical examples per format.
- [ ] `constraints.json` per format (which apps accept extensions, which strip them).
- [ ] Conversion-notes matrix covering the practical pairs (GPX ⟷ TCX, GPX ⟷ FIT-route, TCX ⟷ FIT-route).
