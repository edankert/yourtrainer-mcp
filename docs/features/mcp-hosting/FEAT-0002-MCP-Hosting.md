---
type: "[[feature]]"
id: FEAT-0002
aliases: ["FEAT-0002"]
title: "MCP server + VPS hosting (both layers)"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-26
updated: 2026-05-27
source: []
goal: "Deploy and operate the MCP server that exposes FEAT-0001's knowledge-registry tools AND FEAT-0004's capability tools through a single endpoint at mcp.your-applications.com/your-trainer. Self-hosted on Edwin's VPS. Reliable uptime, low operational overhead, monitorable, reproducible from infrastructure-as-code."
requirements: []
tasks: ["[[TASK-0008]]", "[[TASK-0009]]", "[[TASK-0010]]", "[[TASK-0011]]", "[[TASK-0012]]", "[[TASK-0013]]", "[[TASK-0042]]", "[[TASK-0043]]", "[[TASK-0044]]", "[[TASK-0064]]", "[[TASK-0065]]"]
release: ""
related: []
tests: []
---

# MCP server + VPS hosting (both layers)

## Goal
Single MCP server endpoint exposing both layers of the PHASE-001 surface:
- Knowledge tools (FEAT-0001) — `get_format_spec`, `validate`, etc. Read-only access to the registry corpus.
- Capability tools (FEAT-0004) — FIT read/write, NP/IF/TSS calculation, workout building, linting, batch operations.

Same hosting infrastructure; tool descriptions distinguish the layers for LLM clients.

## Scope

### In scope
- ADR covering: language (Python with `fastmcp` vs TypeScript with the official SDK), MCP transport (SSE over HTTPS recommended), URL structure (subdomain vs subpath), alignment with PHASE-004 FEAT-0017's MCP framework choice.
- VPS provisioning + Caddy or nginx + Let's Encrypt for `mcp.your-applications.com`.
- systemd unit + log rotation + restart-on-failure.
- Monitoring: external uptime check; error-rate alerting.
- MCP tool wrappers exposing both FEAT-0001 knowledge tools and FEAT-0004 capability tools.
- File transfer protocol for the capability layer (base64-in-MCP-args for v1; revisit URL-handoff if size limits hit).
- MCP protocol conformance tests (`mcp-cli` / `mcp-inspector` in CI) + real-client integration runbook covering Claude Desktop, Cursor, custom SDK scripts.
- Public canary + status page at `status.your-applications.com` — continuous smoke tests against production MCP, machine-readable status JSON for integrators (FEAT-0086 tool router consumes this for fall-back signalling).
- Performance baselines + regression detection (pytest-benchmark; CI flags >20% regression).

### Out of scope
- User authentication. All tools public read/transform.
- Per-user state, history, or quotas.
- A web frontend on the same domain.
- Multi-region deployment.

## Acceptance
- [ ] ADR drafted, reviewed, accepted.
- [ ] MCP server reachable at the canonical URL; TLS via Let's Encrypt; systemd-supervised.
- [ ] All FEAT-0001 knowledge tools AND FEAT-0004 capability tools exposed.
- [ ] `/health` endpoint returning 200 OK + library version; monitored externally.
- [ ] Documented runbook for redeployment + cert renewal.
- [ ] 30-day post-launch uptime ≥99%.

## Links
- Phase: [[PHASE-001-Initial-Launch]]
- Tasks: see `plan/tasks/` and the linked TASK-* IDs in frontmatter.
