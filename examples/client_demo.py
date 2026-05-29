#!/usr/bin/env python3
"""Example MCP client for yourtrainer-mcp (TASK-0056).

Exercises the two Your Trainer integration flows — an AI assistant building a
workout, and the workout-creation import/convert path — plus a ride analysis,
against an in-memory server (no network). Run: ``python examples/client_demo.py``.

Requires the package installed (``pip install -e ".[dev]"``). For a real server,
swap ``Client(server.mcp)`` for ``Client("https://mcp.your-applications.com/your-trainer")``.
"""

from __future__ import annotations

import asyncio
import json

from fastmcp import Client

from yourtrainer_mcp import server


async def main() -> None:
    async with Client(server.mcp) as c:
        print("# Flow 1 — AI assistant builds a sweet-spot workout (.ytw)")
        built = (await c.call_tool("build_workout_from_intent", {
            "intent": {"name": "Sweet Spot 3x12", "steps": [
                {"kind": "warmup", "duration_s": 600, "power_low": 0.45, "power_high": 0.75},
                {"kind": "interval", "repeat": 3, "on_duration_s": 720, "off_duration_s": 300,
                 "on_power": 0.9, "off_power": 0.55},
                {"kind": "cooldown", "duration_s": 420, "power_low": 0.6, "power_high": 0.4}]},
            "output_format": "ytw",
        })).data
        diff = built["summary"]["difficulty"]
        print(f"  duration={built['summary']['total_duration_s']}s "
              f"IF={diff['intensity_factor']} TSS={diff['tss']}")
        attr = built["_attribution"]
        print(f"  attribution: {attr.get('note', attr['source'])}")

        print("\n# Flow 2 — workout creation: convert a ZWO, scale to 30 min")
        zwo = (await c.call_tool("build_workout_from_intent", {
            "intent": {"name": "Threshold 2x20", "steps": [
                {"kind": "steady", "duration_s": 2400, "power": 1.0}]},
            "output_format": "zwo"})).data["document"]
        intent = (await c.call_tool("decompose_workout",
                                    {"document": zwo, "source_format": "zwo"})).data["intent"]
        scaled = (await c.call_tool("scale_workout", {
            "document": zwo, "source_format": "zwo",
            "duration_factor": 0.5, "output_format": "ytw"})).data
        print(f"  decomposed {len(intent['steps'])} step(s); "
              f"scaled to {scaled['summary']['total_duration_s']}s")

        print("\n# Flow 3 — analyse a recorded ride (real Edge 810 + Vector)")
        ride = "tests/fixtures/external/Edge810-Vector-2013-08-16-15-35-10.fit"
        summary = (await c.call_tool("inspect_activity_file",
                                     {"path": ride, "ftp_watts": 275})).data
        p = summary["power"]
        print(f"  NP={p['normalized_power_w']}W IF={p['intensity_factor']} "
              f"TSS={p['training_stress_score']}")

        print("\n# Knowledge registry — cite the ZWO spec")
        spec = (await c.call_tool("get_format_spec", {"format_key": "zwo"})).data
        print(f"  {spec['name']} v: {spec['version']}")
        print("\nFull build payload (truncated):")
        print(json.dumps({k: v for k, v in built.items() if k != "document"}, indent=2)[:300])


if __name__ == "__main__":
    asyncio.run(main())
