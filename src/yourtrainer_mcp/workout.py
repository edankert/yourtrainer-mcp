"""Structured-workout model + authoring tools (FEAT-0004).

Aligned to the canonical Your Trainer schema (TASK-0063 / ISS-0001):
- **Build input** mirrors ``workout-intent.json`` (snake_case; ``warmup`` /
  ``intervals`` / ``cooldown``; blocks + repeat groups; power as integer % FTP).
- **.ytw output** matches ``your-trainer/docs/ytw-schema.json`` and the
  ``generate_workout_library.py`` translator (camelCase ``programId`` /
  ``intervals`` with ``intervalType`` / ``targetPowerPercent`` / repeat groups /
  per-locale ``strings``).

Power is an **integer percentage of FTP** throughout (1.0×FTP == 100), matching
both schemas, so a workout is FTP-independent until rendered/scored. Translation
of labels/cues into non-primary locales is the website generator's job; this
module emits the primary-locale ``strings`` block (plus any supplied
``name_i18n`` / ``description_i18n``).
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from xml.dom import minidom

from . import power as power_math

INTERVAL_TYPES = frozenset({"WARMUP", "COOLDOWN", "INTERVAL"})
WORKOUT_TYPES = frozenset({"POWER", "HR_ZONE", "ROUTE"})

# Coggan zone upper bounds (fraction of FTP) for deriving an intensityZone token.
_ZONE_BOUNDS = (("Z1", 0.55), ("Z2", 0.75), ("Z3", 0.90), ("Z4", 1.05),
                ("Z5", 1.20), ("Z6", 1.50), ("Z7", float("inf")))


class WorkoutError(ValueError):
    """Raised for malformed workout intent / files."""


@dataclass
class Cue:
    offset_seconds: int
    text: str
    duration_seconds: int | None = None


@dataclass
class Block:
    """A single workout interval. ``target_power_percent`` is an integer % of FTP."""

    duration_seconds: int
    zone: str
    label: str
    interval_type: str = "INTERVAL"
    id: str | None = None
    target_power_percent: int | None = None
    target_power_end_percent: int | None = None  # ramp end
    target_hr_zone: int | None = None
    cadence_target: int | None = None
    cues: list[Cue] = field(default_factory=list)

    def total_duration_s(self) -> int:
        return self.duration_seconds


@dataclass
class Repeat:
    repeat: int
    intervals: list[Block | Repeat]  # nested repeat groups are allowed (workout-schema)

    def total_duration_s(self) -> int:
        return self.repeat * sum(i.total_duration_s() for i in self.intervals)


@dataclass
class Workout:
    name: str = "Untitled"
    description: str = ""
    workout_type: str = "POWER"
    intervals: list[Block | Repeat] = field(default_factory=list)
    variant: str | None = None
    difficulty: int | None = None
    category: str | None = None
    primary_locale: str = "en"
    slug: str | None = None
    name_i18n: dict[str, str] | None = None
    description_i18n: dict[str, str] | None = None

    def total_duration_s(self) -> int:
        return sum(i.total_duration_s() for i in self.intervals)


def slugify(text: str) -> str:
    return "-".join("".join(c if c.isalnum() else " " for c in text.lower()).split())


def zone_for_percent(percent: float) -> str:
    frac = percent / 100.0
    for name, upper in _ZONE_BOUNDS:
        if frac <= upper:
            return name
    return "Z7"  # pragma: no cover


# --------------------------------------------------------------------------- #
# Build from structured intent (workout-intent.json shape)
# --------------------------------------------------------------------------- #

def _req(d: dict, key: str, ctx: str):
    if key not in d:
        raise WorkoutError(f"{ctx}: missing required field '{key}'")
    return d[key]


def _cue_from_intent(raw: dict, ctx: str) -> Cue:
    return Cue(
        offset_seconds=int(_req(raw, "offset_seconds", ctx)),
        text=str(_req(raw, "text", ctx)),
        duration_seconds=int(raw["duration_seconds"]) if "duration_seconds" in raw else None,
    )


def _block_from_intent(raw: dict, ctx: str, workout_type: str,
                       default_interval_type: str = "INTERVAL") -> Block:
    block = Block(
        duration_seconds=int(_req(raw, "duration_seconds", ctx)),
        zone=str(_req(raw, "zone", ctx)),
        label=str(_req(raw, "label", ctx)),
        interval_type=raw.get("interval_type", default_interval_type),
        id=raw.get("id"),
        cadence_target=int(raw["cadence_target"]) if "cadence_target" in raw else None,
        cues=[_cue_from_intent(c, f"{ctx}.cue[{i}]") for i, c in enumerate(raw.get("cues", []))],
    )
    if block.interval_type not in INTERVAL_TYPES:
        raise WorkoutError(f"{ctx}: invalid interval_type {block.interval_type!r}")
    if workout_type == "POWER":
        block.target_power_percent = int(_req(raw, "target_power_percent", ctx))
        if "target_power_end_percent" in raw:
            block.target_power_end_percent = int(raw["target_power_end_percent"])
    elif workout_type == "HR_ZONE":
        block.target_hr_zone = int(_req(raw, "target_hr_zone", ctx))
    return block


def _items_from_intent(items: list, workout_type: str) -> list[Block | Repeat]:
    out: list[Block | Repeat] = []
    for i, raw in enumerate(items):
        ctx = f"intervals[{i}]"
        if "repeat" in raw:
            reps = int(raw["repeat"])
            if reps <= 0:
                raise WorkoutError(f"{ctx}: repeat must be > 0")
            out.append(Repeat(repeat=reps,
                              intervals=_items_from_intent(_req(raw, "intervals", ctx),
                                                           workout_type)))
        else:
            out.append(_block_from_intent(raw, ctx, workout_type))
    return out


def build_workout(intent: dict) -> Workout:
    """Build a Workout from a ``workout-intent.json``-shaped dict.

    Required: ``name``, ``description``, ``warmup`` (block), ``intervals`` (list
    of blocks/repeat groups), ``cooldown`` (block). ``workout_type`` defaults to
    ``POWER``. See the canonical schema at
    ``your-applications.com/public/schemas/workout-intent.json``.
    """
    workout_type = intent.get("workout_type", "POWER")
    if workout_type not in WORKOUT_TYPES:
        raise WorkoutError(f"invalid workout_type {workout_type!r}")

    intervals: list[Block | Repeat] = []
    intervals.append(_block_from_intent(_req(intent, "warmup", "workout"), "warmup",
                                        workout_type, default_interval_type="WARMUP"))
    intervals.extend(_items_from_intent(_req(intent, "intervals", "workout"), workout_type))
    intervals.append(_block_from_intent(_req(intent, "cooldown", "workout"), "cooldown",
                                        workout_type, default_interval_type="COOLDOWN"))

    return Workout(
        name=intent.get("name", "Untitled"),
        description=intent.get("description", ""),
        workout_type=workout_type,
        intervals=intervals,
        variant=intent.get("variant"),
        difficulty=intent.get("difficulty"),
        category=intent.get("category"),
        primary_locale=intent.get("primary_locale", "en"),
        slug=intent.get("slug"),
        name_i18n=intent.get("name_i18n"),
        description_i18n=intent.get("description_i18n"),
    )


# --------------------------------------------------------------------------- #
# Render: .ytw (canonical schema)
# --------------------------------------------------------------------------- #

def _block_to_ytw(b: Block) -> dict:
    iv: dict = {"duration": b.duration_seconds, "intensityZone": b.zone,
                "label": b.label, "intervalType": b.interval_type}
    if b.id:
        iv["id"] = b.id
    if b.target_power_percent is not None:
        iv["targetPowerPercent"] = int(b.target_power_percent)
        if b.target_power_end_percent is not None:
            iv["targetPowerEndPercent"] = int(b.target_power_end_percent)
    if b.target_hr_zone is not None:
        iv["targetHrZone"] = int(b.target_hr_zone)
    if b.cadence_target is not None:
        iv["cadenceTarget"] = int(b.cadence_target)
    if b.cues:
        iv["cues"] = [
            {"offsetSec": c.offset_seconds, "text": c.text,
             **({"durationSec": c.duration_seconds} if c.duration_seconds is not None else {})}
            for c in b.cues
        ]
    return iv


def _intervals_to_ytw(items: list[Block | Repeat]) -> list[dict]:
    out: list[dict] = []
    for it in items:
        if isinstance(it, Repeat):
            out.append({"repeat": it.repeat, "intervals": _intervals_to_ytw(it.intervals)})
        else:
            out.append(_block_to_ytw(it))
    return out


def _walk_blocks(items: list[Block | Repeat]):
    for it in items:
        if isinstance(it, Repeat):
            yield from _walk_blocks(it.intervals)
        else:
            yield it


def _strings_block(workout: Workout) -> dict:
    """Assemble the per-locale ``strings`` block (primary locale + supplied i18n)."""
    labels: dict[str, str] = {}
    cues: dict[str, str] = {}
    for b in _walk_blocks(workout.intervals):
        if b.id:
            labels.setdefault(b.id, b.label)
            for idx, c in enumerate(b.cues):
                cues.setdefault(f"{b.id}:{idx}", c.text)

    primary = workout.primary_locale
    strings: dict[str, dict] = {
        primary: {"name": workout.name, "description": workout.description,
                  "labels": dict(labels), "cues": dict(cues)}
    }
    for loc in sorted(set(workout.name_i18n or {}) | set(workout.description_i18n or {})):
        if loc == primary:
            continue
        strings[loc] = {
            "name": (workout.name_i18n or {}).get(loc, workout.name),
            "description": (workout.description_i18n or {}).get(loc, workout.description),
            "labels": dict(labels),  # english fallback; full translation is the website's job
            "cues": dict(cues),
        }
    return strings


def to_ytw(workout: Workout) -> str:
    """Serialise to a canonical Your Trainer ``.ytw`` JSON document."""
    doc: dict = {
        "programId": workout.slug or slugify(workout.name),
        "programName": workout.name,
        "description": workout.description,
        "totalDuration": workout.total_duration_s(),
        "workoutType": workout.workout_type,
        "primaryLocale": workout.primary_locale,
        "intervals": _intervals_to_ytw(workout.intervals),
    }
    if workout.variant is not None:
        doc["variant"] = workout.variant
    if workout.difficulty is not None:
        doc["difficulty"] = workout.difficulty
    if workout.category is not None:
        doc["category"] = workout.category
    doc["strings"] = _strings_block(workout)
    return json.dumps(doc, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Parse: .ytw -> Workout (TASK-0033 decompose)
# --------------------------------------------------------------------------- #

def _cue_from_ytw(raw: dict) -> Cue:
    return Cue(offset_seconds=int(raw.get("offsetSec", 0)), text=str(raw.get("text", "")),
              duration_seconds=int(raw["durationSec"]) if "durationSec" in raw else None)


def _block_from_ytw(raw: dict) -> Block:
    return Block(
        duration_seconds=int(raw["duration"]),
        zone=str(raw.get("intensityZone", "Z1")),
        label=str(raw.get("label", "")),
        interval_type=raw.get("intervalType", "INTERVAL"),
        id=raw.get("id"),
        target_power_percent=(int(raw["targetPowerPercent"])
                              if "targetPowerPercent" in raw else None),
        target_power_end_percent=(int(raw["targetPowerEndPercent"])
                                  if "targetPowerEndPercent" in raw else None),
        target_hr_zone=int(raw["targetHrZone"]) if "targetHrZone" in raw else None,
        cadence_target=int(raw["cadenceTarget"]) if "cadenceTarget" in raw else None,
        cues=[_cue_from_ytw(c) for c in raw.get("cues", [])],
    )


def from_ytw(text: str) -> Workout:
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as e:
        raise WorkoutError(f"invalid .ytw JSON: {e}") from e
    if "programId" not in doc or "intervals" not in doc:
        raise WorkoutError("not a .ytw document (missing programId/intervals)")

    def _items(raw_items: list) -> list[Block | Repeat]:
        out: list[Block | Repeat] = []
        for raw in raw_items:
            if "repeat" in raw:
                out.append(Repeat(repeat=int(raw["repeat"]), intervals=_items(raw["intervals"])))
            else:
                out.append(_block_from_ytw(raw))
        return out

    items = _items(doc["intervals"])
    return Workout(
        name=doc.get("programName", "Untitled"),
        description=doc.get("description", ""),
        workout_type=doc.get("workoutType", "POWER"),
        intervals=items,
        variant=doc.get("variant"),
        difficulty=doc.get("difficulty"),
        category=doc.get("category"),
        primary_locale=doc.get("primaryLocale", "en"),
        slug=doc.get("programId"),
    )


# --------------------------------------------------------------------------- #
# Render / parse: ZWO  (power fraction = percent / 100)
# --------------------------------------------------------------------------- #

def _fmt(value: float) -> str:
    return f"{value:g}"


def _frac(percent: int | None) -> float:
    return (percent or 0) / 100.0


def to_zwo(workout: Workout) -> str:
    root = ET.Element("workout_file")
    ET.SubElement(root, "author").text = "yourtrainer-mcp"
    ET.SubElement(root, "name").text = workout.name
    ET.SubElement(root, "description").text = workout.description
    ET.SubElement(root, "sportType").text = "bike"
    wk = ET.SubElement(root, "workout")

    def emit_block(parent, b: Block):
        if b.interval_type == "WARMUP":
            el = ET.SubElement(parent, "Warmup")
            el.set("Duration", str(b.duration_seconds))
            el.set("PowerLow", _fmt(_frac(b.target_power_percent)))
            el.set("PowerHigh", _fmt(_frac(b.target_power_end_percent or b.target_power_percent)))
        elif b.interval_type == "COOLDOWN":
            el = ET.SubElement(parent, "Cooldown")
            el.set("Duration", str(b.duration_seconds))
            el.set("PowerLow", _fmt(_frac(b.target_power_percent)))
            el.set("PowerHigh", _fmt(_frac(b.target_power_end_percent or b.target_power_percent)))
        elif b.target_power_end_percent is not None and \
                b.target_power_end_percent != b.target_power_percent:
            el = ET.SubElement(parent, "Ramp")
            el.set("Duration", str(b.duration_seconds))
            el.set("PowerLow", _fmt(_frac(b.target_power_percent)))
            el.set("PowerHigh", _fmt(_frac(b.target_power_end_percent)))
        else:
            el = ET.SubElement(parent, "SteadyState")
            el.set("Duration", str(b.duration_seconds))
            el.set("Power", _fmt(_frac(b.target_power_percent)))
        if b.cadence_target is not None:
            el.set("Cadence", str(b.cadence_target))

    def _is_constant(b) -> bool:
        return (isinstance(b, Block) and b.interval_type == "INTERVAL" and
                (b.target_power_end_percent is None or
                 b.target_power_end_percent == b.target_power_percent))

    def emit_items(items: list[Block | Repeat]):
        for it in items:
            if isinstance(it, Repeat) and len(it.intervals) == 2 and \
                    all(_is_constant(b) for b in it.intervals):
                on, off = it.intervals
                assert isinstance(on, Block) and isinstance(off, Block)  # _is_constant guard
                el = ET.SubElement(wk, "IntervalsT")
                el.set("Repeat", str(it.repeat))
                el.set("OnDuration", str(on.duration_seconds))
                el.set("OffDuration", str(off.duration_seconds))
                el.set("OnPower", _fmt(_frac(on.target_power_percent)))
                el.set("OffPower", _fmt(_frac(off.target_power_percent)))
            elif isinstance(it, Repeat):
                # Ramps / nested groups can't ride in IntervalsT — expand them.
                for _ in range(it.repeat):
                    emit_items(it.intervals)
            else:
                emit_block(wk, it)

    emit_items(workout.intervals)

    raw = ET.tostring(root, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def _zwo_block(interval_type: str, dur: int, lo: float, hi: float | None,
               cadence: int | None, label: str) -> Block:
    lo_pct = round(lo * 100)
    hi_pct = round(hi * 100) if hi is not None else None
    return Block(
        duration_seconds=dur, zone=zone_for_percent(lo_pct), label=label,
        interval_type=interval_type, target_power_percent=lo_pct,
        target_power_end_percent=hi_pct if hi_pct is not None and hi_pct != lo_pct else None,
        cadence_target=cadence,
    )


def from_zwo(text: str) -> Workout:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise WorkoutError(f"invalid ZWO XML: {e}") from e
    wk = root.find("workout")
    if wk is None:
        raise WorkoutError("ZWO missing <workout> element")

    def _f(el, attr):
        v = el.get(attr)
        return float(v) if v is not None else None

    def _i(el, attr):
        v = el.get(attr)
        return int(float(v)) if v is not None else 0

    items: list[Block | Repeat] = []
    for el in list(wk):
        tag = el.tag
        cad_raw = el.get("Cadence")
        cad = int(cad_raw) if cad_raw else None
        if tag == "Warmup":
            items.append(_zwo_block("WARMUP", _i(el, "Duration"), _f(el, "PowerLow") or 0,
                                    _f(el, "PowerHigh"), cad, "Warm Up"))
        elif tag == "Cooldown":
            items.append(_zwo_block("COOLDOWN", _i(el, "Duration"), _f(el, "PowerLow") or 0,
                                    _f(el, "PowerHigh"), cad, "Cool Down"))
        elif tag == "Ramp":
            items.append(_zwo_block("INTERVAL", _i(el, "Duration"), _f(el, "PowerLow") or 0,
                                    _f(el, "PowerHigh"), cad, "Ramp"))
        elif tag == "SteadyState":
            p = _f(el, "Power") or 0
            items.append(_zwo_block("INTERVAL", _i(el, "Duration"), p, None, cad, "Work"))
        elif tag == "IntervalsT":
            on = _zwo_block("INTERVAL", _i(el, "OnDuration"), _f(el, "OnPower") or 0, None,
                            cad, "Work")
            off = _zwo_block("INTERVAL", _i(el, "OffDuration"), _f(el, "OffPower") or 0, None,
                             None, "Recovery")
            items.append(Repeat(repeat=_i(el, "Repeat"), intervals=[on, off]))
        elif tag == "FreeRide":
            # .ytw has no free-ride concept; map to a 0% coast block (lossy).
            items.append(_zwo_block("INTERVAL", _i(el, "Duration"), 0.0, None, cad, "Free Ride"))
    if not items:
        raise WorkoutError("ZWO <workout> contained no recognised steps")

    def _text(tag: str) -> str:
        node = root.find(tag)
        return node.text.strip() if node is not None and node.text else ""

    return Workout(name=_text("name") or "Untitled", description=_text("description"),
                   workout_type="POWER", intervals=items)


# --------------------------------------------------------------------------- #
# Expand to a 1 Hz power series (shared by difficulty + adherence)
# --------------------------------------------------------------------------- #

def expand_to_power_series(workout: Workout, ftp: float) -> list[float]:
    """Render a POWER workout's prescription to a 1 Hz watts series."""
    series: list[float] = []
    if workout.workout_type != "POWER":
        return series

    def emit(b: Block):
        dur = b.duration_seconds
        if dur <= 0:
            return
        lo = _frac(b.target_power_percent) * ftp
        hi = _frac(b.target_power_end_percent if b.target_power_end_percent is not None
                   else b.target_power_percent) * ftp
        if lo == hi:
            series.extend([lo] * dur)
        else:
            for t in range(dur):
                series.append(lo + (hi - lo) * (t / max(1, dur - 1)))

    def walk(items: list[Block | Repeat]):
        for it in items:
            if isinstance(it, Repeat):
                for _ in range(it.repeat):
                    walk(it.intervals)
            else:
                emit(it)

    walk(workout.intervals)
    return series


