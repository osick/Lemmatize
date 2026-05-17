"""Resolve a Mathlib declaration name to its Lemmatize entry, if any.

Acceptance criterion: covers the `lemmatize lookup <decl>` subcommand.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
ENTRIES_DIR = REPO_ROOT / "lemmatize"


@lru_cache(maxsize=1)
def _index() -> dict[str, dict]:
    """Build {mathlib_declaration: entry} once per process."""
    index: dict[str, dict] = {}
    for path in sorted(ENTRIES_DIR.glob("*.yaml")):
        entry = yaml.safe_load(path.read_text())
        if not isinstance(entry, dict):
            continue
        decl = entry.get("mathlib_declaration")
        if decl:
            index[decl] = entry
    return index


def lookup(declaration: str) -> dict | None:
    """Return the entry for a Mathlib declaration, or None if not in the ontology."""
    return _index().get(declaration)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Resolve a Mathlib declaration to a Lemmatize entry.")
    parser.add_argument("declaration", help="Fully-qualified Mathlib declaration name.")
    args = parser.parse_args(argv)

    entry = lookup(args.declaration)
    if entry is None:
        print(f"no entry for {args.declaration}")
        return 1
    print(yaml.safe_dump(entry, sort_keys=False, allow_unicode=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
