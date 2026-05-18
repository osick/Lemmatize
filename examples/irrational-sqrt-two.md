# Worked example: irrationality of √2

This is the first end-to-end illustration of what Lemmatize does. The target is the Mathlib4 declaration `Nat.Prime.irrational_sqrt`, specialized to p = 2.

The example is reproducible from the repository state:

```sh
lemmatize lookup    Nat.Prime.irrational_sqrt
lemmatize verbalize Nat.Prime.irrational_sqrt --register researcher
lemmatize verbalize Nat.Prime.irrational_sqrt --register faithful_to_mathlib
lemmatize verbalize Nat.Prime.irrational_sqrt --register textbook_classical
lemmatize check     Nat.Prime.irrational_sqrt examples/sample-prose.txt
```

## The Lean side

Mathlib formalizes the result as a statement about *every* prime, not specifically about 2:

```lean
theorem Nat.Prime.irrational_sqrt {p : ℕ} (hp : p.Prime) : Irrational (Real.sqrt p)
```

The proof route, as recorded in `lemmatize/irrational-sqrt-two.yaml`, is

1. apply the criterion that for positive n, `√n` is irrational iff n is not a perfect square;
2. discharge the criterion's hypothesis by `Nat.Prime.not_isSquare`;
3. conclude.

The criterion plus the primality fact do all the work. There is **no descent**, no manipulation of "a/b in lowest terms", and no extraction of a parity contradiction.

## The three renderings

### Baseline (Mathlib identifiers, no ontology)

> Applying `Nat.Prime.irrational_sqrt` with the instance `Nat.prime_two`, we
> obtain `Irrational (Real.sqrt 2)`, which is the desired conclusion. The
> underlying proof uses `irrational_sqrt_natCast_iff_of_pos` and
> `Nat.Prime.not_isSquare`.

Fluent, technically correct, and entirely unreadable to a mathematician who does not already know Mathlib. This is what a generic LLM, given the Lean source, tends to produce.

### Lemmatize-augmented, `faithful_to_mathlib` register

> Mathlib does not give the classical "lowest-terms descent" argument here.
> It proves the general statement that √p is irrational for every prime p, by
> reducing to a perfect-square criterion: a positive natural number n has
> irrational square root if and only if n is not a perfect square. Primality
> rules out being a square (a prime equal to k² would force k = 1, contradiction),
> so √p is irrational, and √2 follows as the case p = 2.

This is the rendering a verbalizer should emit when the user has asked for an explanation of what Lean actually verifies. The disclosure in the first sentence is the §2.1 discipline of `docs/idea.md`: it tells the reader that the textbook proof and the Lean proof are not the same proof.

### `textbook_classical` register

> Suppose √2 = a / b with a, b coprime integers and b ≠ 0. Squaring gives
> 2b² = a², so a² is even and hence a is even; write a = 2a'. Substituting,
> b² = 2a'², so b is also even, contradicting coprimeness. Therefore √2 is
> irrational. (Note: this *descent* argument is not the one Mathlib uses;
> Mathlib routes the proof through a perfect-square criterion. See the
> `faithful_to_mathlib` rendering for what Lean actually verifies.)

This is the *textbook* proof. It is correct mathematics, but it is not what the Lean kernel has type-checked. The closing parenthetical is the part Lemmatize forces a verbalizer to include: a textbook rendering must disclose that it differs from the formal proof.

## What Lemmatize bought us

- **Substitution of identifiers.** `Nat.Prime.irrational_sqrt` becomes "the irrationality of √p for primes p" in the researcher rendering, "the result that √p is irrational" in the faithful rendering, and disappears entirely (replaced by "√2 is irrational") in the textbook rendering.
- **Forced disclosure.** A verbalizer with no ontology renders the textbook proof of √2, because that is what dominates the training distribution. Lemmatize makes the distinction between the textbook proof and the Mathlib proof a *first-class field* of the entry; the verbalizer has nowhere to hide.
- **Auditability.** The `verification` block of the entry records the URLs each claim was checked against and the date. When Mathlib evolves, an entry whose `mathlib_commit_verified_against` falls out of date is flagged mechanically.

The forty-percent claim in §2.4 of `idea.md` is exactly the second and third bullets. The first bullet alone is the sixty-percent "fancy index" claim; the value comes from combining all three.
