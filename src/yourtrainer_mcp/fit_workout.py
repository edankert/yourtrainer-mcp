"""FIT-workout read/write (TASK-0020) + the third TASK-0023 render target.

Encodes a :class:`~yourtrainer_mcp.workout.Workout` to a valid FIT-workout
binary and decodes one back. Power targets use FIT's "% FTP" convention
(stored as ``1000 + percent``). Intervals and ramps are expanded to discrete
time steps on write — semantically faithful and lossless under the
per-second-power round-trip check.
"""

from __future__ import annotations

from . import fit
from .workout import Step, Workout

# workout_step enums.
_DUR_TIME = 0
_TGT_POWER = 4
_TGT_OPEN = 2
_INT_ACTIVE, _INT_REST, _INT_WARMUP, _INT_COOLDOWN = 0, 1, 2, 3


def _pct(frac: float) -> int:
    """Encode a fraction-of-FTP as FIT % FTP (1000 + percent)."""
    return 1000 + int(round(frac * 100))


def _unpct(value: int) -> float:
    return (value - 1000) / 100.0


def _flatten(workout: Workout) -> list[tuple[str, int, float, float]]:
    """Flatten to ``[(intensity_kind, duration_s, power_low, power_high)]``.

    intervals -> on/off steps; ramps/warmup/cooldown keep their low/high.
    freeride -> kind 'freeride' with low/high == -1 sentinel.
    """
    out: list[tuple[str, int, float, float]] = []
    for s in workout.steps:
        if s.kind == "interval":
            for _ in range(s.repeat or 0):
                out.append(("on", s.on_duration_s or 0, s.on_power or 0, s.on_power or 0))
                out.append(("off", s.off_duration_s or 0, s.off_power or 0, s.off_power or 0))
        elif s.kind == "steady":
            out.append(("steady", s.duration_s, s.power or 0, s.power or 0))
        elif s.kind in ("warmup", "cooldown", "ramp"):
            out.append((s.kind, s.duration_s, s.power_low or 0, s.power_high or 0))
        elif s.kind == "freeride":
            out.append(("freeride", s.duration_s, -1.0, -1.0))
    return out


def encode_workout_fit(workout: Workout) -> bytes:
    """Serialise a Workout to FIT-workout bytes."""
    steps = _flatten(workout)
    w = fit.FitWriter()

    w.add_message(fit.MSG_FILE_ID, [
        fit.Field(0, fit.ENUM, 5),        # type = workout
        fit.Field(1, fit.UINT16, 255),    # manufacturer = development
        fit.Field(2, fit.UINT16, 0),      # product
        fit.Field(4, fit.UINT32, 0),      # time_created (FIT epoch)
    ])

    w.add_message(fit.MSG_WORKOUT, [
        fit.Field(8, fit.STRING, workout.name or "Workout"),  # wkt_name
        fit.Field(4, fit.ENUM, 2),                            # sport = cycling
        fit.Field(6, fit.UINT16, len(steps)),                 # num_valid_steps
    ])

    intensity_map = {
        "warmup": _INT_WARMUP, "cooldown": _INT_COOLDOWN,
        "off": _INT_REST, "on": _INT_ACTIVE, "steady": _INT_ACTIVE,
        "ramp": _INT_ACTIVE, "freeride": _INT_ACTIVE,
    }
    for idx, (kind, dur, lo, hi) in enumerate(steps):
        is_open = kind == "freeride"
        fields = [
            fit.Field(254, fit.UINT16, idx),                  # message_index
            fit.Field(1, fit.ENUM, _DUR_TIME),                # duration_type
            fit.Field(2, fit.UINT32, max(0, dur) * 1000),     # duration_value (ms)
            fit.Field(3, fit.ENUM, _TGT_OPEN if is_open else _TGT_POWER),
            fit.Field(4, fit.UINT32, 0),                      # target_value
            fit.Field(5, fit.UINT32, 0 if is_open else _pct(lo)),   # custom low
            fit.Field(6, fit.UINT32, 0 if is_open else _pct(hi)),   # custom high
            fit.Field(7, fit.ENUM, intensity_map[kind]),      # intensity
        ]
        w.add_message(fit.MSG_WORKOUT_STEP, fields)

    return w.to_bytes()


def decode_workout_fit(data: bytes) -> Workout:
    """Decode FIT-workout bytes back into a Workout (flattened steps)."""
    messages = fit.decode(data)
    name = "Workout"
    raw_steps: list[tuple[int, dict]] = []
    for global_num, vals in messages:
        if global_num == fit.MSG_WORKOUT and 8 in vals:
            name = str(vals[8])
        elif global_num == fit.MSG_WORKOUT_STEP:
            raw_steps.append((int(vals.get(254, len(raw_steps))), vals))

    raw_steps.sort(key=lambda t: t[0])
    steps: list[Step] = []
    for _idx, vals in raw_steps:
        dur = int(vals.get(2, 0)) // 1000
        target_type = int(vals.get(3, _TGT_POWER))
        intensity = int(vals.get(7, _INT_ACTIVE))
        if target_type == _TGT_OPEN:
            steps.append(Step("freeride", dur))
            continue
        lo = _unpct(int(vals.get(5, 1000)))
        hi = _unpct(int(vals.get(6, 1000)))
        if intensity == _INT_WARMUP:
            steps.append(Step("warmup", dur, power_low=lo, power_high=hi))
        elif intensity == _INT_COOLDOWN:
            steps.append(Step("cooldown", dur, power_low=lo, power_high=hi))
        elif lo == hi:
            steps.append(Step("steady", dur, power=lo))
        else:
            steps.append(Step("ramp", dur, power_low=lo, power_high=hi))
    return Workout(name=name, steps=steps)
