---
type: "[[task]]"
id: TASK-0013
aliases: ["TASK-0013"]
title: "File transfer protocol design (base64 in MCP args vs URL-handoff)"
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

# TASK-0013 — File transfer protocol design (base64 in MCP args vs URL-handoff)

Decision + implementation. v1: base64-encode input/output in tool args/return (works because workout files are KB-range; routes can be MB but still tractable). Revisit URL-handoff if real-world usage hits MCP payload-size limits. Document the call/return shape in tool descriptions and integrator docs.

## Acceptance
- [ ] Decision documented (likely as a section in TASK-0008 ADR, or its own micro-ADR).
- [ ] Base64 encoding/decoding handled cleanly in all tools.
- [ ] Tool descriptions explain how to pass files (with code examples).
- [ ] Payload-size limit documented; tools return clean error if exceeded.
