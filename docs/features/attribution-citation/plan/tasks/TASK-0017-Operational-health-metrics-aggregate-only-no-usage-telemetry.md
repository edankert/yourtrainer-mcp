---
type: "[[task]]"
id: TASK-0017
aliases: ["TASK-0017"]
title: "Operational health metrics (aggregate-only, no usage telemetry)"
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

# TASK-0017 — Operational health metrics (aggregate-only, no usage telemetry)

Per the strict-statelessness principle in the PHASE-001 phase note, no usage telemetry is captured. The MCP server emits only **operational health metrics** for monitoring: aggregate request counts, error counts, latency percentiles (p50 / p95 / p99), per-tool error rates. These are aggregate counters — no per-call records, no per-rider tracking, no IP retention beyond rate-limit buckets, no input file contents in logs.

Distinction worth being explicit about:
- ✅ *"Tool `validate` received 487 calls today, returned 12 errors, p95 latency 230ms"* — aggregate, operational, fine.
- ❌ *"User X validated workout Y at 14:32"* — per-user, behavioural, ruled out.

## Acceptance
- [ ] Aggregate Prometheus-compatible metrics emitted: `mcp_requests_total`, `mcp_errors_total`, `mcp_latency_seconds` (with `tool` label).
- [ ] Per-tool counters: invocation count, error count.
- [ ] No per-user, per-IP, or per-file analytics in metrics or logs.
- [ ] Audit pass: confirm no input file contents in operational logs (error logs include error type + stack trace but not request payload).
- [ ] Private metrics dashboard (Edwin only) for operational health — no public analytics surface.
