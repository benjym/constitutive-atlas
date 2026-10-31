# Independent rounded-input Tresca references

This packet advances the unchanged BK2022v1 associated perfect-plastic law with the separately project-derived BE update toward numerical qualification. It supplies independent references, not an executable model addition, numerical backend pass, scientific admission or Wichtmann applicability claim. It imports no Atlas DSL/interpreter/compiler, author implementation or compiled artifact.

## Method and frozen inputs

`reference-policy.json` and `pre-generation-freeze.json` precede reference generation. The literal corpus has 61 cases and 38 seed columns: the 30 independent current12/parent12/loading6 component directions and eight deterministic mixtures. It includes elastic, face, upper/lower corner, repeated trial pairs, all six coordinate permutations of six strict/repeated cases, stored dense rational-rotation encodings, exact yield/face-corner equalities and adjacent binary64 inputs, hydrostatic compression/tension/zero, scales2^±80, large offsets and selected-isolation conditioning. The analytical parameter examples are not fitted soil constants.

The reference treats each stored binary64 input as its exact integer ratio, performs the elastic trial at declared high precision and converts Mandel shear using mathematical sqrt(2). It does not replace rounded rotations with their intended ideal eigenframes. The copied characteristic-cubic helper is byte-identical to its independent spectral-reference ancestry. A separate six-oriented-plane active-set enumerator computes the convex principal projection, checking nonnegative multipliers, all yield inequalities, stationarity, trace preservation, spectral identities and the full inverse-elastic plastic increment. It does not evaluate the candidate's branch DSL. Principal active-set Jacobians and spectral divided differences give full Cartesian derivatives, with safe repeated-coordinate limits. This is high-precision convergence and certificate evidence, not rigorous interval root certification.

Current residuals and returned state are distinct: the plastic-strain residual depends on the supplied current stress, while the update uses the independently returned stress. All12components, including nonzero initial plastic history, are retained. A boundary derivative is explicitly a selected active-set extension; it is not asserted to be a unique classical tangent. Six one-sided witnesses establish the source branch changes at yield and both face/corner boundaries.

## Results

- Both 200/280-digit datasets pass the frozen1e-55 comparison over 58,713 numeric fields. Maximum normalized difference3.34e-166. All spectral/KKT certificate errors pass1e-100 at both precisions.
- Source branch counts: 13 elastic, 16 face, 17 upper, 15 lower. Exact Fraction reconstructions also reproduce all 12previously frozen source-ideal certificates.
- 4,608 centered derivative component checks at320 digits and two steps1e-35/1e-45 pass1e-30; maximum normalized error9.05e-70. 11,712 mixed-column linearity checks pass1e-55, maximum2.35e-72. These checks cover strict/repeated/dense cases and selected directions; they are not a claim that every possible perturbation is classically differentiable.
- Twelve ordered loading/unloading/shear/hold/reversal steps retain full sigma6/ep6. Each next parent is the actual binary64-rounded preceding reference update, not an ideal unrounded substitute.
- Deterministic regeneration reproduces the entire200-digit compressed dataset byte-for-byte. Corrupted values, jointly corrupted mixed derivatives and jointly corrupted history linkage reject.

## Rounded-history finding and backend limits

At history step 7, the rounded incoming stress exceeds the exact source yield range by approximately 2.10e-17 Pa. It is recorded as source-invalid. The principal projection extension remains mathematically computable there, but its result does not turn that supplied initial state into an admissible source start. No clipping, silent initial projection or yield-tolerance relaxation was introduced. This sequence therefore does not establish 12 accepted source-admissible backend restarts. The next study must preserve the distinction, including the exact parent and discrepancy as a negative gate.

`backend-negative-input-freeze.json`, written before any candidate observations, supplies 22 literal missing-state, outside-yield, invalid-parameter, nonfinite and finite-input-overflow cases, plus poisoned seed37, near-isolation diagnostics and same-instance recovery requirements. Malformed requests must reject before integration; valid 12 component baselines must remain unchanged. No rejection or rollback was executed by this source-only task. Exact native/Wasm drivers, numerical budgets, branch adjacency, accepted-history partitioning and call counts still need a prospective backend freeze. Neither rejected conditioning cases nor rounded invalid parents may silently count as full-domain coverage.

One ancestry harness initially compared independently rounded Decimal thirds using exact equality and failed at the last working digit. The retained failure summary records the correction: exact Fraction active-set reconstruction, with Decimal values checked against the already frozen1e-100 certificate budget. The original datasets, frozen generator/checker and acceptance gates were not replaced or relaxed.

## Reproduce

Use a fresh output path; the generator refuses to overwrite evidence.

```sh
python3 -B docs/reviews/tresca-rounded-reference-v1/generate.py --precision 200 --output /private/tmp/tresca-reference-replay.json.gz
python3 -B docs/reviews/tresca-rounded-reference-v1/check.py
python3 -B -m unittest tests.test_tresca_rounded_references
```

`inputs.json` is immutable; `freeze_inputs.py` records its construction and refuses an existing destination. `sources.json` binds the unchanged candidate, exact-source receipt and existing certificates; the public source hyperlink remains in the [Tresca source packet](../../ingestion/tresca/README.md). Raw copyrighted source bytes remain private. `toolchain.json` identifies the standard-library environment, and `manifest.json` binds this delivery.

Stop reference construction here. Next: review these references and source-invalid/conditioning distinctions, prospectively freeze the backend driver and numerical acceptance policy, then qualify one serial native target followed by one serial Wasm target. No executable installation before that gate.
