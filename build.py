#!/usr/bin/env python3
"""Build graemeblair.com and the CV source from content/*.yml.

    python build.py                  # render everything into _site/
    python build.py --escape-report  # list characters with no LaTeX mapping

Output goes to `_site/` and is never committed. `index.html` and
`GraemeBlair-CV.tex` are generated -- edit `content/*.yml` instead. See AGENTS.md.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

from sitegen.content import CONTENT, ContentError, load  # noqa: E402
from sitegen.escape import unmapped_characters  # noqa: E402
from sitegen.envs import STATIC  # noqa: E402
from sitegen.targets import html as html_target, latex as latex_target  # noqa: E402


def copy_static(out: Path) -> int:
    """Mirror static/ into the output. Paths map 1:1, so this is a plain copy."""
    shutil.copytree(STATIC, out, dirs_exist_ok=True)
    return sum(1 for p in out.rglob("*") if p.is_file())


def escape_report(content: dict) -> int:
    """Report every non-ASCII character with no entry in the LaTeX table."""
    found: dict[str, list[str]] = {}

    def walk(node, trail: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{trail}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{trail}[{i}]")
        elif isinstance(node, str):
            for char in unmapped_characters(node):
                found.setdefault(char, []).append(trail.lstrip("."))

    walk(content, "")
    if not found:
        print("escape report: every non-ASCII character has a LaTeX mapping")
        return 0
    for char, where in sorted(found.items()):
        print(f"U+{ord(char):04X} {char!r}  {len(where)} use(s), first at {where[0]}")
    return 1


def build(out: Path) -> None:
    content = load(CONTENT)

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    files = copy_static(out)
    print(f"static:  {files} files -> {out}")

    page = html_target.write(content, out)
    print(f"html:    {page.relative_to(REPO)} ({len(page.read_bytes()):,} bytes)")

    tex = latex_target.write(content, out)
    print(f"latex:   {tex.relative_to(REPO)} ({len(tex.read_bytes()):,} bytes)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPO / "_site")
    parser.add_argument(
        "--escape-report",
        action="store_true",
        help="list content characters with no LaTeX mapping, then exit",
    )
    args = parser.parse_args(argv)

    try:
        if args.escape_report:
            return escape_report(load(CONTENT))
        build(args.out)
    except ContentError as exc:
        print(f"content error: {exc}", file=sys.stderr)
        return 1
    except latex_target.TexLintError as exc:
        print(f"latex error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
