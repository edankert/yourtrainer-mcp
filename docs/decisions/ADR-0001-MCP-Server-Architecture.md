---
type: "[[adr]]"
id: ADR-0001
title: "MCP server runtime + framework: Python + FastMCP, HTTP transport, subpath URL"
status: accepted
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: ["[[TASK-0008]]"]
decision: "Python 3.10+ with FastMCP; streamable-HTTP transport for the hosted server, stdio for local dev; served at the subpath mcp.your-applications.com/your-trainer."
context: "PHASE-001 must ship a self-hosted MCP server exposing a knowledge registry and capability tools."
alternatives: ["TypeScript + official MCP SDK", "Subdomain URL instead of subpath", "SSE-only transport"]
consequences: ["Capability tools can use the Python scientific/binary ecosystem (FIT parsing, time-series math).", "Aligns runtime with PHASE-004 FEAT-0017 for a uniform hosting story.", "Requires Python 3.10+ on the VPS."]
supersedes: ""
superseded: ""
related: ["[[TASK-0008]]", "[[FEAT-0002]]", "[[FEAT-0004]]"]
---

# MCP server runtime + framework

## Context
PHASE-001 ships a self-hosted MCP server at `mcp.your-applications.com/your-trainer` exposing two layers: a cycling-format knowledge registry (FEAT-0001) and a capability-tools layer (FEAT-0004). We must pick a language, an MCP framework, a transport, and a URL structure, and ideally align with PHASE-004 FEAT-0017 so hosting is uniform.

The capability layer is the constraining factor: it needs binary FIT read/write (Garmin/`fitparse` ecosystem) and time-series math (NP/IF/TSS, peak-power curves, CTL/ATL/TSB). Both are mature and idiomatic in Python and comparatively painful in the TypeScript ecosystem.

## Decision
- **Language/runtime:** Python, targeting **3.10+** (developed and CI-tested on 3.13).
- **Framework:** **FastMCP** — decorator-based tool registration, first-class stdio + streamable-HTTP transports, low ceremony.
- **Transport:** **streamable HTTP** over HTTPS for the hosted public server; **stdio** for local development and tests.
- **URL structure:** **subpath** `mcp.your-applications.com/your-trainer` (one MCP host can serve multiple servers by path; PHASE-004's server can live at a sibling subpath).
- **Build backend:** hatchling, `src/` layout, package `yourtrainer_mcp`.
- **Dependency posture:** keep the runtime dependency surface minimal. Power/time-series math is **pure-Python** (no numpy) for fast, hermetic CI. FIT binary support is an **optional extra** (`yourtrainer-mcp[fit]` → `fitparse`); TCX/GPX parse with the stdlib only.

## Alternatives
- **TypeScript + official MCP SDK** — strong protocol support, but the binary-FIT and sports-science math story is weak; would mean shelling out to Python anyway.
- **Subdomain per server** (`yt.mcp...`) — more DNS/cert overhead; subpath is simpler for a single VPS host.
- **SSE-only transport** — superseded by streamable HTTP in current MCP; no reason to start on the older transport.

## Consequences
- Capability tools draw on the Python ecosystem directly.
- VPS must provide Python 3.10+ (documented in the deploy artefacts under `deploy/`).
- Runtime stays lean: a clean install needs only FastMCP; `fitparse` is pulled in only when FIT support is wanted.
- Aligns with PHASE-004 FEAT-0017 TASK-0065 (same runtime + framework, two servers behind one host).
