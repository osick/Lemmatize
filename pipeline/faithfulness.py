"""Weak faithfulness check (R4.3).

Given a target Mathlib declaration and a prose verbalization, verify that every
Mathlib identifier named in prose either matches the target or appears in the
declared `dependencies` of the corresponding Lemmatize entry.

The strong check (every step of prose corresponds to a step of the proof) is
future work.
"""

from __future__ import annotations

import re
from pathlib import Path

from pipeline.lookup import lookup


MATHLIB_IDENT_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_']*)+\b")


def cited_identifiers(prose: str) -> set[str]:
    """Return the set of dotted Mathlib-style identifiers mentioned in prose."""
    return set(MATHLIB_IDENT_RE.findall(prose))


def check(declaration: str, prose: str) -> tuple[bool, list[str]]:
    """Return (ok, problems). `problems` is empty when ok is True."""
    entry = lookup(declaration)
    if entry is None:
        return False, [f"no Lemmatize entry for {declaration}; cannot check faithfulness"]

    allowed = {declaration}
    for dep in entry.get("dependencies", []) or []:
        d = dep.get("declaration")
        if d:
            allowed.add(d)

    problems: list[str] = []
    for ident in sorted(cited_identifiers(prose)):
        if ident not in allowed:
            problems.append(
                f"hallucinated reference: {ident!r} is cited in prose but not in the proof DAG of {declaration}"
            )
    return (not problems), problems


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Weak faithfulness check.")
    parser.add_argument("declaration", help="Target Mathlib declaration.")
    parser.add_argument("prose_file", type=Path, help="Path to the generated prose.")
    args = parser.parse_args(argv)

    prose = args.prose_file.read_text()
    ok, problems = check(args.declaration, prose)
    if ok:
        print("OK: no hallucinated references")
        return 0
    for p in problems:
        print(p)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
