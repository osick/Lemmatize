# Lemmatize

*An ontology-driven natural-language layer for Lean's Mathlib.*

> **A note on the name.** *Lemmatize* here refers to mathematical **lemmas**, not the NLP operation that maps inflected words to dictionary headwords. The collision with NLTK and spaCy is intentional — the target audience straddles formal methods and NLP — but every occurrence of "lemmatize" in this repository should be read in the mathematical sense.

Mathlib4 contains over 210,000 formally verified theorems. Each one is type-checked by Lean's kernel, but the identifiers (`Nat.Coprime.dvd_of_dvd_mul_right`) bear no resemblance to the names mathematicians actually use (`Euclid's lemma`). Lemmatize is a curated, machine-readable layer that records, for each notable theorem in Mathlib:

- its named-theorem identity (Wikidata Q-ID),
- canonical name in multiple languages,
- a short prose statement,
- the proof method Lean uses **and** the proof method a textbook would use (often different),
- declared dependencies on other named theorems,
- pre-written verbalizations at multiple registers,
- a verification trail tying every claim to a source.

The vision and motivation live in [`docs/idea.md`](docs/idea.md). The concrete requirements for this proof-of-concept live in [`docs/requirements.md`](docs/requirements.md).

## Status

Early scaffolding. Five seed YAML entries cover √2, the infinitude of primes, Euclid's lemma, the fundamental theorem of arithmetic, and Bezout's identity. The CLI supports `validate`, `lookup`, `verbalize` (stored-template), and `check` (weak faithfulness). The LLM-driven verbalizer, the LeanDojo extraction bridge, and a pinned-commit pass over the seed entries are the next steps.

## Repository layout

```
docs/idea.md             vision document
docs/requirements.md     refined, testable requirements
lemmatize/               one YAML entry per theorem
schema/entry.schema.json JSON Schema for entries
schema/proof-methods.yaml controlled vocabulary
pipeline/                CLI and validation code
examples/                worked examples
tests/                   pytest suite
```

## Quickstart

```sh
pip install -e .[dev]
lemmatize validate
lemmatize lookup    Nat.Prime.irrational_sqrt
lemmatize verbalize Nat.Prime.irrational_sqrt --register faithful_to_mathlib
pytest
```

See `examples/irrational-sqrt-two.md` for an end-to-end walk-through.

`lemmatize validate` is the gate every contribution must pass; it checks every YAML file in `lemmatize/` against the schema, verifies the `id` matches the filename, rejects unknown proof-method tags, and checks cross-references between entries.

## Contributing

Open a pull request against `main`. Add or edit a single YAML file under `lemmatize/` per PR where possible. CI runs `lemmatize validate` and the test suite.

## Licensing

- **Code** (everything under `pipeline/`, `tests/`, build files): Apache-2.0 — see `LICENSE`.
- **Data** (YAML files under `lemmatize/` and `schema/`): CC-BY-SA 4.0, for Wikidata compatibility. The data license file will be added with the first batch of curated entries beyond the seed.
