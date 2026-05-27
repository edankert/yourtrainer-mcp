---
type: "[[risk]]"
id: RISK-0003
title: "Format-spec drift (ZWO, FIT, TCX, GPX, ERG/MRC)"
status: open
owner: edwin
created: 2026-05-27
updated: 2026-05-27
source: []
likelihood: medium
impact: low
mitigation:
  - "Canonical sample files per format checked into the test suite."
  - "CI step that re-validates against fresh samples on every release."
  - "Format-spec version tags in tool responses (\"output produced against ZWO spec v1.4.2\")."
  - "Periodic external review of format-spec changes by subscribing to the relevant standards / SDK changelogs."
related:
  - "[[FEAT-0001-Cycling-Format-Library]]"
  - "[[PHASE-001-Initial-Launch]]"
---

# Format-spec drift

## Description
The formats `yourtrainer-mcp` converts are third-party specs that evolve:

- **ZWO** — Zwift's workout format. Zwift periodically adds block types (e.g. SteadyStateWithLap, IntervalsP for power+cadence pairs).
- **FIT** — Garmin's universal format. Garmin's FIT SDK ships new message types per Wahoo / Garmin / Polar releases.
- **TCX** — Training Center XML. Effectively frozen but still has dialect variants (Garmin TCX vs. Strava-stripped TCX).
- **GPX** — universal, mostly stable; some apps add custom extensions in the `<extensions>` block.
- **ERG / MRC** — CompuTrainer legacy; semi-frozen but TrainerRoad and other consumers add subtle variations.

When a spec evolves and we don't update, two failure modes:
1. **Silent drop.** New block types parsed as unknown; data lost on conversion. User doesn't realise.
2. **Hard error.** New format version rejected entirely; tool returns parse error.

Mode 1 is the worse failure — silent data loss erodes trust without surfacing the cause.

## Mitigation
- **Canonical sample files per format** checked into the test suite. Re-validate on every release. New format-spec versions get new sample files.
- **CI validates against samples** on every PR. Format-spec regression caught before merge.
- **Subscribe to upstream changelogs.** Garmin FIT SDK changelog, Zwift dev forum (where they announce ZWO changes), Polar Pro Trainer FIT extensions. Edwin or a delegated maintainer monitors monthly.
- **Format-version tags in responses.** Each tool response includes `format_version_produced_against` so downstream clients (and the user) can flag potential incompatibility.
- **Roundtrip checks.** When possible, the test suite asserts `parse(emit(parse(file))) == parse(file)` to catch lossy round-trips before they ship.

## Notes
The likelihood is medium because indoor-cycling formats move slower than e.g. JS frameworks but still move. The impact is low for any single converter slip (riders can rerun) and rises if drift accumulates unchecked — which is why the CI step matters more than any individual fix.