# --------------------------------------------------------------------------- #
# Scale (TASK-0035)
# --------------------------------------------------------------------------- #

def _scale_block(b: Block, df: float, inf: float) -> Block:
    def sp(x: int | None) -> int | None:
        return None if x is None else int(round(x * inf))
    return Block(
        duration_seconds=int(round(b.duration_seconds * df)),
        zone=b.zone, label=b.label, interval_type=b.interval_type, id=b.id,
        target_power_percent=sp(b.target_power_percent),
        target_power_end_percent=sp(b.target_power_end_percent),
        target_hr_zone=b.target_hr_zone, cadence_target=b.cadence_target,
        cues=[Cue(int(round(c.offset_seconds * df)), c.text, c.duration_seconds) for c in b.cues],
    )


def scale_workout(workout: Workout, *, duration_factor: float | None = None,
                  intensity_factor: float | None = None) -> Workout:
    """Scale durations and/or power. Power is % FTP, so FTP rescaling is a no-op."""
    if duration_factor is not None and duration_factor <= 0:
        raise WorkoutError("duration_factor must be > 0")
    if intensity_factor is not None and intensity_factor <= 0:
        raise WorkoutError("intensity_factor must be > 0")
    df = duration_factor or 1.0
    inf = intensity_factor or 1.0

    def _scale_items(items: list[Block | Repeat]) -> list[Block | Repeat]:
        out: list[Block | Repeat] = []
        for it in items:
            if isinstance(it, Repeat):
                out.append(Repeat(it.repeat, _scale_items(it.intervals)))
            else:
                out.append(_scale_block(it, df, inf))
        return out

    new_items = _scale_items(workout.intervals)

    suffix = []
    if duration_factor and duration_factor != 1.0:
        suffix.append(f"{int(df * 100)}% duration")
    if intensity_factor and intensity_factor != 1.0:
        suffix.append(f"{int(inf * 100)}% intensity")
    name = workout.name + (f" ({', '.join(suffix)})" if suffix else "")
    return Workout(name=name, description=workout.description, workout_type=workout.workout_type,
                   intervals=new_items, variant=workout.variant, difficulty=workout.difficulty,
                   category=workout.category, primary_locale=workout.primary_locale)


