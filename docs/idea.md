# Lemmatize

*An ontology-driven natural-language layer for Lean's Mathlib.*

---

## Recommended name

**Lemmatize.**

In computational linguistics, *lemmatization* is the operation that reduces an inflected word to its canonical dictionary headword: *running* → *run*, *mice* → *mouse*, *better* → *good*. The headword itself is called the *lemma*.

That is exactly what this project does to Mathlib. A declaration like `Nat.Coprime.dvd_of_dvd_mul_right` is one specific inflected form. Its canonical headword — the form a mathematician would actually use in conversation or in a textbook — is *Euclid's lemma*. The project lemmatizes Lean: every formal identifier in Mathlib is mapped to the canonical mathematical name under which mathematicians group it, with the full dictionary entry (statement in prose, attribution, proof method, cross-references) attached.

The name has three properties that are unusually hard to combine:

- it is an NLP term, instantly meaningful to AI and ML engineers;
- it is a mathematical term, with *lemma* sitting visibly inside it;
- it is an active verb, naming what the project *does* rather than what it contains.

It also travels well across languages (German *lemmatisieren*, French *lemmatiser*) and has no significant collisions in the formal-methods software space.

Alternatives considered: *Lemmata* (quieter, more scholarly), *Pons* (the bridge metaphor hidden in *modus ponens*), *Lemma Atlas* (descriptive but flat).

---

## 1. The core idea

Mathlib4 contains over 210,000 formally verified theorems and 100,000 definitions. Every step of every proof is type-checked by Lean's kernel, but the proofs themselves read like code, not like mathematics. When a Mathlib proof internally calls `Nat.Coprime.dvd_of_dvd_mul_right`, a human reader sees an opaque identifier. A mathematician reading the same argument in a textbook would see *"by Euclid's lemma."*

**Lemmatize** is a curated, machine-readable knowledge layer that sits on top of Mathlib and supplies the semantic context Mathlib deliberately omits. For each notable theorem in Mathlib, Lemmatize records:

- the named-theorem identity (Wikidata Q-ID),
- the canonical name in several languages,
- a short "morally true" statement in prose,
- the proof method(s) the theorem employs (induction, contradiction, construction, …),
- pedagogical metadata distinguishing essential hypotheses from technical ones,
- and short stylistic hints for verbalization.

Lemmatize is not itself a verbalizer. It is the *infrastructure* that any verbalizer can use to turn a Lean proof into prose that reads like mathematics — *"by Euclid's lemma, p divides a or p divides b"* rather than *"applying `Nat.Coprime.dvd_of_dvd_mul_right` with hypothesis h."*

## 2. Lemmatize is not a collection of proofs

The most common misreading of this project is to treat it as a curated library of proofs with annotations. It is not. A collection of proofs *contains* mathematics; Lemmatize *describes* mathematics. The distinction is small in words but cashes out in three concrete ways.

### 2.1 Multiple proofs of the same theorem

A textbook contains one proof of any given theorem. Mathlib contains one. They are often genuinely different proofs, reaching the same conclusion through incompatible reasoning.

The irrationality of √2 is the canonical illustration. The textbook gives the classical "lowest-terms descent" argument: assume √2 = a/b in lowest terms, derive that both a and b are even, contradict coprimeness. Mathlib4 gives a completely different argument, routed through "primes are not perfect squares" (see `irrational_sqrt_two` in `Mathlib/NumberTheory/Real/Irrational.lean`, which reduces to `Nat.Prime.irrational_sqrt`, which in turn reduces to `irrational_sqrt_natCast_iff` plus the fact that a prime is not a perfect square). Same conclusion, fundamentally different reasoning.

No existing artifact catches this mismatch. A textbook contains only the descent proof and has no reason to mention Mathlib's route. Mathlib contains only its own proof and has no reason to mention the descent argument. A user asking an LLM to *"explain the Lean proof of √2's irrationality"* gets handed the textbook proof, because that is what dominates the training distribution — and the substitution goes unnoticed. Lemmatize is the layer that records both proofs, marks them as structurally distinct, and forces a verbalizer to disclose which it is rendering. **This catching-of-substitutions is the move that no existing artifact makes.**

