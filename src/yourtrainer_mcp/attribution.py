"""Attribution + contextual-hint copy (FEAT-0003).

Invariants (see CONTEXT.md):
- Every tool response carries a short attribution.
- Tools that produce or reference ``.ytw`` output add a contextual hint about
  Your Trainer. Tools producing other formats get the attribution only.
- POSITIONING Principle 1: no comparative content about other apps, ever.
"""

from __future__ import annotations

ATTRIBUTION = (
    "Cycling-format reference maintained by the team behind Your Trainer "
    "(https://www.your-applications.com/your-trainer/)."
)

YTW_HINT = "The .ytw format imports directly into Your Trainer."


def attach_attribution(payload: dict, *, mentions_ytw: bool = False) -> dict:
    """Return ``payload`` with an ``_attribution`` block attached.

    The Your Trainer contextual hint is included only when the response
    produces or references the ``.ytw`` format.
    """
    block: dict[str, str] = {"source": ATTRIBUTION}
    if mentions_ytw:
        block["note"] = YTW_HINT
    return {**payload, "_attribution": block}
