"""Structured-workout model + authoring tools (FEAT-0004).

Covers the workout-authoring cluster:
- build from structured intent (TASK-0023): intent dict -> Workout -> ZWO / .ytw
- decompose (TASK-0033): ZWO / .ytw text -> Workout (symmetric inverse)
- scale (TASK-0035): duration / FTP / intensity transforms
- structure linter (TASK-0025): domain-aware static analysis
- difficulty score (TASK-0050): IF/TSS + per-zone breakdown
- app-acceptance checker (TASK-0024): per-app constraints catalogue (v1 seed)

Power is modelled as a *fraction of FTP* throughout (ZWO's native convention),
so a workout is FTP-independent until rendered or scored.

FIT-workout output (the third target in TASK-0023) is handled in
``fit_workout.py`` and wired in a later wave; ZWO + .ytw are deterministic here.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from xml.dom import minidom

from . import power as power_math

YTW_VERSION = 1

# Step kinds. Intervals expand to repeated on/off blocks.
STEP_KINDS = frozenset({"warmup", "cooldown", "steady", "ramp", "interval", "freeride"})


@dataclass
class Step:
    """A single workout segment. Power values are fractions of FTP (1.0 == FTP)."""

    kind: str
    duration_s: int = 0  # single-block kinds (warmup/cooldown/steady/ramp/freeride)
    power: float | None = None  # steady target
    power_low: float | None = None  # ramp/warmup/cooldown start
    power_high: float | None = None  # ramp/warmup/cooldown end
    cadence: int | None = None
    # interval-only
    repeat: int | None = None
    on_duration_s: int | None = None
    off_duration_s: int | None = None
    on_power: float | None = None
    off_power: float | None = None

    def total_duration_s(self) -> int:
        if self.kind == "interval":
            r = self.repeat or 0
            return r * ((self.on_duration_s or 0) + (self.off_duration_s or 0))
        return self.duration_s


@dataclass
class Workout:
    name: str = "Untitled"
    description: str = ""
    author: str = ""
    steps: list[Step] = field(default_factory=list)

    def total_duration_s(self) -> int:
        return sum(s.total_duration_s() for s in self.steps)


class WorkoutError(ValueError):
    """Raised for malformed workout intent / files."""


# --------------------------------------------------------------------------- #
# Build from structured intent (TASK-0023)
# --------------------------------------------------------------------------- #

def _req(d: dict, key: str, ctx: str):
    if key not in d:
        raise WorkoutError(f"{ctx}: missing required field '{key}'")
    return d[key]


def build_workout(intent: dict) -> Workout:
    """Build a Workout from a structured-intent dict.

    Schema::

        {
          "name": "...", "description": "...", "author": "...",
          "steps": [
            {"kind": "warmup",   "duration_s": 600, "power_low": 0.4, "power_high": 0.6},
            {"kind": "steady",   "duration_s": 1200, "power": 0.85, "cadence": 90},
            {"kind": "ramp",     "duration_s": 300, "power_low": 0.6, "power_high": 1.0},
            {"kind": "interval", "repeat": 5, "on_duration_s": 60, "off_duration_s": 60,
             "on_power": 1.2, "off_power": 0.5},
            {"kind": "cooldown", "duration_s": 600, "power_low": 0.6, "power_high": 0.4},
            {"kind": "freeride", "duration_s": 300}
          ]
        }
    """
    steps_in = _req(intent, "steps", "workout")
    if not isinstance(steps_in, list) or not steps_in:
        raise WorkoutError("workout: 'steps' must be a non-empty list")

    steps: list[Step] = []
    for i, raw in enumerate(steps_in):
        ctx = f"step[{i}]"
        kind = _req(raw, "kind", ctx)
        if kind not in STEP_KINDS:
            raise WorkoutError(f"{ctx}: unknown kind '{kind}' (allowed: {sorted(STEP_KINDS)})")
        step = Step(kind=kind, cadence=raw.get("cadence"))
        if kind == "interval":
            step.repeat = int(_req(raw, "repeat", ctx))
            step.on_duration_s = int(_req(raw, "on_duration_s", ctx))
            step.off_duration_s = int(_req(raw, "off_duration_s", ctx))
            step.on_power = float(_req(raw, "on_power", ctx))
            step.off_power = float(_req(raw, "off_power", ctx))
            if step.repeat <= 0:
                raise WorkoutError(f"{ctx}: repeat must be > 0")
        elif kind in ("ramp", "warmup", "cooldown"):
            step.duration_s = int(_req(raw, "duration_s", ctx))
            step.power_low = float(_req(raw, "power_low", ctx))
            step.power_high = float(_req(raw, "power_high", ctx))
        elif kind == "steady":
            step.duration_s = int(_req(raw, "duration_s", ctx))
            step.power = float(_req(raw, "power", ctx))
        elif kind == "freeride":
            step.duration_s = int(_req(raw, "duration_s", ctx))
        steps.append(step)

    return Workout(
        name=intent.get("name", "Untitled"),
        description=intent.get("description", ""),
        author=intent.get("author", ""),
        steps=steps,
    )


# --------------------------------------------------------------------------- #
# Render: ZWO (TASK-0023)
# --------------------------------------------------------------------------- #

def _fmt(value: float) -> str:
    """Render a float without trailing noise (0.5 not 0.50000001)."""
    return f"{value:g}"


def to_zwo(workout: Workout) -> str:
    """Serialise to a Zwift .zwo XML document."""
    root = ET.Element("workout_file")
    ET.SubElement(root, "author").text = workout.author or "yourtrainer-mcp"
    ET.SubElement(root, "name").text = workout.name
    ET.SubElement(root, "description").text = workout.description
    ET.SubElement(root, "sportType").text = "bike"
    wk = ET.SubElement(root, "workout")

    for s in workout.steps:
        if s.kind == "warmup":
            el = ET.SubElement(wk, "Warmup")
            el.set("Duration", str(s.duration_s))
            el.set("PowerLow", _fmt(s.power_low or 0))
            el.set("PowerHigh", _fmt(s.power_high or 0))
        elif s.kind == "cooldown":
            el = ET.SubElement(wk, "Cooldown")
            el.set("Duration", str(s.duration_s))
            el.set("PowerLow", _fmt(s.power_low or 0))
            el.set("PowerHigh", _fmt(s.power_high or 0))
        elif s.kind == "ramp":
            el = ET.SubElement(wk, "Ramp")
            el.set("Duration", str(s.duration_s))
            el.set("PowerLow", _fmt(s.power_low or 0))
            el.set("PowerHigh", _fmt(s.power_high or 0))
        elif s.kind == "steady":
            el = ET.SubElement(wk, "SteadyState")
            el.set("Duration", str(s.duration_s))
            el.set("Power", _fmt(s.power or 0))
        elif s.kind == "interval":
            el = ET.SubElement(wk, "IntervalsT")
            el.set("Repeat", str(s.repeat or 0))
            el.set("OnDuration", str(s.on_duration_s or 0))
            el.set("OffDuration", str(s.off_duration_s or 0))
            el.set("OnPower", _fmt(s.on_power or 0))
            el.set("OffPower", _fmt(s.off_power or 0))
        elif s.kind == "freeride":
            el = ET.SubElement(wk, "FreeRide")
            el.set("Duration", str(s.duration_s))
        if s.cadence is not None:
            el.set("Cadence", str(s.cadence))

    raw = ET.tostring(root, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


# --------------------------------------------------------------------------- #
# Render: .ytw (JSON) (TASK-0023, TASK-0006 format)
# --------------------------------------------------------------------------- #

def to_ytw(workout: Workout) -> str:
    """Serialise to the Your Trainer Workout (.ytw) JSON format."""
    steps: list[dict] = []
    for s in workout.steps:
        d: dict = {"kind": s.kind}
        if s.kind == "interval":
            d.update(
                repeat=s.repeat,
                on_duration_s=s.on_duration_s,
                off_duration_s=s.off_duration_s,
                on_power=s.on_power,
                off_power=s.off_power,
            )
        elif s.kind in ("ramp", "warmup", "cooldown"):
            d.update(duration_s=s.duration_s, power_low=s.power_low, power_high=s.power_high)
        elif s.kind == "steady":
            d.update(duration_s=s.duration_s, power=s.power)
        elif s.kind == "freeride":
            d.update(duration_s=s.duration_s)
        if s.cadence is not None:
            d["cadence"] = s.cadence
        steps.append(d)
    doc = {
        "format": "ytw",
        "version": YTW_VERSION,
        "name": workout.name,
        "description": workout.description,
        "author": workout.author,
        "steps": steps,
    }
    return json.dumps(doc, indent=2)


# --------------------------------------------------------------------------- #
# Decompose: file -> Workout (TASK-0033)
# --------------------------------------------------------------------------- #

def from_ytw(text: str) -> Workout:
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as e:
        raise WorkoutError(f"invalid .ytw JSON: {e}") from e
    if doc.get("format") != "ytw":
        raise WorkoutError("not a .ytw document (missing format: ytw)")
    return build_workout(doc)


def _f(el: ET.Element, attr: str) -> float | None:
    v = el.get(attr)
    return float(v) if v is not None else None


def _i(el: ET.Element, attr: str) -> int:
    v = el.get(attr)
    return int(float(v)) if v is not None else 0


def from_zwo(text: str) -> Workout:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise WorkoutError(f"invalid ZWO XML: {e}") from e

    def _text(tag: str) -> str:
        node = root.find(tag)
        return node.text.strip() if node is not None and node.text else ""

    wk = root.find("workout")
    if wk is None:
        raise WorkoutError("ZWO missing <workout> element")

    steps: list[Step] = []
    for el in list(wk):
        tag = el.tag
        cad_raw = el.get("Cadence")
        cadence = int(cad_raw) if cad_raw else None
        if tag == "Warmup":
            steps.append(Step("warmup", _i(el, "Duration"), power_low=_f(el, "PowerLow"),
                              power_high=_f(el, "PowerHigh"), cadence=cadence))
        elif tag == "Cooldown":
            steps.append(Step("cooldown", _i(el, "Duration"), power_low=_f(el, "PowerLow"),
                              power_high=_f(el, "PowerHigh"), cadence=cadence))
        elif tag == "Ramp":
            steps.append(Step("ramp", _i(el, "Duration"), power_low=_f(el, "PowerLow"),
                              power_high=_f(el, "PowerHigh"), cadence=cadence))
        elif tag == "SteadyState":
            steps.append(Step("steady", _i(el, "Duration"), power=_f(el, "Power"), cadence=cadence))
        elif tag == "IntervalsT":
            steps.append(Step("interval", repeat=_i(el, "Repeat"),
                              on_duration_s=_i(el, "OnDuration"),
                              off_duration_s=_i(el, "OffDuration"),
                              on_power=_f(el, "OnPower"), off_power=_f(el, "OffPower"),
                              cadence=cadence))
        elif tag == "FreeRide":
            steps.append(Step("freeride", _i(el, "Duration"), cadence=cadence))
        # Unknown tags are skipped (forward-compat).
    if not steps:
        raise WorkoutError("ZWO <workout> contained no recognised steps")
    return Workout(name=_text("name"), description=_text("description"),
                   author=_text("author"), steps=steps)


# --------------------------------------------------------------------------- #
# Expand to a 1 Hz power series (shared by difficulty + scoring)
# --------------------------------------------------------------------------- #

def expand_to_power_series(workout: Workout, ftp: float) -> list[float]:
    """Render the prescription to a 1 Hz watts series (fraction*FTP)."""
    series: list[float] = []

    def ramp(dur: int, lo: float, hi: float):
        if dur <= 0:
            return
        for t in range(dur):
            frac = lo + (hi - lo) * (t / max(1, dur - 1)) if dur > 1 else lo
            series.append(frac * ftp)

    for s in workout.steps:
        if s.kind in ("warmup", "cooldown", "ramp"):
            ramp(s.duration_s, s.power_low or 0.0, s.power_high or 0.0)
        elif s.kind == "steady":
            series.extend([(s.power or 0.0) * ftp] * s.duration_s)
        elif s.kind == "freeride":
            # Unknown intensity; assume endurance ~0.6 FTP for scoring purposes.
            series.extend([0.6 * ftp] * s.duration_s)
        elif s.kind == "interval":
            for _ in range(s.repeat or 0):
                series.extend([(s.on_power or 0.0) * ftp] * (s.on_duration_s or 0))
                series.extend([(s.off_power or 0.0) * ftp] * (s.off_duration_s or 0))
    return series


# --------------------------------------------------------------------------- #
# Scale (TASK-0035)
# --------------------------------------------------------------------------- #

def scale_workout(
    workout: Workout,
    *,
    duration_factor: float | None = None,
    intensity_factor: float | None = None,
) -> Workout:
    """Return a scaled copy.

    duration_factor: multiply every duration (0.5 => half-length version).
    intensity_factor: multiply every power fraction (1.1 => 10% harder).
    FTP rescaling is intentionally a no-op here: power is stored as a fraction
    of FTP, so a new FTP changes only the rendered watts, not the prescription.
    """
    if duration_factor is not None and duration_factor <= 0:
        raise WorkoutError("duration_factor must be > 0")
    if intensity_factor is not None and intensity_factor <= 0:
        raise WorkoutError("intensity_factor must be > 0")

    df = duration_factor or 1.0
    inf = intensity_factor or 1.0

    def sd(x: int | None) -> int:
        return int(round((x or 0) * df))

    def sp(x: float | None) -> float | None:
        return None if x is None else round(x * inf, 4)

    new_steps: list[Step] = []
    for s in workout.steps:
        new_steps.append(
            Step(
                kind=s.kind,
                duration_s=sd(s.duration_s),
                power=sp(s.power),
                power_low=sp(s.power_low),
                power_high=sp(s.power_high),
                cadence=s.cadence,
                repeat=s.repeat,
                on_duration_s=sd(s.on_duration_s) if s.on_duration_s else s.on_duration_s,
                off_duration_s=sd(s.off_duration_s) if s.off_duration_s else s.off_duration_s,
                on_power=sp(s.on_power),
                off_power=sp(s.off_power),
            )
        )
    suffix = []
    if duration_factor and duration_factor != 1.0:
        suffix.append(f"{int(df * 100)}% duration")
    if intensity_factor and intensity_factor != 1.0:
        suffix.append(f"{int(inf * 100)}% intensity")
    name = workout.name + (f" ({', '.join(suffix)})" if suffix else "")
    return Workout(name=name, description=workout.description,
                   author=workout.author, steps=new_steps)


# --------------------------------------------------------------------------- #
# Difficulty score (TASK-0050)
# --------------------------------------------------------------------------- #

def difficulty_score(workout: Workout, ftp: float = 250.0) -> dict:
    """Compute IF, prescribed-TSS, and a per-zone time breakdown.

    The score is the prescribed Training Stress Score (FTP-independent because
    power is a fraction of FTP, so any positive FTP yields the same TSS).
    """
    series = expand_to_power_series(workout, ftp)
    duration_s = len(series)
    if duration_s == 0:
        return {"duration_s": 0, "intensity_factor": 0.0, "tss": 0.0, "time_in_zone_s": {}}
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
    """Domain-aware static analysis. Returns a list of findings.

    Each finding: {"severity": "error"|"warning"|"info", "code": str, "message": str}.
    """
    findings: list[dict] = []

    def add(sev: str, code: str, msg: str):
        findings.append({"severity": sev, "code": code, "message": msg})

    if not workout.steps:
        add("error", "empty", "Workout has no steps.")
        return findings

    if not workout.name.strip():
        add("warning", "no-name", "Workout has no name.")

    first, last = workout.steps[0], workout.steps[-1]
    if first.kind not in ("warmup", "ramp"):
        add("warning", "no-warmup", "Workout does not start with a warmup.")
    if last.kind not in ("cooldown",):
        add("info", "no-cooldown", "Workout does not end with a cooldown.")

    for i, s in enumerate(workout.steps):
        ctx = f"step[{i}] ({s.kind})"
        if s.total_duration_s() <= 0:
            add("error", "zero-duration", f"{ctx}: zero or negative duration.")
        for label, val in (
            ("power", s.power), ("power_low", s.power_low), ("power_high", s.power_high),
            ("on_power", s.on_power), ("off_power", s.off_power),
        ):
            if val is not None and not (0.0 <= val <= 2.5):
                add("warning", "power-range",
                    f"{ctx}: {label}={val:g} is outside the plausible 0–2.5×FTP range.")
        is_ramp = s.kind in ("ramp", "warmup", "cooldown")
        if is_ramp and s.power_low is not None and s.power_high is not None:
            if s.kind == "warmup" and s.power_low > s.power_high:
                add("info", "warmup-direction", f"{ctx}: warmup ramps down (low > high).")
            if s.kind == "cooldown" and s.power_low < s.power_high:
                add("info", "cooldown-direction", f"{ctx}: cooldown ramps up (low < high).")
        if s.kind == "interval" and (s.repeat or 0) > 60:
            add("warning", "many-reps", f"{ctx}: {s.repeat} repeats is unusually high.")
        if s.cadence is not None and not (30 <= s.cadence <= 150):
            add("warning", "cadence-range", f"{ctx}: cadence {s.cadence} rpm is implausible.")

    total = workout.total_duration_s()
    if total < 300:
        add("warning", "very-short", f"Total duration {total}s is very short (<5 min).")
    if total > 6 * 3600:
        add("warning", "very-long", f"Total duration {total}s is very long (>6 h).")

    return findings


# --------------------------------------------------------------------------- #
# App-acceptance checker (TASK-0024 / verified by TASK-0057)
# --------------------------------------------------------------------------- #

# Per-app workout constraints. Every entry below is sourced; capabilities we
# could NOT verify against vendor/reference documentation are deliberately
# omitted rather than guessed (a missing key means "unknown", not "false").
# Descriptive only — never comparative (POSITIONING Principle 1).
#
# Sources:
# - Garmin 50-step limit: real upload error "Workout exceeds ... maximum
#   expected number of 50 steps" (forums.trainerday.com/t/.../6202;
#   forums.garmin.com Connect-web threads). Garmin has no native ramp step, so
#   ramps must be expanded into discrete steps (TrainerDay converter notes).
#   Garmin Connect's web builder caps lower (20 steps); 50 is the synced/FIT cap.
# - Garmin 99-repeat cap: Garmin Connect / forums.
# - Zwift native Ramp + FreeRide elements, and no documented step/size cap:
#   github.com/h4l/zwift-workout-file-reference (canonical ZWO tag reference).
APP_CONSTRAINTS: dict[str, dict] = {
    "garmin": {
        "display": "Garmin (Edge / Connect-synced)",
        "max_steps": 50,
        "max_repeats": 99,
        "native_ramp": False,  # ramps expand into multiple discrete steps
        "source": "Garmin 50-step upload error (trainerday/garmin forums); no native ramp.",
    },
    "zwift": {
        "display": "Zwift",
        "max_steps": None,  # no documented hard limit
        "native_ramp": True,
        "native_freeride": True,
        "source": "h4l/zwift-workout-file-reference (Ramp + FreeRide are native ZWO elements).",
    },
}


def app_acceptance(workout: Workout, apps: list[str] | None = None) -> dict:
    """Report, per app, whether a workout will load cleanly.

    Returns ``{app: {"accepted": bool|None, "issues": [...], "warnings": [...],
    "source": str}}``. ``accepted`` is ``None`` when no verified constraints are
    on record for the app. Only documented, sourced limits are enforced;
    ``issues`` are hard blockers, ``warnings`` are caveats (e.g. ramp expansion).
    """
    targets = apps or list(APP_CONSTRAINTS)
    n_steps = len(workout.steps)
    has_freeride = any(s.kind == "freeride" for s in workout.steps)
    has_ramp = any(s.kind in ("warmup", "cooldown", "ramp") for s in workout.steps)
    max_repeat = max((s.repeat or 0 for s in workout.steps if s.kind == "interval"), default=0)

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
        max_steps = c.get("max_steps")
        if max_steps is not None and n_steps > max_steps:
            issues.append(f"{n_steps} steps exceeds the documented {max_steps}-step limit.")
        max_repeats = c.get("max_repeats")
        if max_repeats is not None and max_repeat > max_repeats:
            issues.append(f"interval repeat {max_repeat} exceeds the {max_repeats}-repeat limit.")
        if c.get("native_ramp") is False and has_ramp:
            warnings.append(
                "No native ramp support: ramps/warmup/cooldown expand into multiple "
                "discrete steps, which may push the workout over the step limit."
            )
        if c.get("native_freeride") is False and has_freeride:
            issues.append("Contains a FreeRide block, which this app does not support.")
        result[app] = {"accepted": not issues, "issues": issues,
                       "warnings": warnings, "source": c["source"]}
    return result
