# Exact spectral-range membership — mathematical design

The generic predicate design decides `lambda_max(A) − lambda_min(A) <= Y` exactly for the mathematical symmetric tensor encoded by six finite binary64 Mandel components and a finite nonnegative binary64 width. Equality is included. It uses rational/radical arithmetic rather than rounded eigenvalues, a yield tolerance or projection of supplied state. This packet is source-only: the Atlas interpreter, DSL, native and Wasm runtimes are unchanged.

The design addresses the strict-membership failure retained in [the Tresca backend study](../../../catalogue/investigations/tresca-rounded-backends-v1/README.md). It rejects rounded history parent 7 at both frozen reference precisions, while matching all 61 original case parents and all 12 history parents. It introduces no Tresca-specific mathematical branch. The constitutive source remains [BK2022v1](https://arxiv.org/abs/2207.12719v1), linked and crosswalked in [the source packet](../../ingestion/tresca/README.md); the generic numerical predicate and proof here are project-derived.

## Proof

Let `S = 3A − tr(A)I`, `W = 3Y`, `J2 = tr(S²)/2` and `J3 = det(S)`. Subtracting pressure preserves all eigenvalue gaps and multiplying by three scales them by three, so the required decision is whether the largest squared gap of S is at most `q=W²`.

For ordered eigenvalues of S, write the adjacent gaps as `a>=0`, `b>=0`. The trace-free eigenvalues are `−(2a+b)/3`, `(a−b)/3`, `(a+2b)/3`. Substitution gives `3J2 = a²+ab+b²`; multiplying the three gap factors gives

```
h(q) = (q−a²)(q−b²)(q−(a+b)²)
     = q³ − 6J2 q² + 9J2² q − 4J2³ + 27J3².
```

The largest squared gap `L=(a+b)²` obeys `L−3J2=ab>=0` and `4J2−L=(a−b)²/3>=0`. Thus `3J2<=L<=4J2`. Also `h'(q)=3(q−J2)(q−3J2)`, so h is strictly increasing above `3J2` when J2>0. On `[3J2,4J2]` it has its final zero at L; the endpoint equality at `3J2` occurs for a repeated spectrum and is included. This proves the following decision, including all repeated-root cases:

1. If `q<3J2`, return false.
2. If `q>=4J2`, return true.
3. Otherwise return `h(q)>=0` using an exact sign.

For hydrostatic S, J2=0 and step 2 returns true even at Y=0. For nonhydrostatic S and Y=0, step 1 returns false. No division by an eigenvalue gap occurs.

## Exact Mandel arithmetic

For scaled Mandel components `(d0,d1,d2,u,v,w)`, the physical off-diagonal components are `(u,v,w)/sqrt(2)`. Consequently

```
J2 = (d0²+d1²+d2²+u²+v²+w²)/2
J3 = d0*d1*d2 − (d0*v²+d1*w²+d2*u²)/2 + (u*v*w/2)*sqrt(2).
```

All inputs are exact dyadics; J2 is dyadic and J3 is in Q(sqrt(2)). Squaring J3 preserves this field. The sign of `c+d*sqrt(2)` follows signs of c,d when equal, and exact comparison of `c²` with `2d²` when opposite; the sign of c fixes the comparison orientation. No floating square root, decimal tolerance, overflow-prone binary64 invariant or approximate spectral gap enters the decision. Signed zero represents exact zero.

[exact.py](exact.py) is a separate Fraction-based design prototype, with a general exact ordered-field Sturm root counter as its independent decision oracle. The oracle counts roots strictly above q using signed polynomial remainders; at a root it uses right-hand Taylor signs, preserving equality and repeated-root behavior. Both methods share the derived gap-polynomial coefficients; the coefficient identity is independently checked against products of known exact diagonal gaps. These checks support the analytic proof; they do not replace it.

## Evidence and limits

The policy, literal inputs, code and source hashes were frozen in [pre-check-freeze.json](pre-check-freeze.json) before running either decision. [checks.json](checks.json) records:

- 676 exact polynomial identities and 506 diagonal equality/neighbor decisions, including repeated spectra and hydrostatic zero.
- 230 frozen literal cases agreeing exactly with the independent Sturm count, including 160 deterministic dense tensors, subnormals, mixed scales, near-maximum finite values and a nonzero radical determinant term.
- 146 parent comparisons against both original high-precision datasets; history parent 7 is outside at both precisions. No original references were regenerated or changed.
- 14 explicit invalid-input rejections across the two methods; 36 focused design/Tresca/activation/archive tests pass. No candidate material evaluation, compiled call, build or scientific admission.

Run `python3 -B docs/reviews/certified-spectral-range-v1/check.py` and `python3 -B -m unittest tests.test_certified_spectral_range_design` from the repository root. Full process receipts are retained. [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) defines the next implementation boundary and unresolved expression-range issues.
