---
type: "[[task]]"
id: TASK-0012
aliases: ["TASK-0012"]
title: "Wire FEAT-0001 library functions as MCP tools"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0002]]"]
fixes: []
effort: L
---

# TASK-0012 — Wire FEAT-0001 library functions as MCP tools

Thin MCP tool wrappers around each library function. Tools take base64-encoded input bytes + target format, return base64-encoded output bytes + metadata. Stateless. Each tool documented with the MCP `description` field (used by clients to surface in tool lists).

## Acceptance
- [ ] One MCP tool per FEAT-0001 library function (target: ≥10 tools).
- [ ] All tools callable from Claude Desktop; tool descriptions render correctly in the UI.
- [ ] Sample invocations confirmed end-to-end (upload canonical ZWO → receive canonical `.ytw`).
- [ ] Tool schemas validated; bad inputs return structured errors not 500s.
