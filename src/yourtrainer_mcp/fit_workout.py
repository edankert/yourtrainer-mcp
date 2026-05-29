"""FIT-workout read/write (TASK-0020) + the third TASK-0023 render target.

Encodes a :class:`~yourtrainer_mcp.workout.Workout` to a valid FIT-workout
binary and decodes one back. Power targets use FIT's "% FTP" convention
(stored as ``1000 + percent``). Because the workout model stores power as an
integer percentage of FTP, repeat groups and ramps round-trip exactly (no
quantisation loss) under the per-second-power check.
"""

from __future__ import annotations

from . import fit
from .workout import Block, Repeat, Workout, zone_for_percent

# workout_step enums.
_DUR_TIME = 0
_TGT_POWER = 4
_INT_ACTIVE, _INT_REST, _INT_WARMUP, _INT_COOLDOWN = 0, 1, 2, 3

_INTENSITY_FROM_TYPE = {"WARMUP": _INT_WARMUP, "COOLDOWN": _INT_COOLDOWN, "INTERVAL": _INT_ACTIVE}
_TYPE_FROM_INTENSITY = {_INT_WARMUP: "WARMUP", _INT_COOLDOWN: "COOLDOWN",
                        _INT_ACTIVE: "INTERVAL", _INT_REST: "INTERVAL"}


def _pct(percent: int) -> int:
    """Encode an integer % of FTP as FIT % FTP (1000 + percent)."""
    return 1000 + int(percent)


def _unpct(value: int) -> int:
    return int(value) - 1000


def _flatten(workout: Workout) -> list[Block]:
    """Flatten the workout (expanding nested repeat groups) into a list of blocks."""
    out: list[Block] = []

    def walk(items):
        for it in items:
            if isinstance(it, Repeat):
                for _ in range(it.repeat):
                    walk(it.intervals)
            else:
                out.append(it)

    walk(workout.intervals)
    return out


def encode_workout_fit(workout: Workout) -> bytes:
    """Serialise a Workout to FIT-workout bytes."""
    blocks = _flatten(workout)
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
        fit.Field(6, fit.UINT16, len(blocks)),                # num_valid_steps
    ])

    for idx, b in enumerate(blocks):
        lo = b.target_power_percent or 0
        hi = b.target_power_end_percent if b.target_power_end_percent is not None else lo
        w.add_message(fit.MSG_WORKOUT_STEP, [
            fit.Field(254, fit.UINT16, idx),                       # message_index
            fit.Field(1, fit.ENUM, _DUR_TIME),                     # duration_type
            fit.Field(2, fit.UINT32, max(0, b.duration_seconds) * 1000),  # duration_value (ms)
            fit.Field(3, fit.ENUM, _TGT_POWER),                    # target_type = power
            fit.Field(4, fit.UINT32, 0),                           # target_value
            fit.Field(5, fit.UINT32, _pct(lo)),                    # custom_target_power_low
            fit.Field(6, fit.UINT32, _pct(hi)),                    # custom_target_power_high
            fit.Field(7, fit.ENUM, _INTENSITY_FROM_TYPE.get(b.interval_type, _INT_ACTIVE)),
        ])

    return w.to_bytes()


def decode_workout_fit(data: bytes) -> Workout:
    """Decode FIT-workout bytes back into a Workout (flat blocks)."""
    messages = fit.decode(data)
    name = "Workout"
    raw_steps: list[tuple[int, dict]] = []
    for global_num, vals in messages:
        if global_num == fit.MSG_WORKOUT and vals.get(8) is not None:
            name = str(vals[8])
        elif global_num == fit.MSG_WORKOUT_STEP:
            idx = vals.get(254)
            raw_steps.append((int(idx) if idx is not None else len(raw_steps), vals))

    def _get(vals: dict, key: int, default: int) -> int:
        v = vals.get(key)
        return default if v is None else int(v)

    raw_steps.sort(key=lambda t: t[0])
    blocks: list[Block | Repeat] = []
    for _idx, vals in raw_steps:
        dur = _get(vals, 2, 0) // 1000
        intensity = _get(vals, 7, _INT_ACTIVE)
        lo = _unpct(_get(vals, 5, 1000))
        hi = _unpct(_get(vals, 6, 1000))
        itype = _TYPE_FROM_INTENSITY.get(intensity, "INTERVAL")
        label = {"WARMUP": "Warm Up", "COOLDOWN": "Cool Down"}.get(itype, "Work")
        blocks.append(Block(
            duration_seconds=dur, zone=zone_for_percent(lo), label=label,
            interval_type=itype, target_power_percent=lo,
            target_power_end_percent=hi if hi != lo else None,
        ))
    return Workout(name=name, workout_type="POWER", intervals=blocks)
