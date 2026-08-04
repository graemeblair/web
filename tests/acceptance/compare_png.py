#!/usr/bin/env python3
"""Compare two PNGs pixel by pixel.

Used by Gate 3 (browser screenshots) and Gate 4 (pdftoppm page images). Reports
the fraction of differing pixels and the bounding box containing them, because
"0.4% of pixels differ" is useless without knowing whether they are scattered
antialiasing noise or one shifted paragraph.

Usage:
    python compare_png.py A.png B.png [--threshold 0.001] [--out diff.png]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops


def compare(a: Path, b: Path, out: Path | None = None) -> dict:
    ia = Image.open(a).convert("RGB")
    ib = Image.open(b).convert("RGB")

    if ia.size != ib.size:
        # Pad both to the union size rather than bailing: a height change is
        # itself the finding, and we still want the bounding box of where the
        # content diverged.
        w = max(ia.width, ib.width)
        h = max(ia.height, ib.height)
        pa = Image.new("RGB", (w, h), "white")
        pb = Image.new("RGB", (w, h), "white")
        pa.paste(ia, (0, 0))
        pb.paste(ib, (0, 0))
        ia, ib = pa, pb
        size_mismatch = True
    else:
        size_mismatch = False

    delta = ImageChops.difference(ia, ib)
    bbox = delta.getbbox()
    # Any channel differing by more than 8/255 counts; below that is renderer
    # antialiasing jitter, not a content change.
    mask = delta.convert("L").point(lambda p: 255 if p > 8 else 0)
    differing = sum(mask.histogram()[1:])
    total = ia.width * ia.height

    if out is not None and bbox:
        strip = Image.new("RGB", (ia.width * 3, ia.height), "white")
        strip.paste(ia, (0, 0))
        strip.paste(ib, (ia.width, 0))
        strip.paste(delta, (ia.width * 2, 0))
        strip.save(out)

    return {
        "a": str(a),
        "b": str(b),
        "size_mismatch": size_mismatch,
        "differing_pixels": differing,
        "total_pixels": total,
        "fraction": differing / total if total else 0.0,
        "bbox": bbox,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("a", type=Path)
    p.add_argument("b", type=Path)
    p.add_argument("--threshold", type=float, default=0.001)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)

    r = compare(args.a, args.b, args.out)
    print(
        f"{r['fraction']:.5%} differing ({r['differing_pixels']}/{r['total_pixels']}) "
        f"bbox={r['bbox']} size_mismatch={r['size_mismatch']}"
    )
    return 0 if r["fraction"] <= args.threshold and not r["size_mismatch"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
