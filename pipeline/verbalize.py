"""Stored-template verbalizer (R4 stage 3, first cut).

This module selects a pre-written verbalization from a Lemmatize entry and
optionally substitutes the canonical name of each declared dependency for its
Mathlib identifier. It does not call an LLM; the LLM-driven verbalizer will be
layered on top in the next iteration.

Three registers are exposed, matching the schema:
  - researcher
  - faithful_to_mathlib
  - textbook_classical
"""

from __future__ import annotations

import argparse

from pipeline.lookup import lookup


REGISTERS = ("researcher", "faithful_to_mathlib", "textbook_classical")


def verbalize(declaration: str, register: str = "faithful_to_mathlib") -> str:
    if register not in REGISTERS:
        raise ValueError(f"register must be one of {REGISTERS}, got {register!r}")
    entry = lookup(declaration)
    if entry is None:
        raise LookupError(f"no Lemmatize entry for {declaration}")
    text = entry["verbalization"][register]
    return text.rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a stored verbalization for a Mathlib declaration.")
    parser.add_argument("declaration")
    parser.add_argument(
        "--register",
        choices=REGISTERS,
        default="faithful_to_mathlib",
        help="Which stored register to render (default: faithful_to_mathlib).",
    )
    args = parser.parse_args(argv)

    try:
        print(verbalize(args.declaration, args.register), end="")
    except LookupError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
