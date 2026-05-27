---
type: "[[task]]"
id: TASK-0008
aliases: ["TASK-0008"]
title: "MCP server architecture ADR + framework choice"
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

# TASK-0008 — MCP server architecture ADR + framework choice

Decision task. ADR covering: language (Python with `fastmcp` vs TypeScript with the official MCP SDK), transport (SSE over HTTPS recommended for self-hosted public servers), URL structure (subdomain `mcp.your-applications.com` vs subpath under main domain), alignment with PHASE-004 FEAT-0017's MCP framework choice (recommend: same runtime + framework, two servers). Output an ADR.

## Acceptance
- [ ] ADR drafted, reviewed, accepted (next available ADR number — likely ADR-0005).
- [ ] Framework choice committed; skeleton MCP server scaffolded in the sibling repo.
- [ ] Alignment confirmed with PHASE-004 FEAT-0017 TASK-0065 — same runtime + framework if possible.
