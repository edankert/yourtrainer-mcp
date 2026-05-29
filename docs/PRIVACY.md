# Privacy & statelessness guarantee

yourtrainer-mcp is **stateless with respect to rider/user data**. It captures no
accounts, no profiles, no usage analytics, and **retains no user content**.

## What that means concretely
- **User input is processed in memory and discarded.** Activity files (FIT/TCX/
  GPX), uploaded workout documents (ZWO/.ytw, base64 FIT), routes, and library
  paths are read, used to compute a result, and dropped when the tool call
  returns. Nothing is written to disk.
- **No persistent caches of user content.** The server keeps exactly two pieces
  of cross-call state, neither of which is user data:
  1. **Aggregate health counters** (`health.py`): request/error totals and
     per-*tool-name* counts + uptime. No per-call records, no arguments, no
     payloads, no IP addresses. Surfaced via the `get_health` tool.
  2. **A public-content cache** (`content.py`): a short-TTL, size-bounded cache
     of *public Your Trainer website content* (the workout-library manifest,
     `.ytw` files, the manual, the AI-skill catalogue). This is published
     content, not rider data, and user input never reaches it.
- **No logging of user content, and no IP retention.** The library emits no log
  records of its own. The HTTP entrypoint **disables uvicorn's per-request access
  log** (which would otherwise record client IPs), and the reverse-proxy vhosts
  (`deploy/Caddyfile`, `deploy/nginx-mcp.conf`) log no request bodies and no
  per-request client IPs (`access_log off`). Operational visibility comes from
  the aggregate-only `get_health` tool.

## Why it's structural, not just policy
The server has no concept of "rider X": there are no accounts and no stored
state keyed to a user, so it *cannot* return one rider's data to another. This
is verifiable from the code.

## Verification
- Audit + enforcing tests: `tests/test_statelessness.py` (TST-0013) asserts that
  processing user content never enters the content cache, that no working files
  are written, that health metrics are aggregate-only, that repeated calls don't
  bleed, and that the package emits no log records.
- Hosting hardening (`deploy/`): the systemd unit runs with `PrivateTmp=true`,
  `ProtectSystem=strict`, and no writable paths; the Caddy log format records
  aggregate metadata only.

## Operator guidance
- Do **not** enable request-body logging at the proxy or app layer.
- Keep the process's working/temp dirs non-persistent (the provided unit does).

## Out of scope (by design)
No OAuth-mediated integrations (Strava/Garmin Connect/TrainingPeaks pull), which
would require holding tokens/state. Riders export files and pass them in instead.
See `CONTEXT.md` and the public privacy disclosure on the website.
