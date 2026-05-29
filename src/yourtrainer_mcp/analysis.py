"""Single-ride analytics (FEAT-0004).

- HR–power decoupling (TASK-0028)
- FTP estimate from a ride (TASK-0046)
- Power-duration model + modelled FTP / mFTP (TASK-0047)
- Peak-power curve as a standalone calculator (TASK-0022)
- Peak / best efforts with timing (TASK-0054)
- Cadence analysis (TASK-0052)
- HR drift (TASK-0053)
- Lap / interval auto-detection (TASK-0036)

All pure Python; operates on per-sample lists (gaps zero-filled for power).
"""

from __future__ import annotations

from collections.abc import Sequence

from . import power as power_math

STANDARD_DURATIONS_S = (1, 5, 30, 60, 300, 1200, 3600)


# --------------------------------------------------------------------------- #
# Peak power (TASK-0022) + best efforts with timing (TASK-0054)
# --------------------------------------------------------------------------- #

def peak_power_curve(
    power: Sequence[float],
    durations_s: Sequence[int] = STANDARD_DURATIONS_S,
    sample_rate_hz: float = 1.0,
) -> dict[int, float]:
    """Mean-max power for each duration (thin wrapper over the engine)."""
    return power_math.peak_power_curve(power, durations_s, sample_rate_hz)


def best_efforts(
    power: Sequence[float],
    durations_s: Sequence[int] = STANDARD_DURATIONS_S,
    sample_rate_hz: float = 1.0,
) -> dict[int, dict]:
    """Best effort per duration, with the watts and the start offset (seconds)."""
    result: dict[int, dict] = {}
    n = len(power)
    for d in durations_s:
        window = max(1, round(d * sample_rate_hz))
        if window > n:
            continue
        rolling = power_math.rolling_average(power, window)
        best_idx = max(range(len(rolling)), key=lambda i: rolling[i])
        result[d] = {
            "watts": round(rolling[best_idx], 1),
            "start_s": round(best_idx / sample_rate_hz, 1),
        }
    return result


# --------------------------------------------------------------------------- #
# FTP estimate (TASK-0046)
# --------------------------------------------------------------------------- #

def estimate_ftp(power: Sequence[float], sample_rate_hz: float = 1.0) -> dict:
    """Estimate FTP from a ride.

    Prefers best 60-min power when available; otherwise 95% of best 20-min
    power (the common field-test convention). Returns the estimate, the method,
    and the underlying peak values.
    """
    ppc = power_math.peak_power_curve(power, (1200, 3600), sample_rate_hz)
    if 3600 in ppc:
        return {"ftp_w": round(ppc[3600], 1), "method": "best_60min",
                "peak_60min_w": round(ppc[3600], 1)}
    if 1200 in ppc:
        return {"ftp_w": round(ppc[1200] * 0.95, 1), "method": "best_20min_x0.95",
                "peak_20min_w": round(ppc[1200], 1)}
    return {"ftp_w": None, "method": "insufficient_data",
            "reason": "ride shorter than 20 minutes"}


# --------------------------------------------------------------------------- #
# Power-duration model + mFTP (TASK-0047)
# --------------------------------------------------------------------------- #

def power_duration_model(
    power: Sequence[float],
    durations_s: Sequence[int] = (180, 300, 600, 720, 1200),
    sample_rate_hz: float = 1.0,
) -> dict:
    """Fit the 2-parameter critical-power model P(t) = W'/t + CP.

    Linear regression of mean-max power against 1/t. CP (intercept) is the
    modelled sustainable power; mFTP is reported as CP. Needs ≥2 usable points.
    """
    ppc = power_math.peak_power_curve(power, durations_s, sample_rate_hz)
    pts = [(1.0 / t, p) for t, p in ppc.items()]
    if len(pts) < 2:
        return {"cp_w": None, "w_prime_j": None, "mftp_w": None,
                "method": "insufficient_data", "points_used": len(pts)}

    n = len(pts)
    sx = sum(x for x, _ in pts)
    sy = sum(y for _, y in pts)
    sxx = sum(x * x for x, _ in pts)
    sxy = sum(x * y for x, y in pts)
    denom = n * sxx - sx * sx
    if denom == 0:
        return {"cp_w": None, "w_prime_j": None, "mftp_w": None,
                "method": "degenerate", "points_used": n}
    slope = (n * sxy - sx * sy) / denom  # W' (joules)
    intercept = (sy - slope * sx) / n  # CP (watts)
    return {
        "cp_w": round(intercept, 1),
        "w_prime_j": round(slope, 0),
        "mftp_w": round(intercept, 1),
        "method": "2-param-cp",
        "points_used": n,
    }


# --------------------------------------------------------------------------- #
# HR–power decoupling (TASK-0028) and HR drift (TASK-0053)
# --------------------------------------------------------------------------- #

