---
type: "[[change]]"
id: CHG-20260529-17
title: "Production deploy: MCP live at mcp.your-applications.com/your-trainer"
status: merged
owner: user:edwin
created: 2026-05-29
updated: 2026-05-29
source: []
commit: ""
pr: ""
impacts: ["mcp-hosting", "deploy", "privacy"]
issues: []
features: ["[[FEAT-0002]]"]
related: ["[[TASK-0009]]", "[[TASK-0010]]", "[[TASK-0012]]", "[[TASK-0064]]", "[[RISK-0001]]"]
---

# Production deploy

## Summary
Deployed the MCP server live at **https://mcp.your-applications.com/your-trainer**.

Environment differed from the assumed Caddy setup: the VPS (Ubuntu 24.04,
76.13.51.7) already runs **nginx** serving other sites on :80/:443 with
Let's Encrypt certs managed externally. Adapted accordingly:

- **App + service:** created `ytmcp` system user; cloned the repo to
  `/opt/yourtrainer-mcp`; venv + `pip install .`; installed
  `deploy/yourtrainer-mcp.service` → systemd service **active + enabled**
  (auto-start on boot), bound to `127.0.0.1:8080`.
- **Reverse proxy:** used **nginx** (not Caddy — port clash). Added an isolated
  vhost `deploy/nginx-mcp.conf` for `mcp.your-applications.com` → `127.0.0.1:8080`
  with SSE-safe proxy settings; `nginx -t` before a graceful reload; existing
  vhosts untouched.
- **TLS:** installed certbot + obtained a Let's Encrypt cert for `mcp`
  (HTTP-01, grey-cloud direct origin per the DNS decision); certbot timer
  auto-renews. (DNS for `mcp` was created in Cloudflare as DNS-only / grey cloud.)
- **Privacy hardening applied live** (TASK-0064 invariant): nginx logs no request
  bodies and no client IPs (`access_log off`); uvicorn's per-request access log
  disabled via `uvicorn_config={"access_log": False}`. Aggregate `get_health`
  remains the only operational signal.

## Verification (live)
- TLS: publicly-trusted LE cert, CN `mcp.your-applications.com` (curl without -k).
- HTTP → HTTPS 301 redirect.
- `initialize` over the public HTTPS endpoint returns `serverInfo: yourtrainer-mcp`.
- `deploy/healthcheck.sh` against the public URL: OK.
- Journal after a request: **no per-request access line** (only the startup banner).

## Documentation Coverage (All Types Considered)
- features: updated (FEAT-0002 deployed; monitoring/status still open)
- tasks: updated (TASK-0009 → done)
- decisions: not-applicable (deploy choice recorded here)
- risks: RISK-0001 — live deploy; data-at-rest surface minimised (privacy hardening)
- changes: new (this note)
- snapshot: updated (TASK-0009 done, active_wave = DEPLOYED LIVE)

## Remaining (FEAT-0002)
- **TASK-0011** monitoring/alerting — `healthcheck.sh` + `get_health` ready;
  needs a cron/uptime monitor + alert channel wired on the host.
- **TASK-0043** public status page — `deploy/status/` ready; needs a
  `status.your-applications.com` DNS record + vhost.
- 30-day ≥99% uptime is a time-based exit metric (PHASE-001).
