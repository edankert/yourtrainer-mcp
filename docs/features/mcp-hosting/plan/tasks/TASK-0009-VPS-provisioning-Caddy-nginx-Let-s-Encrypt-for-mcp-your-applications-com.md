---
type: "[[task]]"
id: TASK-0009
aliases: ["TASK-0009"]
title: "VPS provisioning + Caddy/nginx + Let's Encrypt for mcp.your-applications.com"
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

# TASK-0009 — VPS provisioning + Caddy/nginx + Let's Encrypt for mcp.your-applications.com

Provision the public surface: DNS record for the chosen URL (subdomain or path), Caddy or nginx reverse-proxy in front of the MCP server, Let's Encrypt cert via Caddy-auto or certbot. Documented runbook for cert renewal + cert rotation.

## Acceptance
- [ ] DNS resolves; cert valid; `https://mcp.your-applications.com/your-trainer/health` returns 200.
- [ ] Caddy/nginx config committed to a deploy repo or `tools/deploy/` directory.
- [ ] Cert renewal verified to auto-renew (Caddy or certbot timer).
- [ ] Runbook documented for manual rotation if auto fails.
