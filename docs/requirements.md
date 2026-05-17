# Lemmatize — Requirements (v0.1)

Refined from `docs/idea.md` (v0.3). This document captures the requirements for the proof-of-concept (POC) as testable statements. The vision and motivation live in `idea.md`; this file is the contract the implementation must satisfy.

The project name refers to mathematical **lemmas**, not the NLP operation on words. The collision with NLTK/spaCy is intentional (the target audience straddles both fields) and is disclosed in the README.

---

## R1. Scope of the POC

R1.1 The POC covers a curated slice of approximately twenty named theorems from elementary and analytic number theory, chosen from the list in `idea.md` §5.1.

R1.2 A theorem qualifies for inclusion only if it has a Mathlib4 formalization that can be cited by declaration name. Theorems that are not yet in Mathlib are deferred.

R1.3 The slice may be reduced to fifteen theorems if formalizations are not available; it may not exceed twenty-five.

R1.4 English is the only required language for the POC. German is a stretch goal. French is out of scope until after MVP.

---

## R2. Per-theorem entry (data model)

Each theorem is represented by one YAML file in `lemmatize/`, named in `kebab-case` (e.g. `irrational-sqrt-two.yaml`). Each file MUST be a single YAML document validated against `schema/entry.schema.json`.

### R2.1 Required fields

| Field | Type | Purpose |
| --- | --- | --- |
| `id` | string | Stable kebab-case identifier; matches filename without `.yaml`. |
| `wikidata` | string or `TBD` | Wikidata Q-ID for the theorem; `TBD` when no clean Q-ID exists. |
| `canonical_name` | map `lang → string` | Headword the verbalizer should emit. MUST contain `en`. |
| `short_form` | map `lang → string` | Short attribution form, e.g. `"by Euclid's lemma"`. MUST contain `en`. |
| `mathlib_declaration` | string | Fully-qualified Lean 4 identifier. |
| `mathlib_file` | string | Path inside the Mathlib4 repo, e.g. `Mathlib/NumberTheory/Irrational.lean`. |
| `mathlib_lines` | string | Line range as `"L1-L2"`. |
| `mathlib_commit_verified_against` | string | 40-char Mathlib4 commit SHA, or `TBD` (with a verification task open). |
| `mathlib_statement` | string (literal block) | Verbatim Lean statement, no transformations. |
| `mathlib_proof_body` | string (literal block) | Verbatim Lean proof term/tactic block. |
| `proof_method_lean` | array of strings | Controlled-vocab tags from `schema/proof-methods.yaml`. |
| `proof_method_textbook` | array of strings | Same vocabulary; the *textbook* method, which may differ. |
| `dependencies` | array of objects | Theorems this proof directly invokes; see §R2.3. |
| `verbalization` | object | Three rendered templates; see §R2.4. |
| `verification` | array of objects | Audit trail; see §R2.5. |

### R2.2 Optional fields

| Field | Type | Purpose |
| --- | --- | --- |
| `aliases` | array of strings | Other names the theorem is known by. |
| `proof_chain` | array of strings | Reasoning one level deeper than `dependencies`, in chronological proof order. |
| `essential_hypotheses` | array of strings | Hypotheses without which the theorem is false. |
| `technical_hypotheses` | array of strings | Hypotheses that exist for the sake of the formalization, not the mathematics. |
| `notes` | string | Free-form maintainer commentary. |

### R2.3 Dependency entries

Each item of `dependencies` is an object with:

- `declaration` (string, required) — the called Mathlib identifier;
- `canonical_name` (string, required) — the headword for that dependency;
- `gloss` (string, required) — one-line description of what the dependency contributes here;
- `lemmatize_id` (string, optional) — if the dependency itself has an entry in this repo, its `id`.

### R2.4 Verbalizations

`verbalization` is an object with three required keys, each a string:

- `researcher` — terse, names theorems, assumes graduate-level fluency.
- `faithful_to_mathlib` — discloses Mathlib's actual proof route, even when it differs from the textbook treatment (this is the §2.1 discipline).
- `textbook_classical` — the proof a textbook would give, regardless of how Mathlib proves it. Where this differs from `faithful_to_mathlib`, the entry MUST set `proof_method_lean ≠ proof_method_textbook`.

### R2.5 Verification entries

Each item of `verification` is an object with:

- `claim` (string, required) — the asserted fact;
- `source` (string, required) — URL, Mathlib file path, or `local-lean-check`;
- `checked_on` (ISO date string, required) — `YYYY-MM-DD`;
- `checker` (string, optional) — identifier of the human or tool that verified.

