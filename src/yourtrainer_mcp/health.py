"""Operational health metrics (TASK-0017).

Strictly aggregate, in-process counters — NO per-call records, NO request
payloads, NO IP/rider data retained (CONTEXT.md statelessness invariant).
Counters live for the process lifetime and reset on restart. This exists to
answer "is the server healthy and what's the load shape?", never "who called
what".
"""

from __future__ import annotations

import threading

_lock = threading.Lock()
_requests_total = 0
_errors_total = 0
_by_tool: dict[str, int] = {}
_errors_by_tool: dict[str, int] = {}
# Monotonic start marker is injected by the server at process start (Date.now is
# unavailable in some sandboxes; the server passes time.monotonic()).
_start_monotonic: float | None = None


def set_start(monotonic_seconds: float) -> None:
    global _start_monotonic
    _start_monotonic = monotonic_seconds


def record(tool_name: str, ok: bool) -> None:
    """Increment aggregate counters for one tool invocation."""
    global _requests_total, _errors_total
    with _lock:
        _requests_total += 1
        _by_tool[tool_name] = _by_tool.get(tool_name, 0) + 1
        if not ok:
            _errors_total += 1
            _errors_by_tool[tool_name] = _errors_by_tool.get(tool_name, 0) + 1


def snapshot(now_monotonic: float | None = None) -> dict:
    """Return the current aggregate metrics (no per-call detail)."""
    with _lock:
        uptime = None
        if _start_monotonic is not None and now_monotonic is not None:
            uptime = round(now_monotonic - _start_monotonic, 1)
        return {
            "requests_total": _requests_total,
            "errors_total": _errors_total,
            "error_rate": round(_errors_total / _requests_total, 4) if _requests_total else 0.0,
            "by_tool": dict(_by_tool),
            "errors_by_tool": dict(_errors_by_tool),
            "uptime_s": uptime,
            "note": "Aggregate-only; no per-call records, no rider data retained.",
        }


def reset() -> None:
    """Reset all counters (used by tests)."""
    global _requests_total, _errors_total, _start_monotonic
    with _lock:
        _requests_total = 0
        _errors_total = 0
        _by_tool.clear()
        _errors_by_tool.clear()
        _start_monotonic = None
