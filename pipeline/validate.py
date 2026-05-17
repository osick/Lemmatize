"""Validate Lemmatize YAML entries against the schema and cross-references.

Acceptance criterion A4 in docs/requirements.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "entry.schema.json"
VOCAB_PATH = REPO_ROOT / "schema" / "proof-methods.yaml"
ENTRIES_DIR = REPO_ROOT / "lemmatize"


@dataclass
class ValidationReport:
    files_checked: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def _load_vocab() -> set[str]:
    data = yaml.safe_load(VOCAB_PATH.read_text())
    return {tag["id"] for tag in data["tags"]}


def _load_entry(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def validate_entry(path: Path, schema: dict, vocab: set[str], known_ids: set[str]) -> list[str]:
    """Return a list of error strings for a single YAML file. Empty list = OK."""
    errors: list[str] = []
    try:
        entry = _load_entry(path)
    except yaml.YAMLError as exc:
        return [f"{path.name}: YAML parse error: {exc}"]

    if not isinstance(entry, dict):
        return [f"{path.name}: top-level YAML must be a mapping"]

    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(entry), key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path.name}: schema error at {loc}: {err.message}")

    expected_id = path.stem
    if entry.get("id") != expected_id:
        errors.append(
            f"{path.name}: id field {entry.get('id')!r} does not match filename stem {expected_id!r}"
        )

    for field_name in ("proof_method_lean", "proof_method_textbook"):
        for tag in entry.get(field_name, []) or []:
            if tag not in vocab:
                errors.append(
                    f"{path.name}: {field_name} contains unknown tag {tag!r}; "
                    f"add it to schema/proof-methods.yaml or fix the entry"
                )

    for dep in entry.get("dependencies", []) or []:
        dep_id = dep.get("lemmatize_id")
        if dep_id is not None and dep_id not in known_ids and dep_id != expected_id:
            errors.append(
                f"{path.name}: dependency lemmatize_id {dep_id!r} does not resolve to any entry"
            )

    return errors


def validate_all(entries_dir: Path = ENTRIES_DIR) -> ValidationReport:
    schema = _load_schema()
    vocab = _load_vocab()

    paths = sorted(p for p in entries_dir.glob("*.yaml"))
    known_ids = {p.stem for p in paths}

    report = ValidationReport()
    for path in paths:
        report.files_checked += 1
        report.errors.extend(validate_entry(path, schema, vocab, known_ids))
    return report


def main() -> int:
    report = validate_all()
    if report.ok:
        print(f"OK: {report.files_checked} entry/entries validated")
        return 0
    for err in report.errors:
        print(err)
    print(f"FAIL: {len(report.errors)} error(s) across {report.files_checked} file(s)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