An entry whose `mathlib_commit_verified_against` is `TBD` MAY still ship, but it MUST carry a `verification` item whose `claim` is `"pending Mathlib commit pin"` so it is discoverable.

---

## R3. Controlled vocabularies

R3.1 Proof methods are drawn from `schema/proof-methods.yaml`. Adding a tag is a versioned change to the vocabulary file. The vocabulary file carries a `version` field; entries do not pin a version (they always validate against the latest).

R3.2 The initial vocabulary is small and additive. The starter tags are: `direct`, `contradiction`, `contrapositive`, `induction`, `strong-induction`, `well-founded-recursion`, `case-analysis`, `construction`, `existence-by-counting`, `pigeonhole`, `descent`, `unique-factorization`, `algebraic-manipulation`, `analytic`, `combinatorial`, `topological`.

R3.3 Unknown tags MUST cause schema validation to fail.

---

## R4. Pipeline

The pipeline is a thin layer; the LLM does the linguistic work. The four stages are:

1. **Extract** — given a Mathlib declaration, obtain its called declarations and tactic structure. The POC may stub this stage by relying on hand-authored `dependencies` in the YAML while the LeanDojo / lean-jixia bridge is being built.
2. **Lookup** — for each called declaration, return its Lemmatize entry if present, else `None`.
3. **Verbalize** — prompt an LLM with the enriched representation. Out of scope for the very first cut; the contract is defined but the implementation is deferred to the second iteration.
4. **Faithfulness check** — given a generated verbalization and the proof DAG, every Mathlib declaration named in prose MUST appear in the DAG. Hallucinated names are an error.

R4.1 Each stage is invokable from a CLI: `lemmatize validate`, `lemmatize lookup <decl>`, `lemmatize verbalize <decl>`, `lemmatize check <decl> <prose-file>`.

R4.2 `lemmatize validate` MUST pass before any other command will run against the data set.

R4.3 The faithfulness check is *weak*: it requires every cited theorem to appear in the proof DAG. It does not yet require that every step of the prose corresponds to a step of the proof. Strengthening is future work.

---

## R5. Repository layout

```
docs/
  idea.md                  # vision (input)
  requirements.md          # this file
lemmatize/                 # YAML entries, one per theorem
  irrational-sqrt-two.yaml
  ...
schema/
  entry.schema.json        # JSON Schema for entries
  proof-methods.yaml       # controlled vocabulary
pipeline/
  __init__.py
  cli.py                   # `lemmatize` entry point
  validate.py              # schema + cross-reference validation
  lookup.py                # declaration → entry resolution
  faithfulness.py          # weak faithfulness check
examples/                  # populated in second iteration
tests/
  test_validate.py
pyproject.toml
README.md
```

---

## R6. Licensing and governance

R6.1 Code is Apache-2.0. Data (YAML entries) is CC-BY-SA 4.0 to remain Wikidata-compatible. A `LICENSE-DATA` file MUST be present once the first entry lands. (The existing `LICENSE` file covers code.)

R6.2 Contributions are accepted as pull requests editing or adding YAML files. Each PR MUST cause `lemmatize validate` to pass in CI.

R6.3 The maintainer is the project lead until ~fifty theorems are landed; thereafter governance transitions to a steering group along the Mathlib model.

---

## R7. Acceptance criteria for the first implementation cut

The first cut is complete when:

- A1. `schema/entry.schema.json` exists and rejects entries missing any required field.
- A2. `schema/proof-methods.yaml` exists with the R3.2 starter vocabulary.
- A3. `lemmatize/irrational-sqrt-two.yaml` exists, validates, and exercises every required field including all three verbalization renderings.
- A4. `pipeline/validate.py` validates every YAML file in `lemmatize/` against the schema and checks that:
  - each file's `id` matches its filename,
  - every `proof_method_*` tag is in the vocabulary,
  - every `dependencies[*].lemmatize_id` (if set) resolves to another entry in the repo.
- A5. A `lemmatize` CLI invokes `validate` and `lookup`. The other subcommands may print a "not yet implemented" message.
- A6. `tests/test_validate.py` covers: a valid entry passes; a missing required field fails; an unknown proof-method tag fails.
- A7. README states the NLP-name caveat in its first paragraph.

The second cut (out of scope for this commit) adds the LeanDojo bridge, the verbalizer prompt, and worked examples.
