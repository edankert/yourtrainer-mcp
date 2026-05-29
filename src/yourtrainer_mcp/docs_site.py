"""Static docs-site generator for the knowledge corpus (TASK-0055).

Renders the packaged ``specs/`` corpus to dependency-free static HTML so the
same source of truth serves LLM clients (via MCP) and human readers (the public
docs-site mirror). POSITIONING-compliant: attribution in the footer, never any
comparative content.

The output is generated into a target directory (``build/docs-site`` by
default); it is not committed — hosting it is a deploy step.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from . import registry
from .attribution import ATTRIBUTION

_CSS = """
:root { color-scheme: light dark; }
body { font: 16px/1.6 system-ui, sans-serif; max-width: 52rem; margin: 3rem auto;
       padding: 0 1rem; }
h1 a { text-decoration: none; }
code, pre { background: rgba(127,127,127,.12); border-radius: 6px; }
pre { padding: 1rem; overflow:auto; } code { padding: .1rem .35rem; }
.kind { color:#777; font-weight:400; font-size:.9rem; }
table { border-collapse: collapse; width:100%; } td,th { text-align:left;
       border-bottom:1px solid rgba(127,127,127,.25); padding:.4rem .6rem; vertical-align:top; }
footer { margin-top:3rem; color:#777; font-size:.85rem; border-top:1px solid rgba(127,127,127,.25);
         padding-top:1rem; }
nav a { margin-right:.8rem; }
"""


def _page(title: str, body: str) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{escape(title)}</title><style>{_CSS}</style></head><body>\n"
        f"{body}\n"
        f"<footer>{escape(ATTRIBUTION)}</footer>\n"
        "</body></html>\n"
    )


def _format_page(key: str) -> str:
    f = registry.get_format(key)
    parts = ["<p><a href=\"index.html\">← all formats</a></p>",
             f"<h1>{escape(f['name'])} "
             f"<span class=\"kind\">{escape(f['kind'])}"
             f"{' · binary' if f['binary'] else ''}</span></h1>",
             f"<p><strong>Key:</strong> <code>{escape(key)}</code> · "
             f"<strong>Version:</strong> {escape(f.get('version', ''))}</p>",
             "<h2>Spec</h2>", f"<p>{escape(f['spec'])}</p>"]

    examples = registry.get_examples(key)
    if examples:
        parts.append("<h2>Examples</h2>")
        for ex in examples:
            parts.append(f"<h3>{escape(ex.get('title', 'Example'))}</h3>")
            parts.append(f"<pre><code>{escape(ex.get('content', ''))}</code></pre>")

    constraints = registry.get_constraints(key)
    if constraints:
        parts.append("<h2>Constraints</h2><table><tr><th>App</th><th>Note</th></tr>")
        for c in constraints:
            parts.append(f"<tr><td>{escape(str(c.get('app','')))}</td>"
                         f"<td>{escape(str(c.get('note','')))}</td></tr>")
        parts.append("</table>")

    notes = registry.get_conversion_notes(key)
    if notes:
        parts.append("<h2>Conversion notes</h2><table><tr><th>To</th><th>Note</th></tr>")
        for n in notes:
            parts.append(f"<tr><td>{escape(str(n.get('to','')))}</td>"
                         f"<td>{escape(str(n.get('note','')))}</td></tr>")
        parts.append("</table>")

    glossary = registry.get_glossary(key)
    if glossary:
        parts.append("<h2>Glossary</h2><table><tr><th>Term</th><th>Definition</th></tr>")
        for g in glossary:
            parts.append(f"<tr><td>{escape(str(g.get('term','')))}</td>"
                         f"<td>{escape(str(g.get('definition','')))}</td></tr>")
        parts.append("</table>")

    return _page(f"{f['name']} — cycling format reference", "\n".join(parts))


def _index_page() -> str:
    rows = []
    for key in registry.format_keys():
        f = registry.get_format(key)
        rows.append(
            f"<tr><td><a href=\"{escape(key)}.html\">{escape(f['name'])}</a></td>"
            f"<td><code>{escape(key)}</code></td><td>{escape(f['kind'])}</td>"
            f"<td>{'binary' if f['binary'] else 'text'}</td></tr>"
        )
    body = (
        "<h1>Cycling-format reference</h1>"
        "<p>Structured documentation for the indoor-cycling format ecosystem — "
        "specs, canonical examples, constraints, conversion notes, and glossaries. "
        "The same corpus is served to LLM clients via the "
        "<code>mcp.your-applications.com/your-trainer</code> MCP server.</p>"
        "<table><tr><th>Format</th><th>Key</th><th>Kind</th><th>Encoding</th></tr>"
        + "\n".join(rows) + "</table>"
    )
    return _page("Cycling-format reference", body)


def build_site(out_dir: str | Path = "build/docs-site") -> dict:
    """Generate the static docs site. Returns a summary of what was written."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = ["index.html"]
    (out / "index.html").write_text(_index_page(), encoding="utf-8")
    for key in registry.format_keys():
        name = f"{key}.html"
        (out / name).write_text(_format_page(key), encoding="utf-8")
        written.append(name)
    return {"out_dir": str(out), "pages": len(written), "files": written}
