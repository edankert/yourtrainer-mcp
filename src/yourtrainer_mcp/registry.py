"""Knowledge-registry loader + query API (FEAT-0001).

The per-format corpus lives as packaged JSON under ``yourtrainer_mcp/specs/``.
Each file documents one format: spec summary, ≥3 canonical examples, known
per-app constraints, conversion notes, glossary, and version. These power the
registry MCP tools (``get_format_spec`` etc.) and double as the source for the
public docs-site mirror (a later FEAT-0001 task).

Corpus content is descriptive and never comparative (POSITIONING Principle 1).
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources


class UnknownFormat(KeyError):
    """Raised when a format key is not in the registry."""


@lru_cache(maxsize=1)
def _load_all() -> dict[str, dict]:
    corpus: dict[str, dict] = {}
    specs_dir = resources.files("yourtrainer_mcp") / "specs"
    for entry in specs_dir.iterdir():
        if entry.name.endswith(".json"):
            data = json.loads(entry.read_text(encoding="utf-8"))
            corpus[data["key"]] = data
    return corpus


def format_keys() -> list[str]:
    return sorted(_load_all())


def get_format(key: str) -> dict:
    corpus = _load_all()
    if key not in corpus:
        raise UnknownFormat(f"unknown format '{key}'; known: {', '.join(sorted(corpus))}")
    return corpus[key]


def get_spec(key: str) -> dict:
    f = get_format(key)
    return {"key": f["key"], "name": f["name"], "kind": f["kind"],
            "binary": f["binary"], "version": f.get("version", ""), "spec": f["spec"]}


def get_examples(key: str) -> list[dict]:
    return get_format(key).get("examples", [])


def get_constraints(key: str) -> list[dict]:
    return get_format(key).get("constraints", [])


def get_conversion_notes(key: str) -> list[dict]:
    return get_format(key).get("conversion_notes", [])


def get_glossary(key: str) -> list[dict]:
    return get_format(key).get("glossary", [])


def get_version(key: str) -> str:
    return get_format(key).get("version", "")
