# Certified centered-middle comparison — source-only design

The exact generic predicate design is complete: `3*lambda_middle(A)-trace(A)>w` for a finite binary64 symmetric Mandel tensor and finite nonnegative width of matching dimensions. Strict equality is false. Negation supplies the lower comparison. No runtime, solver, schema, model or public website changes are included.

The [proof](PROOF.md) reduces the decision to exact signs of the pair sum and determinant of `B=3A-(trace(A)+w)I`, whose trace is nonpositive. In terms of the exact centered invariants J and D, the test is `J>3*w*w` and `D+J*w-w*w*w<0`. No rounded eigenvalue, tolerance, division by spectral gap or binary64 intermediate invariant is used. The [runtime contract](RUNTIME_CONTRACT.md) defines typing, finite seed checks, failure semantics and the subsequent qualification boundary.

An independent oracle constructs the Cartesian Q(sqrt(2)) matrix and characteristic polynomial directly by matrix permutations, then counts strictly positive roots by Sturm remainders with gcd recursion for multiplicities. It shares ordered-field arithmetic with the invariant route, while avoiding its characteristic coefficients and determinant-sign classification. Repeated positive roots must count twice; zero roots are excluded.

`pre-check-freeze.json` binds the literal inputs, two methods, checker, policy and source receipts before either design predicate was evaluated. The retained process and `checks.json` report exact agreement on all 1,160 literal cases, including all 61 original Tresca rounded trial tensors, 220 nonzero three-shear products, repeated spectra, equality neighbors, inherited dense/extreme inputs and rounded rotations. There are 773 independently known expected outcomes, 48 exact metamorphic checks, seven multiplicity checks, 30 exact rational-rotation checks, 30 direct coefficient identities and 78 invalid-input rejections. The two direct reversal tensors select upper=false and lower-via-negation=true, avoiding the prior face misclassification.

Inputs comprise 750 diagonal cases, 230 inherited literals, 61 original trial tensors, 60 exact metamorphic cases, 32 rounded rotations, 21 equality neighbors, four additional extreme cases and the reversal with its negation. Rounded rotations are checked as the actual stored tensors; they are not asserted to preserve an ideal spectrum. Original trial construction is explicit in the frozen literal values; no material kernel or reference dataset was rerun or modified.

Reopen the exact source-only evidence:

```sh
python3 -B docs/reviews/certified-centered-middle-v1/verify.py
python3 -B -m unittest tests.test_certified_centered_middle_design -q
```

All 21 related software tests pass, with process execution denied during the saved design replay. There were zero native/Wasm builds or material calls in this task. The proof/oracle does not qualify a future implementation, repair the current Tresca candidate, validate experiments or confer scientific admission.

Next: implement just this generic Boolean through the normal DSL/interpreter/generated C++ pipelines, with preserved pinned-source archives and separate frozen native/Wasm/seed/failure gates. Then a distinct private Tresca candidate must pass the entire original one-step/38-column, continuous-history and laboratory corpora without altering their policies. Earlier failure reports remain unchanged. No push or deployment is included.
