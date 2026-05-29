---
type: "[[task]]"
id: TASK-0016
aliases: ["TASK-0016"]
title: "Contextual hint integration in tool responses"
status: done
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-29
source: []
implements: ["[[FEAT-0003]]"]
fixes: []
effort: S
---

> **Done 2026-05-29 (CHG-20260529-07).** attach_attribution wired into every MCP tool response; .ytw hint only on .ytw-producing tools.

# TASK-0016 — Contextual hint integration in tool responses

Wire the attribution + hint strings into the MCP wrapper response shape. Each response includes `attribution` (always) and `hint` (conditional on output format). Clients (Claude Desktop etc.) surface these to the user as part of the tool result.

## Acceptance
- [ ] Wrapper code reads attribution + hint strings from the config (TASK-0015 deliverable).
- [ ] Response shape documented; both fields present and rendered by Claude Desktop.
- [ ] Manual end-to-end test: convert ZWO → `.ytw` → see hint; convert ZWO → ERG → see only attribution.
