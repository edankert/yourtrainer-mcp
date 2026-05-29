"""Plan-vs-actual adherence scorecard (TASK-0034).

Compares a planned workout against a recorded activity's power stream and
scores how closely the rider followed each step. Closes the planning→execution
loop. Pairs with the AI-coach workflow upstream (FEAT-0084).
"""

from __future__ import annotations

from collections.abc import Sequence

from . import power as power_math
from .workout import Workout, expand_to_power_series


def adherence_scorecard(
    workout: Workout,
    actual_power: Sequence[float],
    ftp: float,
    sample_rate_hz: float = 1.0,
    tolerance_pct: float = 10.0,
) -> dict:
    """Score how closely ``actual_power`` followed ``workout``.

    Aligns the actual stream to the planned per-second target series and reports
    per-step average target vs actual, deviation %, and an in-tolerance flag,
    plus an overall compliance score (% of time within ``tolerance_pct``).

    Power steps only; FreeRide steps are reported as ``untargeted``.
    """
    if ftp <= 0:
        raise ValueError("ftp must be positive")
    target = expand_to_power_series(workout, ftp)  # 1 Hz watts
    # Resample actual to 1 Hz indices by scaling its sample rate.
    actual = list(actual_power)
    n = min(len(target), int(len(actual) / sample_rate_hz) if sample_rate_hz else len(actual))

    def actual_at(sec: int) -> float | None:
        idx = int(sec * sample_rate_hz)
        return actual[idx] if 0 <= idx < len(actual) else None

    steps_out: list[dict] = []
    in_tol_seconds = 0
    counted = 0
    cursor = 0
    for i, step in enumerate(workout.steps):
        dur = step.total_duration_s()
        seg_target = target[cursor:cursor + dur]
        seg_actual = [a for s in range(cursor, cursor + dur) if (a := actual_at(s)) is not None]
        cursor += dur
        if not seg_target or not seg_actual:
            steps_out.append({"step": i, "kind": step.kind, "status": "no_data"})
            continue
        if step.kind == "freeride":
            steps_out.append({"step": i, "kind": step.kind, "status": "untargeted",
                              "avg_actual_w": round(power_math.average(seg_actual), 1)})
            continue
        avg_t = power_math.average(seg_target)
        avg_a = power_math.average(seg_actual)
        dev = (avg_a - avg_t) / avg_t * 100 if avg_t else 0.0
        for s in range(cursor - dur, min(cursor, cursor - dur + len(seg_actual))):
            a = actual_at(s)
            t = target[s] if s < len(target) else None
            if a is not None and t:
                counted += 1
                if abs((a - t) / t * 100) <= tolerance_pct:
                    in_tol_seconds += 1
        steps_out.append({
            "step": i, "kind": step.kind,
            "avg_target_w": round(avg_t, 1),
            "avg_actual_w": round(avg_a, 1),
            "deviation_pct": round(dev, 1),
            "in_tolerance": abs(dev) <= tolerance_pct,
        })

    compliance = round(100 * in_tol_seconds / counted, 1) if counted else 0.0
    return {
        "planned_duration_s": len(target),
        "compared_seconds": n,
        "compliance_pct": compliance,
        "tolerance_pct": tolerance_pct,
        "steps": steps_out,
    }
