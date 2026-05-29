#!/usr/bin/env python3
"""Public canary for the status page (TASK-0043).

Probes the MCP endpoint with an `initialize` call, measures latency, and writes
a small ``status.json`` next to ``index.html``. Run on a schedule (cron /
systemd timer) on the host. Stateless: it keeps only the latest status, no
historical request data.

Usage:
    ENDPOINT=https://mcp.your-applications.com/your-trainer \\
        python canary.py /var/www/status/status.json
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

ENDPOINT = os.environ.get("ENDPOINT", "http://127.0.0.1:8080/your-trainer")
TIMEOUT = float(os.environ.get("TIMEOUT", "5"))

_BODY = json.dumps({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
               "clientInfo": {"name": "canary", "version": "0"}},
}).encode()


def probe() -> dict:
    req = urllib.request.Request(
        ENDPOINT, data=_BODY, method="POST",
        headers={"Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"},
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            text = resp.read().decode("utf-8", "replace")
        latency_ms = round((time.perf_counter() - start) * 1000, 1)
        up = '"name":"yourtrainer-mcp"' in text.replace(" ", "")
        return {"up": up, "latency_ms": latency_ms,
                "detail": "ok" if up else "unexpected response"}
    except Exception as exc:  # noqa: BLE001
        return {"up": False, "latency_ms": None, "detail": str(exc)}


def main() -> int:
    out_path = sys.argv[1] if len(sys.argv) > 1 else "status.json"
    result = probe()
    result["endpoint"] = ENDPOINT
    result["checked_at"] = datetime.now(timezone.utc).isoformat()
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print(json.dumps(result))
    return 0 if result["up"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
