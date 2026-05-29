---
type: "[[adr]]"
id: ADR-0006
title: "Your Trainer content via stateless website proxy; product Q&A in the ecosystem MCP"
status: accepted
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
decision: "The MCP fetches public Your Trainer content (workout library, AI-skill catalogue, manual) from the website over HTTP with a short TTL cache; product-manual Q&A is hosted in this ecosystem MCP rather than the PHASE-004 server."
context: "Content is maintained on the website; the user asked the MCP to serve the library/skills/manual and answer manual questions here."
alternatives: ["Bundle content in the MIT package", "Load content from a private deploy path", "Put manual Q&A in the PHASE-004 Your-Trainer MCP"]
consequences: ["Single source of truth stays on the website; MCP stays stateless (public content only).", "Adds a website runtime dependency (RISK-0004).", "Blurs the PHASE-001/004 ecosystem-vs-product boundary by design."]
supersedes: ""
superseded: ""
related: ["[[FEAT-0007]]", "[[RISK-0004]]", "[[PHASE-001-Initial-Launch]]"]
---

# Content via stateless website proxy; product Q&A in the ecosystem MCP

## Context
Per the user, the curated workout library, the in-app AI-assistant skill
catalogue, and the product manual are hosted on `your-applications.com`. They
asked the MCP to (a) serve the library + skills and (b) answer Your Trainer
questions from the manual — explicitly in this (ecosystem) MCP.

## Decision
- **Fetch public content from the website over HTTP** (stdlib `urllib`, no new
  dependency) with a short in-process **TTL cache of public content only**.
  The website remains the single source of truth; the MCP is a stateless proxy.
- **Host product-manual Q&A in this ecosystem MCP.** This consciously crosses
  the PHASE-001 (ecosystem) vs PHASE-004 (Your-Trainer-specific) boundary the
  phase note drew; accepted because they share runtime/infra and the user wants
  one endpoint.
- The workout library has a JSON manifest contract; **skills/manual are parsed
  from HTML** for now (a website JSON endpoint would be more robust — future).

## Alternatives
- **Bundle content in the MIT package** — would duplicate/aged content and force
  republish on every content change; rejected (website is the source of truth).
- **Private deploy-path content** — unnecessary; the content is already public.
- **Manual Q&A in the PHASE-004 server** — cleaner separation, but the user
  chose one endpoint.

## Consequences
- Statelessness preserved (no rider data cached).
- New **website runtime dependency** — content tools degrade if the site is
  down; format/capability tools are unaffected (RISK-0004).
- A future website JSON contract for skills/manual should replace HTML parsing.
