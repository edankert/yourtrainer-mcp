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

## Contract (read once)

- **Stateless.** No accounts, no stored uploads, no telemetry. Each call is
  independent (see `CONTEXT.md`).
- **File transfer** (ADR-0005): text formats (ZWO/.ytw/GPX/TCX/ERG/MRC) pass as
  strings; **FIT** crosses as **base64**; local files / libraries are referenced
  by **filesystem path** (the host process reads them).
- **Power is a fraction of FTP** (1.0 == FTP) in the workout model, ZWO, and .ytw.
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

1. The assistant composes a structured intent and calls
   `build_workout_from_intent` with `output_format="ytw"`:
   ```json
   {"intent": {"name": "Sweet Spot 3x12", "steps": [
       {"kind": "warmup", "duration_s": 600, "power_low": 0.45, "power_high": 0.75},
       {"kind": "interval", "repeat": 3, "on_duration_s": 720, "off_duration_s": 300,
        "on_power": 0.9, "off_power": 0.55},
       {"kind": "cooldown", "duration_s": 420, "power_low": 0.6, "power_high": 0.4}]},
    "output_format": "ytw"}
   ```
2. The response carries the `.ytw` document + a `difficulty` summary (IF/TSS,
   time-in-zone). The app imports the `.ytw` directly.
3. Optionally call `workout_difficulty` / `app_acceptance_check` first to show the
   rider the load and confirm it loads on their head unit.

## Worked flow 2 — workout-creation: bring a workout from another app

> Rider uploads a Zwift `.zwo` (or screenshot → text the assistant authored).

1. `decompose_workout(document, "zwo")` → structured intent.
2. (optional) `scale_workout(...)` for a 30-min version, or `lint_workout` to
   flag issues.
3. `build_workout_from_intent(intent, "ytw")` → import-ready `.ytw`.
4. `roundtrip_workout` can verify the conversion preserved the power profile.

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
