---
type: "[[task]]"
id: TASK-0042
aliases: ["TASK-0042"]
title: "MCP protocol conformance + real-client integration tests"
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

# TASK-0042 — MCP protocol conformance + real-client integration tests

Two distinct things: (a) automated MCP-protocol-conformance tests in CI using `mcp-cli` / `mcp-inspector` against the running server; (b) documented manual integration-test runbook covering the real-client matrix (Claude Desktop, Cursor, at least one custom SDK script).

Layer 3 + Layer 4 of the testing strategy. Without conformance tests, the server may work with one MCP client but break for others (different clients exercise different protocol corners). Without the client matrix, integrator-facing bugs only surface when integrators hit them.

## Acceptance
- [ ] CI step runs `mcp-cli` (or equivalent) against the test-mode MCP server on every PR; lists tools, calls representative ones, validates responses against the MCP schema.
- [ ] Manual integration-test runbook covers: Claude Desktop install + 5 sample tool calls; Cursor install + 3 sample tool calls; custom Anthropic-SDK script that exercises 10 tools end-to-end.
- [ ] Each client test documented with: install steps, sample prompts, expected results, known limitations.
- [ ] Runbook re-run before each MCP release as a release-gate.
- [ ] Conformance-test failures surface clearly: tool name, expected vs actual, MCP-spec section violated.