# --------------------------------------------------------------------------- #
# Difficulty score (TASK-0050)
# --------------------------------------------------------------------------- #

def difficulty_score(workout: Workout, ftp: float = 250.0) -> dict:
    """IF, prescribed-TSS, and per-zone time for a POWER workout (FTP-independent)."""
    series = expand_to_power_series(workout, ftp)
    duration_s = len(series)
    if duration_s == 0:
        return {"duration_s": workout.total_duration_s(), "intensity_factor": 0.0,
                "tss": 0.0, "time_in_zone_s": {}}
    np_value = power_math.normalized_power(series)
    if_value = power_math.intensity_factor(np_value, ftp)
    tss = power_math.training_stress_score(duration_s, np_value, ftp)
    tiz = power_math.time_in_zone(series, ftp)
    return {
        "duration_s": duration_s,
        "normalized_power_frac": round(np_value / ftp, 3),
        "intensity_factor": round(if_value, 3),
        "tss": round(tss, 1),
        "time_in_zone_s": {k: round(v, 1) for k, v in tiz.items()},
    }


# --------------------------------------------------------------------------- #
# Structure linter (TASK-0025)
# --------------------------------------------------------------------------- #

def lint_workout(workout: Workout) -> list[dict]:
    """Domain-aware static analysis. Returns findings (severity/code/message)."""
    findings: list[dict] = []

    def add(sev: str, code: str, msg: str):
        findings.append({"severity": sev, "code": code, "message": msg})

    if not workout.intervals:
        add("error", "empty", "Workout has no intervals.")
        return findings
    if not workout.name.strip():
        add("warning", "no-name", "Workout has no name.")

    blocks = list(_walk_blocks(workout.intervals))
    if blocks and blocks[0].interval_type != "WARMUP":
        add("warning", "no-warmup", "Workout does not start with a warmup.")
    if blocks and blocks[-1].interval_type != "COOLDOWN":
        add("info", "no-cooldown", "Workout does not end with a cooldown.")

    for i, b in enumerate(blocks):
        ctx = f"block[{i}] ({b.label})"
        if b.duration_seconds <= 0:
            add("error", "zero-duration", f"{ctx}: zero or negative duration.")
        for lbl, val in (("target_power_percent", b.target_power_percent),
                         ("target_power_end_percent", b.target_power_end_percent)):
            if val is not None and not (0 <= val <= 250):
                add("warning", "power-range", f"{ctx}: {lbl}={val} outside 0-250% FTP.")
        if b.cadence_target is not None and not (30 <= b.cadence_target <= 150):
            add("warning", "cadence-range", f"{ctx}: cadence {b.cadence_target} rpm implausible.")

    for it in workout.intervals:
        if isinstance(it, Repeat) and it.repeat > 50:
            add("warning", "many-reps", f"repeat {it.repeat} exceeds the .ytw maximum of 50.")

    total = workout.total_duration_s()
    if total < 300:
        add("warning", "very-short", f"Total duration {total}s is very short (<5 min).")
    if total > 6 * 3600:
        add("warning", "very-long", f"Total duration {total}s is very long (>6 h).")
    return findings


