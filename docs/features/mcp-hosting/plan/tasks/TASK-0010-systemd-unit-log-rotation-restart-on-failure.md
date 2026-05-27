---
type: "[[task]]"
id: TASK-0010
aliases: ["TASK-0010"]
title: "systemd unit + log rotation + restart-on-failure"
status: backlog
phase: "[[PHASE-001-Initial-Launch]]"
owner: unassigned
created: 2026-05-27
updated: 2026-05-27
source: []
implements: ["[[FEAT-0002]]"]
fixes: []
effort: S
---

# TASK-0010 — systemd unit + log rotation + restart-on-failure

Wrap the MCP server in a systemd unit running as a non-root user. Configure log rotation via journald or a rotating file handler. Restart-on-failure with backoff. Documented in the deploy runbook.

## Acceptance
- [ ] Server runs under systemd as a dedicated non-root user.
- [ ] `systemctl status cycling-mcp` reports green.
- [ ] Crash recovery confirmed by manual kill + observation of restart.
- [ ] Logs accessible via `journalctl -u cycling-mcp` and rotated.
