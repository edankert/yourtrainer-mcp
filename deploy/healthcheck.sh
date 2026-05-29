#!/usr/bin/env bash
# Liveness probe for yourtrainer-mcp (TASK-0011).
#
# Sends an MCP `initialize` and checks the server identifies itself. Exit 0 =
# healthy, non-zero = unhealthy. Suitable for systemd OnFailure=, a cron alert,
# Uptime Kuma "push/HTTP" monitors, or the canary in deploy/status/canary.py.
#
# Usage: ENDPOINT=https://mcp.your-applications.com/your-trainer ./healthcheck.sh
set -euo pipefail

ENDPOINT="${ENDPOINT:-http://127.0.0.1:8080/your-trainer}"
TIMEOUT="${TIMEOUT:-5}"

body='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"healthcheck","version":"0"}}}'

response="$(curl -fsS -m "$TIMEOUT" -X POST "$ENDPOINT" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d "$body" 2>/dev/null || true)"

if printf '%s' "$response" | grep -q '"name":"yourtrainer-mcp"'; then
  echo "OK: yourtrainer-mcp responding at $ENDPOINT"
  exit 0
fi

echo "FAIL: no valid initialize response from $ENDPOINT" >&2
exit 1
