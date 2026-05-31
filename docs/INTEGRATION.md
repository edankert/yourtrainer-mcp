# Integrating yourtrainer-mcp

How to connect an LLM client or application to the MCP server and use its tools,
with the two primary Your Trainer integration targets worked through:
**in-app AI assistants** and the **workout-creation process** (upstream FEAT-0086).

## Connecting

The server speaks MCP over two transports:

| Use | Transport | How |
|-----|-----------|-----|
| Hosted (production) | streamable HTTP | `https://mcp.your-applications.com/your-trainer` |
| Local dev | stdio | run `yourtrainer-mcp` (default) |
| Local HTTP | streamable HTTP | `YTMCP_TRANSPORT=http yourtrainer-mcp` → `http://127.0.0.1:8080/your-trainer` |

Example MCP client config (Claude Desktop / Cursor style), local stdio:

```json
{
  "mcpServers": {
    "yourtrainer": { "command": "yourtrainer-mcp" }
  }
}
```

For the hosted server, point your client's HTTP/streamable-HTTP transport at the
endpoint above. Every tool result includes an `_attribution` block; tools that
produce `.ytw` add a Your Trainer hint.

## Local install & self-hosting

The hosted endpoint needs no install. To run it **locally** (development, an
air-gapped/offline setup, or to self-host your own instance), install the
package and run the `yourtrainer-mcp` command.

### Install

```bash
# Recommended: isolated install of the CLI (no clone)
pipx install "git+https://github.com/edankert/yourtrainer-mcp"

# or into the current environment
pip install "git+https://github.com/edankert/yourtrainer-mcp"

# add the optional extra for richer real-world FIT reading (compressed/dev fields)
pip install "yourtrainer-mcp[fit] @ git+https://github.com/edankert/yourtrainer-mcp"
```

Requires Python ≥ 3.10. (Contributors: clone the repo and `pip install -e ".[dev]"`.)

### Run

```bash
yourtrainer-mcp                         # stdio transport (default) — for local MCP clients
YTMCP_TRANSPORT=http yourtrainer-mcp    # streamable HTTP on 127.0.0.1:8080/your-trainer
```

HTTP bind is configured by `YTMCP_HOST` / `YTMCP_PORT` / `YTMCP_PATH`
(defaults `127.0.0.1` / `8080` / `/your-trainer`). For a production self-host
(systemd + reverse proxy + TLS), see [`../deploy/README.md`](../deploy/README.md).

### Register the LOCAL server with your client

These mirror the hosted-endpoint instructions on the integrators page, but for a
local install. Use the **stdio** command for a desktop client on the same
machine, or point at your **self-hosted HTTP** URL.

- **Claude Desktop** — `claude_desktop_config.json`:
  ```json
  { "mcpServers": { "yourtrainer": { "command": "yourtrainer-mcp" } } }
  ```
- **Claude Code (CLI):**
  ```bash
  claude mcp add yourtrainer yourtrainer-mcp            # local stdio
  # or a self-hosted HTTP instance:
  claude mcp add yourtrainer http://127.0.0.1:8080/your-trainer --transport http
  ```
- **Cursor** — Settings → MCP Servers → Add. Command `yourtrainer-mcp` (stdio),
  or Transport HTTP with your self-hosted URL.
- **OpenAI Codex (CLI)** — `~/.codex/config.toml`:
  ```toml
  [mcp_servers.yourtrainer]
  command = "yourtrainer-mcp"          # local stdio
  # or, for a self-hosted HTTP instance:
  # url = "http://127.0.0.1:8080/your-trainer"
  # transport = "http"
  ```
- **Any MCP SDK** — Python (`mcp`/`fastmcp`) or TS (`@modelcontextprotocol/sdk`):
  spawn `yourtrainer-mcp` over stdio, or point an HTTP transport at your URL, then
  run `initialize → tools/list → tools/call`. See `examples/client_demo.py`.

## Contract (read once)

- **Stateless.** No accounts, no stored uploads, no telemetry. Each call is
  independent (see `CONTEXT.md`).
- **File transfer** (ADR-0005): text formats (ZWO/.ytw/GPX/TCX/ERG/MRC) pass as
  strings; **FIT** crosses as **base64**; local files / libraries are referenced
  by **filesystem path** (the host process reads them).
