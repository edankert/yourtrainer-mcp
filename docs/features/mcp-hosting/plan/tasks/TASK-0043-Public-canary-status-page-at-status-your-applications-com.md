---
type: "[[task]]"
id: TASK-0043
aliases: ["TASK-0043"]
title: "Public canary + status page at status.your-applications.com"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0002]]"]
fixes: []
effort: M
---

# TASK-0043 — Public canary + status page at status.your-applications.com

Continuous smoke tests against the production MCP, plus a public status page. Two purposes: (a) early-warning when the MCP degrades in production; (b) integrators (especially upstream Your Trainer FEAT-0086) need a programmatic signal to know when to fall back. Public status page also builds trust.

Layer 6 of the testing strategy.

## Acceptance
- [ ] Cron-driven smoke script runs every 5 minutes: hits representative tool from each layer (knowledge / capability / workflow / library), asserts response shape + correctness against a fixed sample.
- [ ] Per-tool status published to a static-generated page at `status.your-applications.com` — green/red per tool, latency p50/p95, last-checked timestamp.
- [ ] Machine-readable status JSON at `status.your-applications.com/api/status.json` — consumable by integrators (FEAT-0086 tool router can poll it).
- [ ] Historical uptime visible (last 30 days).
- [ ] Page styled cleanly; no marketing chrome.
- [ ] Cross-linked from the integrator docs (FEAT-0003 TASK-0096) and the GitHub README.
