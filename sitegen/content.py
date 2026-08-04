"""Load and validate content/*.yml.

One namespace per file: `content/site.yml` arrives in templates as `site`,
`content/teaching.yml` as `teaching`, and so on. Files are optional so that
categories can be migrated one at a time without every template needing to know
which ones exist yet.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "content"


class ContentError(ValueError):
    pass


def load_one(path: Path):
    try:
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ContentError(f"{path.name}: {exc}") from exc


def load(directory: Path = CONTENT) -> dict:
    """Load every content/*.yml into a namespace keyed by filename stem."""
    data: dict = {}
    for path in sorted(directory.glob("*.yml")):
        value = load_one(path)
        if value is None:
            raise ContentError(f"{path.name} is empty")
        data[path.stem] = value

    _reject_unresolved(data)
    return data


def _reject_unresolved(data, trail: str = "") -> None:
    """Fail on any UNRESOLVED marker left by an extraction script.

    Extractors never pick a winner when the site and the CV disagree -- they
    write UNRESOLVED and leave the decision to a human. This makes forgetting to
    decide a build failure rather than a silent choice.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            _reject_unresolved(value, f"{trail}.{key}")
    elif isinstance(data, list):
        for i, value in enumerate(data):
            _reject_unresolved(value, f"{trail}[{i}]")
    elif isinstance(data, str) and "UNRESOLVED" in data:
        raise ContentError(
            f"{trail.lstrip('.')} still contains UNRESOLVED -- a site/CV "
            f"disagreement needs a decision before this can build"
        )
