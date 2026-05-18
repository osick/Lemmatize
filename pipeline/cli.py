"""`lemmatize` command-line entry point.

Subcommands:
  validate            check all YAML entries (R4.2)
  lookup <decl>       resolve a Mathlib declaration to its entry
  verbalize <decl>    run the LLM verbalizer (not yet implemented)
  check <decl> <file> weak faithfulness check on a prose file
"""

from __future__ import annotations

import argparse
import sys

from pipeline import validate, lookup, faithfulness, verbalize as verbalize_mod


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lemmatize")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate", help="Validate all YAML entries against the schema.")

    p_lookup = sub.add_parser("lookup", help="Resolve a Mathlib declaration to a Lemmatize entry.")
    p_lookup.add_argument("declaration")

    p_verb = sub.add_parser("verbalize", help="Render a stored verbalization for a Mathlib declaration.")
    p_verb.add_argument("declaration")
    p_verb.add_argument(
        "--register",
        choices=verbalize_mod.REGISTERS,
        default="faithful_to_mathlib",
    )

    p_check = sub.add_parser("check", help="Weak faithfulness check on a prose file.")
    p_check.add_argument("declaration")
    p_check.add_argument("prose_file")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "validate":
        return validate.main()
    if args.cmd == "lookup":
        return lookup.main([args.declaration])
    if args.cmd == "verbalize":
        return verbalize_mod.main([args.declaration, "--register", args.register])
    if args.cmd == "check":
        return faithfulness.main([args.declaration, args.prose_file])

    print(f"unknown command: {args.cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
