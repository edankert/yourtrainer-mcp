"""Cycling power / training-load math — pure Python, no third-party deps.

Implements the canonical Coggan metrics so they can be validated against
reference values (TrainingPeaks / Intervals.icu) and unit-tested hermetically.

Definitions
-----------
NP (Normalised Power)
    1. 30-second rolling average of power.
    2. Raise each rolling value to the 4th power.
    3. Take the mean.
    4. Take the 4th root.
IF (Intensity Factor)
    NP / FTP.
TSS (Training Stress Score)
    (duration_s * NP * IF) / (FTP * 3600) * 100
    == (duration_s / 3600) * IF^2 * 100
"""

from __future__ import annotations

from collections.abc import Sequence

# Coggan 7-zone model, upper bound of each zone as a fraction of FTP.
# Z7 ("Neuromuscular") is open-ended (math.inf).
COGGAN_ZONE_UPPER_BOUNDS: tuple[tuple[str, float], ...] = (
    ("Z1 Active Recovery", 0.55),
    ("Z2 Endurance", 0.75),
    ("Z3 Tempo", 0.90),
    ("Z4 Threshold", 1.05),
    ("Z5 VO2max", 1.20),
    ("Z6 Anaerobic", 1.50),
    ("Z7 Neuromuscular", float("inf")),
)


def average(values: Sequence[float]) -> float:
    """Arithmetic mean; 0.0 for an empty sequence."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def rolling_average(values: Sequence[float], window: int) -> list[float]:
    """Trailing simple moving average over ``window`` samples.

    The output has one value per input sample once the window is full
    (i.e. ``len(values) - window + 1`` values). For inputs shorter than the
    window, returns a single value: the mean of all samples.
    """
    if window <= 1:
        return list(values)
    if len(values) < window:
        return [average(values)] if values else []

    out: list[float] = []
    window_sum = sum(values[:window])
    out.append(window_sum / window)
    for i in range(window, len(values)):
        window_sum += values[i] - values[i - window]
        out.append(window_sum / window)
    return out


def normalized_power(power: Sequence[float], sample_rate_hz: float = 1.0) -> float:
    """Coggan Normalised Power for a power stream sampled at ``sample_rate_hz``.

    Gaps should already be zero-filled (a stopped rider records 0 W).
    """
    if not power:
        return 0.0
    window = max(1, round(30 * sample_rate_hz))
    rolling = rolling_average(power, window)
    if not rolling:
        return 0.0
    fourth = [r**4 for r in rolling]
    return average(fourth) ** 0.25


def intensity_factor(np_value: float, ftp: float) -> float:
    """IF = NP / FTP."""
    if ftp <= 0:
        raise ValueError("ftp must be positive")
    return np_value / ftp


def training_stress_score(
    duration_s: float, np_value: float, ftp: float
) -> float:
    """TSS = (duration_s * NP * IF) / (FTP * 3600) * 100."""
    if ftp <= 0:
        raise ValueError("ftp must be positive")
    if duration_s < 0:
        raise ValueError("duration_s must be non-negative")
    if_value = intensity_factor(np_value, ftp)
    return (duration_s * np_value * if_value) / (ftp * 3600) * 100


def peak_power_curve(
    power: Sequence[float],
    durations_s: Sequence[int] = (1, 5, 30, 60, 300, 1200, 3600),
    sample_rate_hz: float = 1.0,
) -> dict[int, float]:
    """Mean-max power for each requested duration (seconds).

    For each duration, the best (highest) rolling average of that length.
    Durations longer than the recording are omitted from the result.
    """
    result: dict[int, float] = {}
    n = len(power)
    for d in durations_s:
        window = max(1, round(d * sample_rate_hz))
        if window > n:
            continue
        result[d] = max(rolling_average(power, window))
    return result


def time_in_zone(
    power: Sequence[float],
    ftp: float,
    sample_rate_hz: float = 1.0,
    zones: Sequence[tuple[str, float]] = COGGAN_ZONE_UPPER_BOUNDS,
) -> dict[str, float]:
    """Seconds spent in each power zone, keyed by zone name.

    A sample is assigned to the first zone whose upper bound (as a fraction of
    FTP) it does not exceed.
    """
    if ftp <= 0:
        raise ValueError("ftp must be positive")
    seconds_per_sample = 1.0 / sample_rate_hz
    buckets: dict[str, float] = {name: 0.0 for name, _ in zones}
    for p in power:
        frac = p / ftp
        for name, upper in zones:
            if frac <= upper:
                buckets[name] += seconds_per_sample
                break
    return buckets
