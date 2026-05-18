"""Tests for pipeline.verbalize and pipeline.faithfulness."""

from __future__ import annotations

import pytest

from pipeline.faithfulness import check, cited_identifiers
from pipeline.verbalize import REGISTERS, verbalize


def test_verbalize_known_declaration_each_register():
    for register in REGISTERS:
        text = verbalize("Nat.Prime.irrational_sqrt", register=register)
        assert text.strip(), f"empty rendering for register {register}"


def test_verbalize_unknown_declaration_raises():
    with pytest.raises(LookupError):
        verbalize("Does.Not.Exist")


def test_verbalize_unknown_register_raises():
    with pytest.raises(ValueError):
        verbalize("Nat.Prime.irrational_sqrt", register="not-a-register")


def test_cited_identifiers_picks_up_dotted_names():
    prose = "We invoke Nat.Prime.not_isSquare and lowercase.not.a.mathlib.name."
    assert "Nat.Prime.not_isSquare" in cited_identifiers(prose)
    # leading lowercase tokens like "lowercase.not.a.mathlib.name" are skipped
    assert all(s[0].isupper() for s in cited_identifiers(prose))


def test_faithfulness_accepts_declared_dependency():
    prose = "Mathlib uses Nat.Prime.not_isSquare to discharge the criterion."
    ok, problems = check("Nat.Prime.irrational_sqrt", prose)
    assert ok, problems


def test_faithfulness_flags_hallucination():
    prose = "We close the proof by Made.Up.Lemma applied to the hypothesis."
    ok, problems = check("Nat.Prime.irrational_sqrt", prose)
    assert not ok
    assert any("Made.Up.Lemma" in p for p in problems)


def test_faithfulness_target_declaration_allowed():
    prose = "By Nat.Prime.irrational_sqrt, √p is irrational."
    ok, problems = check("Nat.Prime.irrational_sqrt", prose)
    assert ok, problems