### 2.2 Runtime constraint, not training data

A textbook is meant to be read by a human. Lemmatize is meant to be queried by a model under constraint.

A textbook's narrative cannot constrain an LLM's output at generation time. At best, the textbook joins the training distribution and influences the model statistically. A YAML entry with controlled vocabulary, canonical names, and explicit proof-method tags is a *runtime input* the model is conditioned on at inference. The shift is from "training corpus" to "schema enforced when the explanation is being produced." This is what closes the gap between fluent-but-unverifiable LLM prose and prose that names the right theorems for the right reasons.

### 2.3 Auditability

Every Lemmatize entry carries verification provenance — the URLs each fact was sourced from, the Mathlib commit it was verified against, the date of verification. When Mathlib evolves underneath, entries that no longer match self-flag rather than silently rot. A textbook does not do this. A documentation site does not do this. The Stacks Project comes closest in spirit but is itself the proof corpus, not an annotation layer over an external formal artifact.

### 2.4 The honest caveat

Roughly sixty percent of Lemmatize's value can fairly be described as "a more structured index" — controlled vocabulary, canonical names, Wikidata anchors. That part is useful but not new in principle; it is Wikidata for theorems. The forty percent that is genuinely new is the faithfulness discipline of §2.1 and the role as runtime constraint of §2.2. Those two pieces do not exist in any current collection of proofs.

A skeptic who compresses Lemmatize to "fancy index" has the sixty percent right and the forty percent missing. The forty percent is the part worth building.

## 3. Background and motivation

### 3.1 The classical tradition

The idea of producing natural-language proofs from formal ones has a long history in automated reasoning. **PROVERB** (Huang & Fiedler, Saarbrücken, mid-1990s) introduced the *assertion-level* representation: proofs reified at the level of "apply theorem X" or "apply definition Y" rather than natural-deduction inference. **P.rex** (Fiedler) added user modeling, adapting granularity to the reader's expertise. The **Ωmega** proof-planning system organized proof construction around named *methods* — effectively an ontology of proof techniques. **Theorema** (Buchberger, RISC Linz) produced textbook-style prose; **Naproche/SAD** uses controlled natural language for proof acts and is still actively maintained.

