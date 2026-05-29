---
type: "[[task]]"
id: TASK-0009
aliases: ["TASK-0009"]
title: "VPS provisioning + Caddy/nginx + Let's Encrypt for mcp.your-applications.com"
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

# TASK-0009 — VPS provisioning + Caddy/nginx + Let's Encrypt for mcp.your-applications.com

Provision the public surface: DNS record for the chosen URL (subdomain or path), Caddy or nginx reverse-proxy in front of the MCP server, Let's Encrypt cert via Caddy-auto or certbot. Documented runbook for cert renewal + cert rotation.

## Acceptance
- [ ] DNS resolves; cert valid; `https://mcp.your-applications.com/your-trainer/health` returns 200.
- [ ] Caddy/nginx config committed to a deploy repo or `tools/deploy/` directory.
- [ ] Cert renewal verified to auto-renew (Caddy or certbot timer).
- [ ] Runbook documented for manual rotation if auto fails.

> **Done 2026-05-29 (CHG-20260529-17).** Provisioned on the existing Ubuntu 24.04 VPS (76.13.51.7). nginx already owned :80/:443 serving other sites, so used **nginx** (not Caddy): isolated vhost `mcp.your-applications.com` -> 127.0.0.1:8080 (deploy/nginx-mcp.conf), **Let's Encrypt via certbot** (auto-renew). systemd service `yourtrainer-mcp` enabled + active. Existing sites untouched (nginx -t before reload). Live + TLS-valid; privacy hardening applied (no body/IP/per-call logging).
