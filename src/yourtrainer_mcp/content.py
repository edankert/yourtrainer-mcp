"""Your Trainer website content client (FEAT-0007, ADR-0006).

The MCP acts as a **stateless proxy over public Your Trainer content** hosted on
the website: the curated workout library, the AI-assistant skill catalogue, and
the product manual. Content is fetched over HTTP (stdlib ``urllib`` — no new
dependency) with a short in-process TTL cache.

Statelessness: the cache holds **public content only** (a manifest, workout
files, help pages) — never rider data — so it does not violate the
no-cross-call-leakage invariant. It exists purely to avoid hammering the website.

The fetcher is injectable (``set_fetcher``) so tests run against local fixtures
with no network.
"""

from __future__ import annotations

import json
import time
import urllib.request
from collections.abc import Callable
from html.parser import HTMLParser

DEFAULT_BASE_URL = "https://www.your-applications.com/your-trainer"
CACHE_TTL_S = 300.0

_base_url = DEFAULT_BASE_URL
_cache: dict[str, tuple[float, str]] = {}


def _urllib_fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "yourtrainer-mcp"})
    with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310 - https only
        return resp.read().decode("utf-8", "replace")


_fetcher: Callable[[str], str] = _urllib_fetch


def set_fetcher(fn: Callable[[str], str]) -> None:
    """Override the fetcher (tests inject a local-fixture reader)."""
    global _fetcher
    _fetcher = fn
    _cache.clear()


def set_base_url(url: str) -> None:
    global _base_url
    _base_url = url.rstrip("/")
    _cache.clear()


def clear_cache() -> None:
    _cache.clear()


def fetch_text(path: str) -> str:
    """Fetch ``<base>/<path>`` as text, with a TTL cache (public content only)."""
    now = time.monotonic()
    hit = _cache.get(path)
    if hit is not None and now - hit[0] < CACHE_TTL_S:
        return hit[1]
    url = f"{_base_url}/{path.lstrip('/')}"
    text = _fetcher(url)
    _cache[path] = (now, text)
    return text


# --------------------------------------------------------------------------- #
# Workout library (manifest-driven)
# --------------------------------------------------------------------------- #

def library_manifest() -> dict:
    return json.loads(fetch_text("library/manifest.json"))


def list_workouts(
    set_: str | None = None,
    category: str | None = None,
    max_duration_s: int | None = None,
    requires_power: bool | None = None,
) -> list[dict]:
    """Filtered workout metadata from the library manifest (no .ytw bodies)."""
    out = []
    for w in library_manifest().get("workouts", []):
        if set_ and w.get("set") != set_:
            continue
        if category and w.get("category") != category:
            continue
        if max_duration_s is not None and (w.get("duration_seconds") or 0) > max_duration_s:
            continue
        if requires_power is not None and bool(w.get("requires_power_meter")) != requires_power:
            continue
        out.append(_workout_summary(w))
    return out


def _workout_summary(w: dict) -> dict:
    keys = ("slug", "name", "set", "category", "duration_seconds", "intensity_summary",
            "tss", "intensity_factor", "difficulty_score", "discipline_tags",
            "physiology_focus", "requires_power_meter")
    return {k: w[k] for k in keys if k in w}


def get_workout(slug: str) -> dict:
    """Workout metadata plus the fetched ``.ytw`` document for ``slug``."""
    for w in library_manifest().get("workouts", []):
        if w.get("slug") == slug:
            summary = _workout_summary(w)
            file_path = w.get("file_path")
            summary["ytw"] = fetch_text(file_path) if file_path else None
            return summary
    raise KeyError(f"workout not found: {slug}")


def search_workouts(query: str, limit: int = 10) -> list[dict]:
    q = query.lower()
    scored = []
    for w in library_manifest().get("workouts", []):
        hay = " ".join(str(w.get(k, "")) for k in
                       ("name", "category", "intensity_summary")).lower()
        tags = " ".join(w.get("discipline_tags", []) + w.get("physiology_focus", [])).lower()
        score = hay.count(q) * 2 + tags.count(q)
        if q in hay or q in tags:
            scored.append((score, _workout_summary(w)))
    scored.sort(key=lambda t: -t[0])
    return [w for _, w in scored[:limit]]


# --------------------------------------------------------------------------- #
# HTML section parsing (manual + AI skills)
# --------------------------------------------------------------------------- #

class _SectionParser(HTMLParser):
    """Split a help page into sections at h1/h2/h3 boundaries."""

    def __init__(self) -> None:
        super().__init__()
        self.sections: list[dict] = []
        self._cur: dict | None = None
        self._in_heading = False
        self._heading_id: str | None = None
        self._skip = 0  # depth inside script/style

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
            return
        if tag in ("h1", "h2", "h3"):
            self._flush()
            self._in_heading = True
            self._heading_id = dict(attrs).get("id")
            self._cur = {"level": int(tag[1]), "id": self._heading_id, "title": "", "text": ""}

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        if tag in ("h1", "h2", "h3"):
            self._in_heading = False

    def handle_data(self, data):
        if self._skip or self._cur is None:
            return
        if self._in_heading:
            self._cur["title"] += data
        else:
            self._cur["text"] += data

    def _flush(self):
        if self._cur is not None:
            self._cur["title"] = " ".join(self._cur["title"].split())
            self._cur["text"] = " ".join(self._cur["text"].split())
            if self._cur["title"]:
                self.sections.append(self._cur)
        self._cur = None

    def close(self):
        super().close()
        self._flush()


def _parse_sections(html: str) -> list[dict]:
    p = _SectionParser()
    p.feed(html)
    p.close()
    return p.sections


def _slug(title: str) -> str:
    return "-".join("".join(c if c.isalnum() else " " for c in title.lower()).split())


def manual_sections() -> list[dict]:
    secs = _parse_sections(fetch_text("manual.html"))
    for s in secs:
        s.setdefault("id", None)
        s["key"] = s["id"] or _slug(s["title"])
    return secs


def search_manual(query: str, limit: int = 5) -> list[dict]:
    q = query.lower()
    scored = []
    for s in manual_sections():
        score = s["title"].lower().count(q) * 3 + s["text"].lower().count(q)
        if q in s["title"].lower() or q in s["text"].lower():
            snippet = _snippet(s["text"], q)
            scored.append((score, {"key": s["key"], "title": s["title"], "snippet": snippet}))
    scored.sort(key=lambda t: -t[0])
    return [s for _, s in scored[:limit]]


def get_manual_section(key: str) -> dict:
    for s in manual_sections():
        if s["key"] == key or s["title"].lower() == key.lower():
            return {"key": s["key"], "title": s["title"], "text": s["text"]}
    raise KeyError(f"manual section not found: {key}")


def _snippet(text: str, q: str, width: int = 160) -> str:
    i = text.lower().find(q)
    if i < 0:
        return text[:width]
    start = max(0, i - width // 2)
    prefix = "…" if start else ""
    suffix = "…" if start + width < len(text) else ""
    return prefix + text[start:start + width] + suffix


def ai_skills() -> list[dict]:
    """The AI-assistant skill/prompt catalogue, parsed from ai-skills.html."""
    out = []
    for s in _parse_sections(fetch_text("ai-skills.html")):
        if s["level"] >= 3 and s["title"].lower() != "on this page":
            out.append({"key": s.get("id") or _slug(s["title"]),
                        "title": s["title"], "summary": _snippet(s["text"], "", 200)})
    return out
