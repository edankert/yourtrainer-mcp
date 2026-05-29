---
type: "[[adr]]"
id: ADR-0004
title: "Default workout output format + intensity convention"
status: accepted
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0014]]"]
decision: "Default build output is ZWO; power is expressed as a fraction of FTP across the model and .ytw. .ytw is offered alongside and carries the Your Trainer contextual hint."
context: "The builder can emit ZWO, .ytw, or FIT; we need a sensible default and one intensity convention."
alternatives: ["Default to .ytw", "Default to absolute watts", "Default to FIT"]
consequences: ["Broad interoperability by default; FTP-relative model stays device-independent.", "Trojan-horse hint rides on .ytw output only, per POSITIONING."]
supersedes: ""
superseded: ""
related: ["[[TASK-0014]]", "[[FEAT-0003]]", "[[FEAT-0004]]"]
---

# Default workout output format + intensity convention

## Context
`build_workout_from_intent` can render ZWO, .ytw, or FIT. We need (a) a default
format when the caller doesn't specify one and (b) a single intensity
convention so build/scale/decompose/difficulty all agree.

## Decision
- **Default output: ZWO.** It is the most widely interoperable workout format
  and FTP-relative, so it imports cleanly across the ecosystem.
- **Intensity convention: fraction of FTP** (1.0 == FTP) everywhere in the
  workout model, ZWO, and .ytw. Absolute watts are only produced on conversion
  to ERG/FIT, where they are derived from a supplied FTP.
- **.ytw is a first-class alternate.** When the caller asks for `.ytw`, the
  response includes the Your Trainer contextual hint (POSITIONING: hint only on
  the format that imports into Your Trainer; never comparative).

## Alternatives
- **Default .ytw** — would privilege our own format as the default; we prefer
  the trojan-horse to be earned by usefulness, not defaulting.
- **Default absolute watts** — couples every workout to one rider's FTP.
- **Default FIT** — binary, less convenient as a default text deliverable.

## Consequences
- Callers get an interoperable artifact by default; `.ytw`/`fit` are explicit opt-ins.
- The FTP-relative model keeps difficulty scoring FTP-independent (see workout.py).
