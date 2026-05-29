---
type: "[[risk]]"
id: RISK-0004
title: "Website runtime dependency for content tools (availability/latency)"
status: open
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
likelihood: medium
impact: medium
related: ["[[FEAT-0007]]", "[[ADR-0006]]"]
---

# RISK-0004 — Website runtime dependency for content tools

## Risk
The FEAT-0007 content tools (workout library, AI skills, manual Q&A) fetch from
`your-applications.com` at runtime. If the website is down/slow, those tools
fail or lag. HTML parsing for skills/manual is also brittle to markup changes.

## Mitigations
- Short in-process **TTL cache** (public content only) reduces fetches + smooths
  blips.
- Failures are **isolated**: only content tools are affected; the format
  knowledge registry and all capability/analysis tools are fully local and keep
  working.
- A **website JSON contract** for skills/manual (vs HTML scraping) would harden
  parsing — recommended follow-up.
- The workout library is already manifest-driven (stable JSON contract).

## Status
Open — accept for v1; revisit if content-tool error-rate is material in `get_health`.
