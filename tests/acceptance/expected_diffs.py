"""Pre-registered, deliberate deviations from the frozen baseline.

The acceptance suite compares the built site against `baseline/`, which is a
byte-for-byte snapshot of the hand-written site at the commit recorded in
`baseline/COMMIT`. Any difference fails -- unless it is listed here.

The rule: a deviation gets an entry BEFORE the change lands, with a reason a
reader can evaluate. Nothing is fixed silently. Several of these are visible
behavior changes, not cosmetic cleanups, and the owner has to agree to each one.

Each entry is (kind, key, reason):
  kind  "id" | "citation" | "href" | "src" | "toggle" | "text"
  key   the exact value that differs
"""

from __future__ import annotations

EXPECTED_DIFFS: list[tuple[str, str, str]] = [
    # --- filled in as changes are proposed; empty means "must match exactly" ---
]


def is_expected(kind: str, key: str) -> bool:
    return any(k == kind and v == key for k, v, _ in EXPECTED_DIFFS)


def reason(kind: str, key: str) -> str | None:
    for k, v, why in EXPECTED_DIFFS:
        if k == kind and v == key:
            return why
    return None


def describe(kind: str, key: str) -> str:
    why = reason(kind, key)
    return f"{kind} {key!r}: {why}" if why else f"{kind} {key!r}: UNREGISTERED"
