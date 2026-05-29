"""Tests for the static docs-site generator (TASK-0055)."""

from __future__ import annotations

from yourtrainer_mcp import docs_site, registry


def test_build_site_writes_index_and_all_formats(tmp_path):
    summary = docs_site.build_site(tmp_path)
    keys = registry.format_keys()
    # index + one page per format.
    assert summary["pages"] == len(keys) + 1
    assert (tmp_path / "index.html").exists()
    for key in keys:
        assert (tmp_path / f"{key}.html").exists()


def test_index_lists_every_format(tmp_path):
    docs_site.build_site(tmp_path)
    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    for key in registry.format_keys():
        assert f'href="{key}.html"' in index


def test_format_page_has_spec_examples_and_attribution(tmp_path):
    docs_site.build_site(tmp_path)
    page = (tmp_path / "zwo.html").read_text(encoding="utf-8")
    assert "<h2>Spec</h2>" in page
    assert "<h2>Examples</h2>" in page
    assert "Your Trainer" in page  # attribution footer
    # The corpus version string is surfaced.
    assert registry.get_version("zwo") in page


def test_examples_are_html_escaped(tmp_path):
    docs_site.build_site(tmp_path)
    page = (tmp_path / "zwo.html").read_text(encoding="utf-8")
    # ZWO examples contain XML; raw '<workout_file>' must be escaped in <pre>.
    assert "&lt;workout_file&gt;" in page
    assert "<workout_file>" not in page  # never emitted raw


def test_no_comparative_content_on_pages(tmp_path):
    docs_site.build_site(tmp_path)
    banned = ["better than", "worse than", "superior to", "inferior to"]
    for key in registry.format_keys():
        text = (tmp_path / f"{key}.html").read_text(encoding="utf-8").lower()
        for phrase in banned:
            assert phrase not in text
