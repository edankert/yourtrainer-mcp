#!/usr/bin/env python3
"""Build the public docs-site mirror from the knowledge corpus (TASK-0055).

    python scripts/build_docs.py [out_dir]      # default: build/docs-site

Output is dependency-free static HTML; serve the directory as the public docs
site (e.g. cycling-formats.your-applications.com). Not committed (build/).
"""

from __future__ import annotations

import sys

from yourtrainer_mcp.docs_site import build_site


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "build/docs-site"
    summary = build_site(out)
    print(f"Wrote {summary['pages']} pages to {summary['out_dir']}/")
    for f in summary["files"]:
        print(f"  {f}")


if __name__ == "__main__":
    main()
