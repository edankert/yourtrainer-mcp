# Deploying yourtrainer-mcp

Self-hosted deploy for `mcp.your-applications.com/your-trainer` (FEAT-0002).
Runtime per **ADR-0001**: Python 3.10+, FastMCP, streamable-HTTP behind a TLS
reverse proxy. The process is stateless — it needs no database, no writable
state, and no secrets.

## Prerequisites (VPS)
- Python 3.10+ (`python3 --version`).
- A reverse proxy with automatic TLS. This guide uses **Caddy**; an nginx +
  Let's Encrypt equivalent works the same way (proxy `/your-trainer*` →
  `127.0.0.1:8080`, disable response buffering for SSE).
- DNS: `mcp.your-applications.com` → the VPS IP.

## Install
```bash
sudo useradd --system --create-home --home-dir /opt/yourtrainer-mcp ytmcp
sudo -u ytmcp git clone https://github.com/edankert/yourtrainer-mcp.git /opt/yourtrainer-mcp
cd /opt/yourtrainer-mcp
sudo -u ytmcp python3 -m venv .venv
# add the FIT extra if FIT-binary support is wanted: ".[fit]"
sudo -u ytmcp .venv/bin/pip install .
```

## Service
```bash
sudo cp deploy/yourtrainer-mcp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now yourtrainer-mcp
sudo systemctl status yourtrainer-mcp
```

## Reverse proxy (Caddy)
```bash
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile   # or merge into an existing one
sudo systemctl reload caddy
```

## Verify
```bash
curl -s -X POST https://mcp.your-applications.com/your-trainer \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}'
```
Expect a `200` with `content-type: text/event-stream` and a JSON-RPC
`initialize` result naming `yourtrainer-mcp`.

## Upgrades
```bash
cd /opt/yourtrainer-mcp && sudo -u ytmcp git pull
sudo -u ytmcp .venv/bin/pip install .
sudo systemctl restart yourtrainer-mcp
```

## Monitoring + alerting (TASK-0011)
- **Liveness:** `deploy/healthcheck.sh` sends an MCP `initialize` and exits
  non-zero if the server doesn't identify itself. Wire it to whatever you run:
  - systemd: an `OnFailure=` unit, or a `.timer` that runs the check and alerts.
  - cron: `*/5 * * * * ENDPOINT=https://mcp.your-applications.com/your-trainer /opt/yourtrainer-mcp/deploy/healthcheck.sh || mail -s 'mcp down' you@…`
  - Uptime Kuma / Healthchecks.io: point an HTTP(S) monitor at the endpoint, or
    have the script ping a push URL on success.
- **Error rate / load shape:** the `get_health` MCP tool returns aggregate-only
  counters (requests/errors/by-tool/uptime) — scrape it or call it from a check.
  It holds no per-call or rider data (statelessness invariant).

## Public status page (TASK-0043)
- `deploy/status/canary.py` probes the endpoint and writes `status.json`; run it
  on a timer on the host:
  ```bash
  ENDPOINT=https://mcp.your-applications.com/your-trainer \
    python3 deploy/status/canary.py /var/www/status/status.json
  ```
- `deploy/status/index.html` is a static page that reads `status.json`. Serve
  the `deploy/status/` directory (e.g. at `status.your-applications.com`).

## Notes
- These monitoring/status artefacts are ready to wire; "done" for TASK-0011/0043
  requires the live host (an actual alert channel + a hosted status page).
- The `ReadWritePaths=` / capability-drop lines in the unit assume the process
  truly writes nothing. If you add file-based logging later, grant the path.