This tradition produced the most human-sounding output formal proofs have ever had. The reason it did not scale was that the underlying libraries (Mizar, Ωmega's own corpus) were comparatively tiny. Mathlib has changed that.

### 3.2 Current Lean infrastructure

Several pieces of the puzzle already exist in the Lean ecosystem:

- **Mathlib 100 / 1000+** (Freek Wiedijk, Pietro Monticone, Floris van Doorn): YAML files mapping Mathlib declaration names to Wikidata Q-IDs for famous named theorems. As of late 2024 the 1000+ project is described by its maintainers as "barely started" and waiting on infrastructure development.
- **EpiK Protocol's Mathlib knowledge graph**: parses doc-gen4 HTML output into a Neo4j graph with theorem nodes and relationships (`HAS_ATTRIBUTE`, `HAS_DESCRIPTION`, `EXTENDS_TO`).
- **Herald** (arXiv 2410.10878, ICLR 2025): Lean 4 informalization pipeline using Lean-jixia static analysis plus an LLM, fine-tuned on a synthetically generated NL-FL aligned corpus.
- **Hattori, Matsuzaki, Fujiwara** (arXiv 2509.09726, September 2025): recursive summarization of formal proofs. The authors explicitly note that hand-built per-tactic templates are the bottleneck — i.e. a small manual proof-method ontology is what made their approach work.
- **LeanDojo, LeanExplore, Lean Finder**: tooling for extracting proof structure, dependencies, and semantic search over Mathlib.
- **Formal Abstracts** (Thomas Hales): Lean-based formal statements of published research results with concept-level metadata. The closest existing project in spirit to Lemmatize, though aimed at *abstracting research papers into Lean* rather than verbalizing Lean back into prose.

### 3.3 The gap

Existing informalization work treats the verbalization problem end-to-end: feed an LLM the Lean proof plus some context (docstrings, dependent theorems), generate prose. The output is fluent but the LLM has no principled way to know that `Nat.Coprime.dvd_of_dvd_mul_right` should be called "Euclid's lemma," and no principled way to choose between "we apply induction" and "the result follows by strong induction on n." These choices emerge from training distribution, not from a curated source of truth.

Lemmatize fills the gap. It is the source of truth that any informalizer can be conditioned on.

## 4. Embedding in the SAIR vision

The Foundation for Science and AI Research (SAIR), co-founded by Terence Tao alongside Nobel, Turing, and Fields laureates, articulates its mission around two pillars — *AI for Science* and *Science for AI* — summarized as *"Grounding intelligence. Scaling discovery."*

Lemmatize sits squarely on this axis.

**Grounding intelligence.** AI explanations today are LLM-generated chains of natural-language reasoning: persuasive but unverifiable, and known to be unfaithful to the underlying computation. A Lemmatize-augmented informalizer produces explanations whose claims are *type-checked by Lean's kernel*. The prose is a faithful surface form of a machine-verified argument. This converts AI "explanation" from a rhetorical artifact into an auditable one. It is the cleanest demonstration of grounding currently available in any domain.

**Scaling discovery.** Lemmatize makes Mathlib navigable for mathematicians who don't (yet) read Lean. Every theorem becomes discoverable by its mathematical name; every proof becomes readable at the level of detail the reader chooses. This compounds with the rising tide of AI-assisted formalization: as more mathematics enters Mathlib, Lemmatize turns it into a living, browsable reference work — Wikipedia for verified mathematics.

It is also a clean instance of *Science for AI*: Lemmatize is itself a piece of scientific infrastructure, governed transparently, built with the rigor of a mathematical library, designed to make AI systems demonstrably more trustworthy in a high-stakes domain.

Lemmatize is not a universal solution to AI explainability. It applies where mathematics applies. Within that scope, it is the clearest existing path from *"trust me, the model says so"* to *"here is the verified argument and a faithful translation of it."*

## 5. POC scope and design

### 5.1 Slice: number theory's greatest hits

The POC covers approximately twenty named theorems from elementary and analytic number theory. The slice is chosen because:

- The proofs are short (typically under fifty lines of Lean).
- Most are already formalized in Mathlib4 and appear in the Mathlib 100 / 1000+ YAML files.
- The proofs reference each other densely — Euclid's lemma feeds the Fundamental Theorem of Arithmetic, which feeds the irrationality of √2 and the infinitude of primes — which is precisely the property that makes ontology-aware verbalization visibly outperform a baseline.
- The named theorems are recognizable to any mathematician, so the side-by-side comparisons are immediately legible to a non-specialist audience.

Initial target list (subject to confirmation that each has a clean Mathlib4 proof):

1. Irrationality of √2 — *seed entry already produced; see `irrational-sqrt-two.yaml`*
2. Infinitude of primes (Euclid)
3. Euclid's lemma
4. Fundamental theorem of arithmetic
5. Fermat's little theorem
6. Wilson's theorem
7. Bezout's identity
8. Chinese remainder theorem
9. Euler's product formula
10. Divergence of the sum of reciprocals of primes
11. Bertrand's postulate
12. Fermat's theorem on sums of two squares
13. Quadratic reciprocity (if a clean form is available)
14. Lagrange's four-square theorem (if available)
15. Liouville's theorem on Diophantine approximation
16. Hensel's lemma
17. Lifting-the-exponent lemma
18. Countability of ℚ
19. Pell's equation (existence of nontrivial solutions)
20. Erdős's proof of Bertrand (if a separate Mathlib entry exists)

Reduce to fifteen if some are not yet formalized.

### 5.2 Schema (per-theorem YAML)

The schema is concretely fixed by the seed entry `irrational-sqrt-two.yaml`, produced under the same conventions as this document. Key fields, with the rationale from §2 motivating each:

- **`mathlib_declaration`, `mathlib_file`, `mathlib_lines`, `mathlib_commit_verified_against`** — bind the entry to a specific verified Lean source.
- **`mathlib_statement`, `mathlib_proof_body`** — the actual Lean code, reproduced verbatim, so the entry can be diffed against Mathlib if the source changes.
- **`canonical_name`** (multilingual) and **`short_form`** — the headword the verbalizer should use in prose.
- **`dependencies`** — the named theorems the proof directly invokes, each with a one-line gloss.
- **`proof_chain`** — the reasoning Lean actually uses, one level deeper than the immediate call.
- **`proof_method_lean`** vs. **`proof_method_textbook`** — the §2.1 distinction: how Lean proves it vs. how a textbook proves it. The verbalizer must disclose which it renders.
- **`verbalization`** — three rendered templates (`researcher`, `faithful_to_mathlib`, `textbook_classical`) the verbalizer can select from.
- **`verification`** — the audit trail: for every claim, which URL it was checked against.

The full first entry, for irrationality of √2, is in the companion file. It is the reference implementation of the schema and should be copied as the template for entries 2–20.

### 5.3 Pipeline

```
[Lean proof source]
       │
       ▼
LeanDojo / lean-jixia
       │  (extract called declarations, tactic structure,
       │   term-level proof DAG)
       ▼
[Structured proof representation]
       │
       ▼
Lemmatize lookup
       │  (resolve each called declaration → ontology entry,
       │   where available; otherwise pass through unchanged)
       ▼
[Enriched proof representation]
       │
       ▼
LLM verbalizer  (Claude / GPT / Gemini)
       │  prompted with:
       │    - the enriched proof representation
       │    - constraint: prefer canonical names over Mathlib identifiers
       │    - audience parameter (researcher / grad / undergrad)
       │    - faithfulness parameter (strict / relaxed)
       │    - target language
       ▼
[Natural-language proof]
       │
       ▼
Faithfulness check
       │  (parse output, verify each cited theorem actually appears
       │   in the proof DAG; flag hallucinated references)
       ▼
[Verified verbalization]
```

Implementation size estimate: 200–400 lines of Python plus prompt engineering. The LLM does the heavy lifting; Lemmatize constrains it; the faithfulness check is what makes the result auditable.

### 5.4 Deliverable

The POC ships as a public GitHub repository containing:

1. **`lemmatize/`** — YAML files for ~20 theorems.
2. **`pipeline/`** — pipeline code (extraction, lookup, verbalization, faithfulness check).
3. **`examples/`** — five to eight case studies, each containing:
   - the original Lean proof,
   - the structured representation extracted by the pipeline,
   - a *baseline* verbalization (LLM without Lemmatize),
   - the *Lemmatize-augmented* verbalization,
   - the textbook version, cited, for comparison,
   - a brief discussion of where Lemmatize helps and where it does not.
4. **`writeup.md`** — a 1,500–2,500 word write-up suitable for the Lean community blog or as a short arXiv note.
5. Optional: a 90-second screen recording showing the pipeline running end-to-end.

The killer artifact is the side-by-side comparison table. Specifically: examples where the baseline produces *"by `Nat.Coprime.dvd_of_dvd_mul_right`"* and the Lemmatize-augmented version produces *"by Euclid's lemma."* That contrast is the elevator pitch.

### 5.5 Effort and timeline

| Phase   | Work                                                                                       |
| ------- | ------------------------------------------------------------------------------------------ |
| Week 1  | Environment setup; finalize the 20 theorems; refine schema based on the seed entry.        |
| Week 2  | YAML entries 2–8 (carry forward conventions from the seed entry).                          |
| Week 3  | Implement LeanDojo extraction and Lemmatize lookup.                                        |
| Week 4  | Implement LLM verbalizer + faithfulness check; first end-to-end run on one proof.          |
| Week 5  | Complete YAML for all ~20 theorems; iterate verbalizer prompts on 3 examples.              |
| Week 6  | Produce all 5–8 worked examples; write the write-up; polish the repository.                |

Realistic for one focused person at 8–12 hours per week. Less if existing tooling is leveraged aggressively.

## 6. Beyond the POC

The POC is a stepping stone. The natural sequence after it lands:

- **Phase 2 (12–18 months): WhyProver.** A web service plus VS Code extension that verbalizes any Lean proof on demand, at the user's chosen resolution and language, using Lemmatize. By-product: a large aligned corpus of (Lean proof, NL explanation, named-theorem references) tuples for training next-generation math LLMs.
- **Phase 3 (2–3 years): Verified Foundations of ML.** Apply the methodology to the foundational theorems of machine learning (PAC bounds, VC dimension, NTK convergence, scaling laws where provable). A direct contribution to SAIR's "Science for AI" pillar.
- **Phase 4 (10 years): The Living Mathematical Knowledge Graph.** Every theorem in the published literature linked to a formalization, every formalization carrying a verified multi-resolution explanation, navigable by humans and AI alike.

## 7. Governance, licensing, collaboration

Lemmatize must be open from day one.

- **Licensing.** Apache 2.0 for code; CC-BY-SA 4.0 for the YAML data (compatible with Wikidata).
- **Hosting.** GitHub initially, with the explicit goal of eventual integration with the Mathlib4 repository or as an official Lean community repository.
- **Governance.** Benevolent dictator initially. After roughly fifty theorems are in, transition to a small steering group along Mathlib's maintainer model. Floris van Doorn (1000+ maintainer) and Pietro Monticone are the obvious early collaborators to approach.
- **Contribution model.** Pull requests against YAML files, with light review for accuracy and style consistency. Same model as Mathlib's `100.yaml`.

## 8. First concrete step

The next ninety minutes of work:

1. Check GitHub for `lemmatize` repo-name availability. If taken at the user level, fall back to `lemmatize-lean` or claim a fresh organization name.
2. Create the public repository.
3. Add a `README.md` containing a condensed version of this document.
4. Drop in the existing seed entry `irrational-sqrt-two.yaml`.
5. Post a short note on the Lean Zulip's `#general` stream: project name, link to the repo, brief explanation of the goal, ask for feedback. Tag Floris van Doorn and Pietro Monticone.

That is enough to start. Everything else follows.

---

## Open questions to resolve early

- **Tactic granularity.** Should Lemmatize record entries only for "famous" theorems (the 1000+ list) or also for important *intermediate* lemmas like `Nat.gcd_dvd_left`? Recommendation: start with the 1000+ subset; expand carefully only when a clear pedagogical need emerges.
- **Proof-method vocabulary stability.** The tag set will evolve. Recommendation: version the vocabulary explicitly and treat each version as a release.
- **Faithfulness metric.** What does it mean for a verbalization to be "faithful" to a Lean proof? Recommendation: start with the weak form (every named theorem cited in prose appears in the proof DAG) and develop stronger forms only when the weak form is solid.
- **Multilingual scope at MVP.** Start English-only, add German once the English version is stable; defer French until after MVP.
- **Wikidata Q-ID resolution.** Q-IDs for individual theorems are not always cleanly assigned in Wikidata. Recommendation: where the theorem has its own Wikipedia article, use that Q-ID; where it does not, leave `wikidata: TBD` rather than guess. The seed entry follows this rule.
- **Relationship to Hales' Formal Abstracts.** Coordinate explicitly to avoid duplicating effort. Lemmatize focuses on verbalization metadata for *existing* Mathlib formalizations; Formal Abstracts focuses on formalizing *new* research results. They are complementary.
- **Name collision with NLP libraries.** The verb *lemmatize* is in common use in NLTK, spaCy, and other NLP libraries as a function name. This is a feature, not a bug — the target audience straddles NLP and formal methods — but the README should state in its first paragraph that the project refers to mathematical lemmas, not word lemmas.

---

*Document version: 0.3 (added §2 distinguishing Lemmatize from a curated collection of proofs; seed YAML entry now exists; verification discipline applied throughout). Maintainer: TBD.*
