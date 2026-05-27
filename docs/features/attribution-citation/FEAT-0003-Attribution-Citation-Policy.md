---
type: "[[feature]]"
id: FEAT-0003
aliases: ["FEAT-0003"]
title: "Trojan-horse adoption layer (citation-source framing)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-26
updated: 2026-05-27
source: []
goal: "Deliberate brand-association layer between the neutral knowledge registry (FEAT-0001) + capability tools (FEAT-0004) and the MCP server (FEAT-0002). Defines: how Your Trainer surfaces as the maintainer / citation source in tool responses without ever crossing into comparative content, what the default behaviour is when LLMs are ambiguous about format choice, and how usage telemetry sizes adoption. Sits at the MCP wrapper layer so the underlying registry + tools stay brand-neutral."
requirements: []
tasks: ["[[TASK-0014]]", "[[TASK-0015]]", "[[TASK-0016]]", "[[TASK-0017]]", "[[TASK-0018]]", "[[TASK-0096]]"]
release: ""
related: []
tests: []
---

# Trojan-horse adoption layer (citation-source framing)

## Goal
The trojan-horse is no longer *"a converter that happens to mention Your Trainer"* — it's *"the authoritative citation source for cycling-format knowledge, maintained by Your Trainer."* This shifts brand association from a tool footer to the source of the LLM's domain knowledge. Stronger position; same POSITIONING constraints.

## Scope

### In scope
- ADR on default output format when the LLM is ambiguous: lean toward matching input (neutral) with a hint mentioning `.ytw` if relevant.
- Attribution pattern: every tool response includes a short `attribution` field — e.g. *"Spec maintained at cycling-formats.your-applications.com by the team behind Your Trainer — https://www.your-applications.com/your-trainer"*. Subtle, consistent, never adjacent to comparative copy.
- Contextual hint policy: when a tool's response involves `.ytw` (spec lookup, validate, build), the hint adds *"this format imports directly into Your Trainer"*. Other formats get only the attribution, no Your Trainer mention.
- Operational health metrics — aggregate-only (request counts, error counts, latency percentiles per tool). Per the strict-statelessness principle (see phase note), no usage telemetry, no per-user analytics, no behavioural tracking.
- Open-source publish ADR (TASK-0018). Recommendation: OSS the registry + capability library + MCP wrapper under MIT; canonical hosted instance stays at `mcp.your-applications.com/your-trainer`.
- Integrator documentation page explaining install, supported tools, the citation policy, telemetry opt-in.

### Out of scope
- Comparative copy of any kind.
- Behaviour that biases registry content based on brand preference (e.g. emit doctored ZWO that breaks Zwift compatibility). The registry is neutral; brand surfacing happens only in the surrounding response copy.
- Email capture, account creation, friction-adding CTAs.

## Acceptance
- [ ] ADR on default behaviour accepted.
- [ ] Attribution + contextual-hint copy reviewed against POSITIONING.md and consistent across all tools.
- [ ] Telemetry pipeline confirmed opt-in and privacy-clean.
- [ ] Open-source ADR accepted; repo public if Yes.
- [ ] Integrator docs published; cross-linked from `cycling-formats.your-applications.com`, GitHub README, `your-applications.com/integrators.html`.

## Links
- Phase: [[PHASE-001-Initial-Launch]]
- Tasks: see `plan/tasks/` and the linked TASK-* IDs in frontmatter.