- **Power is an integer percentage of FTP** (`target_power_percent: 90` == 90% FTP)
  in the workout-intent and the canonical `.ytw`.
- **Errors** surface as MCP tool errors with a message (e.g. malformed workout).

## Tool catalogue by use-case

**Workout authoring** — `build_workout_from_intent`, `decompose_workout`,
`scale_workout`, `lint_workout`, `workout_difficulty`, `app_acceptance_check`,
`read_fit_workout`.

**Ride / training analysis** — `inspect_activity_file`, `analyze_ride`,
`training_load`, `recovery_time`, `batch_inspect`, `detect_file`.

**Knowledge registry** — `list_supported_formats`, `get_format_spec`,
`get_canonical_examples`, `get_format_constraints`, `get_conversion_notes`,
`get_format_glossary`, `get_format_version`, `validate`.

**Routes & workflows** — `analyze_route`, `anonymize_gpx`, `adherence_scorecard`,
`migration_inventory`, `roundtrip_workout`.

**Library** — `index_library`, `find_duplicate_workouts`, `library_statistics`,
`best_efforts_across_history`. **Ops** — `get_health`.

## Worked flow 1 — in-app AI assistant builds a workout

> Rider: "Give me a 1-hour sweet-spot session."

1. The assistant composes a structured intent (the Your Trainer
   `workout-intent` shape: `warmup`/`intervals`/`cooldown`, blocks + repeat
   groups, power as integer % FTP) and calls `build_workout_from_intent` with
   `output_format="ytw"`:
   ```json
   {"intent": {
       "name": "Sweet Spot 3x12", "description": "3x12 at 90% FTP",
       "workout_type": "POWER", "category": "sweet-spot",
       "warmup": {"duration_seconds": 600, "zone": "Z2", "label": "Warmup",
                  "target_power_percent": 45, "target_power_end_percent": 75},
       "intervals": [{"repeat": 3, "intervals": [
           {"duration_seconds": 720, "zone": "Z3", "label": "Sweet Spot",
            "id": "ss", "target_power_percent": 90},
           {"duration_seconds": 300, "zone": "Z1", "label": "Recovery",
            "target_power_percent": 55}]}],
       "cooldown": {"duration_seconds": 420, "zone": "Z1", "label": "Cooldown",
                    "target_power_percent": 60, "target_power_end_percent": 40}},
    "output_format": "ytw"}
   ```
   The output is a **canonical Your Trainer `.ytw`** (`programId`, `intervals`
   with `intervalType`/`targetPowerPercent`/repeat groups, `strings`) that
   imports directly into the app. Canonical schema:
   `your-applications.com/your-trainer/workout-schema.html`.
2. The response also carries a `difficulty` summary (IF/TSS, time-in-zone).
3. Optionally call `workout_difficulty` / `app_acceptance_check` first to show the
   rider the load and confirm it loads on their head unit.

## Worked flow 2 — workout-creation: bring a workout from another app

> Rider uploads a Zwift `.zwo` (or screenshot → text the assistant authored).

1. `decompose_workout(document, "zwo")` → a canonical Your Trainer `.ytw`
   (this *is* the ZWO→.ytw conversion).
2. (optional) `scale_workout(...)` for a shorter version, or `lint_workout` to
   flag issues.
3. `roundtrip_workout` can verify the conversion preserved the power profile.

## Worked flow 3 — "analyse my ride"

1. App hands the assistant a file path (or writes the upload to a temp path).
2. `inspect_activity_file(path, ftp_watts)` → NP/IF/TSS, peak-power, time-in-zone.
3. `analyze_ride(path, ftp_watts)` → decoupling, FTP estimate, intervals, etc.
4. `training_load([[date, tss], ...])` across history → CTL/ATL/TSB.

## Example client

`examples/client_demo.py` exercises flows 1–3 against an in-memory server
(no network) using the FastMCP client — a copy-paste starting point.

## See also

- `README.md` — overview & install. `deploy/README.md` — hosting.
- Knowledge corpus is also browsable as the static docs-site
  (`python scripts/build_docs.py`).
