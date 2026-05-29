---
type: "[[adr]]"
id: ADR-0002
title: "Open-source the library + MCP wrapper under MIT; hosted instance canonical"
status: accepted
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0018]]"]
decision: "Publish the knowledge-registry corpus and capability library + MCP wrapper as a public GitHub repo under the MIT licence. The hosted instance at mcp.your-applications.com/your-trainer remains the canonical service (Plausible/Mastodon model)."
context: "The trojan-horse adoption strategy is attribution-in-the-docs; OSS amplifies rather than dilutes it."
alternatives: ["Keep closed-source", "OSS the corpus only, keep capability code private", "Permissive-but-not-MIT (Apache-2.0)"]
consequences: ["Lowers adoption friction; invites domain contributors.", "Forking risk is low because the hosted instance + attribution are the value.", "Adds OSS maintenance burden — tracked by RISK-0002."]
supersedes: ""
superseded: ""
related: ["[[TASK-0018]]", "[[FEAT-0003]]", "[[RISK-0002]]"]
---

# Open-source publication

## Context
FEAT-0003's adoption strategy is to become *the authoritative cycling-format reference the LLM cites*. That leverage comes from attribution carried in the docs and tool responses — which works **better**, not worse, when the corpus is open. The PHASE-001 phase note already recommends OSS; this ADR formalises it.

## Decision
- **Open-source** the knowledge-registry corpus and the capability library + MCP wrapper.
- **Licence: MIT** — maximally permissive, lowest adoption friction, consistent with the README and CLAUDE.md framing.
- **The hosted instance stays canonical.** `mcp.your-applications.com/your-trainer` is the service we operate and attribute; the repo is the reference implementation anyone can self-host (Plausible / Mastodon model).
- **Repo is public on GitHub** from first push.

## Alternatives
- **Closed-source** — contradicts the trojan-horse strategy; nothing to cite or contribute to.
- **Corpus-only OSS** — splits the project, complicates the build, and the capability code is the part contributors can most help harden.
- **Apache-2.0** — fine, but MIT is already the stated intent and is lighter-weight for a docs-heavy project; no patent surface that motivates Apache here.

## Consequences
- Adoption friction drops; domain experts can correct format docs via PRs.
- Forking risk is low: the value is the hosted instance + attribution, not the code.
- OSS maintenance burden is real — governed by **RISK-0002**; a `MAINTAINERS.md` / contribution expectations doc is a follow-up (not blocking first publication).