# --------------------------------------------------------------------------- #
# App-acceptance checker (TASK-0024 / verified TASK-0057)
# --------------------------------------------------------------------------- #

APP_CONSTRAINTS: dict[str, dict] = {
    "garmin": {
        "display": "Garmin (Edge / Connect-synced)",
        "max_steps": 50,
        "max_repeats": 99,
        "native_ramp": False,
        "source": "Garmin 50-step upload error (trainerday/garmin forums); no native ramp.",
    },
    "zwift": {
        "display": "Zwift",
        "max_steps": None,
        "native_ramp": True,
        "source": "h4l/zwift-workout-file-reference (Ramp is a native ZWO element).",
    },
}


def app_acceptance(workout: Workout, apps: list[str] | None = None) -> dict:
    """Report, per app, whether a workout will load cleanly (sourced limits only)."""
    targets = apps or list(APP_CONSTRAINTS)
    blocks = list(_walk_blocks(workout.intervals))
    n_steps = len(workout.intervals)
    has_ramp = any(b.target_power_end_percent is not None and
                   b.target_power_end_percent != b.target_power_percent for b in blocks) or \
        any(b.interval_type in ("WARMUP", "COOLDOWN") for b in blocks)

    def _max_repeat(items: list[Block | Repeat]) -> int:
        best = 0
        for it in items:
            if isinstance(it, Repeat):
                best = max(best, it.repeat, _max_repeat(it.intervals))
        return best

    max_repeat = _max_repeat(workout.intervals)

    result: dict[str, dict] = {}
    for app in targets:
        c = APP_CONSTRAINTS.get(app)
        if c is None:
            result[app] = {"accepted": None,
                           "issues": [f"No verified constraints on record for '{app}'."],
                           "warnings": []}
            continue
        issues: list[str] = []
        warnings: list[str] = []
        if c.get("max_steps") is not None and n_steps > c["max_steps"]:
            issues.append(f"{n_steps} steps exceeds the documented {c['max_steps']}-step limit.")
        if c.get("max_repeats") is not None and max_repeat > c["max_repeats"]:
            issues.append(
                f"interval repeat {max_repeat} exceeds the {c['max_repeats']}-repeat limit.")
        if c.get("native_ramp") is False and has_ramp:
            warnings.append("No native ramp support: ramps/warmup/cooldown expand into multiple "
                            "discrete steps, which may push the workout over the step limit.")
        result[app] = {"accepted": not issues, "issues": issues,
                       "warnings": warnings, "source": c["source"]}
    return result
