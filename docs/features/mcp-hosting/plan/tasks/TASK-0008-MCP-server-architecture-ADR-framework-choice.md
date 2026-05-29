---
type: "[[task]]"
id: TASK-0008
aliases: ["TASK-0008"]
title: "MCP server architecture ADR + framework choice"
status: done
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
- [x] ADR drafted, reviewed, accepted — [[ADR-0001]] (Python + FastMCP, streamable-HTTP, subpath URL).
- [x] Framework choice committed; skeleton MCP server scaffolded (`src/yourtrainer_mcp/server.py`, boots over stdio + HTTP; `initialize` verified).
- [x] Alignment recorded with PHASE-004 FEAT-0017 TASK-0065 — same runtime + framework (two servers behind one host).

> **Closed 2026-05-29 (CHG-20260529-01).** See [[ADR-0001]].
