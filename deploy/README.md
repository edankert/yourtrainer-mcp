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

## Notes
- Monitoring/alerting (TASK-0011) and the public status page (TASK-0043) are
  separate tasks; this artefact covers provisioning + service + proxy only.
- The `ReadWritePaths=` / capability-drop lines in the unit assume the process
  truly writes nothing. If you add file-based logging later, grant the path.