def hr_power_decoupling(
    power: Sequence[float], heart_rate: Sequence[float]
) -> dict:
    """Aerobic decoupling (Pw:Hr): efficiency-factor drift across ride halves.

    Splits the ride in half; computes EF = avg_power / avg_HR for each half;
    decoupling% = (EF_first − EF_second) / EF_first × 100. Positive means the
    second half cost more heartbeats per watt (cardiac drift). <5% is the
    common "well-paced aerobic ride" rule of thumb.
    """
    n = min(len(power), len(heart_rate))
    if n < 2:
        return {"decoupling_pct": None, "reason": "insufficient_data"}
    mid = n // 2
    p1, p2 = power[:mid], power[mid:n]
    h1, h2 = heart_rate[:mid], heart_rate[mid:n]
    ef1 = _safe_ratio(power_math.average(p1), power_math.average(h1))
    ef2 = _safe_ratio(power_math.average(p2), power_math.average(h2))
    if ef1 is None or ef2 is None or ef1 == 0:
        return {"decoupling_pct": None, "reason": "zero_hr_or_power"}
    decoupling = (ef1 - ef2) / ef1 * 100
    return {
        "decoupling_pct": round(decoupling, 2),
        "ef_first_half": round(ef1, 4),
        "ef_second_half": round(ef2, 4),
        "well_paced": abs(decoupling) < 5.0,
    }


def hr_drift(heart_rate: Sequence[float]) -> dict:
    """HR drift across ride halves and a rough aerobic-HR estimate.

    Aerobic HR is approximated as the median HR (a coarse central tendency for
    sustained riding); treat as indicative, not a lab aerobic threshold.
    """
    hr = [h for h in heart_rate if h and h > 0]
    if len(hr) < 2:
        return {"hr_drift_pct": None, "reason": "insufficient_data"}
    mid = len(hr) // 2
    avg1 = power_math.average(hr[:mid])
    avg2 = power_math.average(hr[mid:])
    drift = (avg2 - avg1) / avg1 * 100 if avg1 else None
    median = sorted(hr)[len(hr) // 2]
    return {
        "hr_drift_pct": round(drift, 2) if drift is not None else None,
        "avg_hr_first_half": round(avg1, 1),
        "avg_hr_second_half": round(avg2, 1),
        "approx_aerobic_hr": round(median, 1),
    }


def _safe_ratio(num: float, den: float) -> float | None:
    return num / den if den else None


# --------------------------------------------------------------------------- #
# Cadence analysis (TASK-0052)
# --------------------------------------------------------------------------- #

def cadence_analysis(cadence: Sequence[float], sample_rate_hz: float = 1.0) -> dict:
    """Cadence stats: averages, coasting fraction, time in cadence bands."""
    if not cadence:
        return {"reason": "no_cadence_data"}
    spp = 1.0 / sample_rate_hz
    moving = [c for c in cadence if c > 0]
    bands = {"coasting(0)": 0.0, "<70": 0.0, "70-89": 0.0, "90-99": 0.0, "100+": 0.0}
    for c in cadence:
        if c <= 0:
            bands["coasting(0)"] += spp
        elif c < 70:
            bands["<70"] += spp
        elif c < 90:
            bands["70-89"] += spp
        elif c < 100:
            bands["90-99"] += spp
        else:
            bands["100+"] += spp
    return {
        "avg_rpm_moving": round(power_math.average(moving), 1) if moving else 0.0,
        "peak_rpm": max(cadence),
        "coasting_pct": round(100 * (len(cadence) - len(moving)) / len(cadence), 1),
        "time_in_band_s": {k: round(v, 1) for k, v in bands.items()},
    }


# --------------------------------------------------------------------------- #
# Lap / interval auto-detection (TASK-0036)
# --------------------------------------------------------------------------- #

def detect_intervals(
    power: Sequence[float],
    ftp: float,
    threshold_frac: float = 0.88,
    min_duration_s: int = 30,
    sample_rate_hz: float = 1.0,
) -> list[dict]:
    """Find work efforts in an unstructured ride.

    Smooths power over 10 s, then returns contiguous runs above
    ``threshold_frac × FTP`` lasting at least ``min_duration_s``.
    """
    if ftp <= 0:
        raise ValueError("ftp must be positive")
    if not power:
        return []
    smooth_w = max(1, round(10 * sample_rate_hz))
    smoothed = power_math.rolling_average(power, smooth_w)
    threshold = threshold_frac * ftp
    min_samples = max(1, round(min_duration_s * sample_rate_hz))

    efforts: list[dict] = []
    run_start: int | None = None
    for i, p in enumerate(smoothed):
        if p >= threshold and run_start is None:
            run_start = i
        elif p < threshold and run_start is not None:
            _emit(efforts, power, run_start, i, min_samples, sample_rate_hz)
            run_start = None
    if run_start is not None:
        _emit(efforts, power, run_start, len(smoothed), min_samples, sample_rate_hz)
    return efforts


def _emit(efforts, power, start, end, min_samples, sample_rate_hz):
    if end - start < min_samples:
        return
    segment = power[start:end]
    efforts.append({
        "start_s": round(start / sample_rate_hz, 1),
        "end_s": round(end / sample_rate_hz, 1),
        "duration_s": round((end - start) / sample_rate_hz, 1),
        "avg_w": round(power_math.average(segment), 1),
        "normalized_power_w": round(power_math.normalized_power(segment, sample_rate_hz), 1),
    })
