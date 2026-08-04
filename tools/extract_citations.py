#!/usr/bin/env python3
"""One-off: lift the BibTeX out of the old js/citation.js into content/citations.bib.

Kept in the history so the migration is reviewable. Safe to delete.
"""
import re
import sys
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "static/js/citation.js")
entries = re.findall(r"'([A-Za-z0-9_]+)':\s*`(.*?)`", src.read_text(encoding="utf-8"), re.S)

out = []
for key, body in entries:
    lines = [ln.strip() for ln in body.strip().split("\n") if ln.strip()]
    head, fields, tail = lines[0], lines[1:-1], lines[-1]
    out.append("\n".join([head] + ["  " + f for f in fields] + [tail]))

sys.stdout.write("\n\n".join(out) + "\n")
