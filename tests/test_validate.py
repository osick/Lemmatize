"""Tests for pipeline.validate. Acceptance criterion A6 in docs/requirements.md."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml

from pipeline.validate import (
    ENTRIES_DIR,
    SCHEMA_PATH,
    VOCAB_PATH,
    validate_all,
    validate_entry,
)


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def _vocab() -> set[str]:
    data = yaml.safe_load(VOCAB_PATH.read_text())
    return {tag["id"] for tag in data["tags"]}


def _seed_entry() -> dict:
    return yaml.safe_load((ENTRIES_DIR / "irrational-sqrt-two.yaml").read_text())


def test_repo_validates_clean():
    report = validate_all()
    assert report.ok, report.errors
    assert report.files_checked >= 1


def test_missing_required_field_fails(tmp_path: Path):
    entry = _seed_entry()
    del entry["verbalization"]
    p = tmp_path / "irrational-sqrt-two.yaml"
    p.write_text(yaml.safe_dump(entry, sort_keys=False, allow_unicode=True))

    errors = validate_entry(p, _schema(), _vocab(), known_ids={"irrational-sqrt-two"})
    assert any("verbalization" in e for e in errors), errors


def test_unknown_proof_method_fails(tmp_path: Path):
    entry = _seed_entry()
    entry["proof_method_lean"] = ["not-a-real-tag"]
    p = tmp_path / "irrational-sqrt-two.yaml"
    p.write_text(yaml.safe_dump(entry, sort_keys=False, allow_unicode=True))

    errors = validate_entry(p, _schema(), _vocab(), known_ids={"irrational-sqrt-two"})
    assert any("not-a-real-tag" in e for e in errors), errors


def test_id_must_match_filename(tmp_path: Path):
    entry = _seed_entry()
    entry["id"] = "wrong-id"
    p = tmp_path / "irrational-sqrt-two.yaml"
    p.write_text(yaml.safe_dump(entry, sort_keys=False, allow_unicode=True))

    errors = validate_entry(p, _schema(), _vocab(), known_ids={"irrational-sqrt-two"})
    assert any("filename stem" in e for e in errors), errors


def test_dangling_lemmatize_id_fails(tmp_path: Path):
    entry = copy.deepcopy(_seed_entry())
    entry["dependencies"].append({
        "declaration": "Made.Up.Decl",
        "canonical_name": "Made up",
        "gloss": "Should fail because lemmatize_id does not exist.",
        "lemmatize_id": "does-not-exist",
    })
    p = tmp_path / "irrational-sqrt-two.yaml"
    p.write_text(yaml.safe_dump(entry, sort_keys=False, allow_unicode=True))

    errors = validate_entry(p, _schema(), _vocab(), known_ids={"irrational-sqrt-two"})
    assert any("does-not-exist" in e for e in errors), errors
