# Candidate source/finite-law audit v1

Reviewer `/root/occ_selection_review`, 1 November 2026. This follow-up preserves all previous frozen review outputs. No model, checker, source evidence or shared code was edited by this reviewer. No builds/compiled calls or E5 decision occurred.

**Changes requested for candidate SHA-256 `7e528930d05ec38ec1c286fa114749b4fc148affb454425297aac2c85f1f4977`.** The source contract remains accepted. The candidate's normalization can produce a nontraceless stress deviator from legitimate near-hydrostatic stored controls, violating its own finite equations. This is separate from the previously identified rotation input producer failure. Changing only the rotation producer cannot resolve the candidate flaw.

## Exact stored-input oracle

`candidate-review-check.py` binds every binary64 state/control component with `Fraction.from_float`. It computes the exact rational trace/deviator before conversion to Decimal, then invokes the independent bisection oracle of the uneliminated finite equations. Tensor output is reconstructed from that independently determined deviatoric direction. No target elimination is used as oracle. The budget remains `2e-10` with pressure normalization by pref, unchanged from prospective policy. The checker records candidate and dependency hashes and writes a distinct result filename keyed by candidate hash.

Reproduce:

```sh
python3 -B docs/ingestion/original-cam-clay/control-selection-v1/independent-review/candidate-review-check.py
```

For the reviewed candidate, 405 of407 cases pass: all400 corpus cases, all4 pure tiny shears including `1e-200` and the minimum binary64 subnormal, and one adjacent-diagonal case. Two actual finite-law failures are retained in `candidate-review-results-7e528930d05e.json`:

- The retained rotated stored control fails the finite-law gate with error `9.604058450989866e-5` against `2e-10`.
- A pressure50000 Pa, pc100000 Pa interior state with `de=(-.03333333333333333,-.03333333333333333,nextafter(-.03333333333333333,+inf),0,0,0)` fails with error `0.8278966338024831`.

The first failure is especially transparent. The candidate computes normalized input `(-1,-1,-0.9999999999999998,0,0,0)`. Subtracting the rounded mean gives `Dbox=(0,0,2.220446049250313e-16,0,0,0)`, hence unit direction `(0,0,1,0,0,0)`. The true stored-input deviator direction is proportional to `(-.5,-.5,1,0,0,0)`. Candidate `plastic_s` has a nonzero trace: output mean is `.10657202909726109 Pa`, while its own `p_end` is `.02815522021462834 Pa`. This is a finite flow/pressure error amplified by shear rigidity, rather than an acceptable small roundoff discrepancy.

## Source audit and numerical selection

Apart from the normalization defect, candidate equations faithfully express the reviewed elimination, zero-distortion projection and corner. Exact zero loading is selected by maximum absolute extracted component, with no positive amplitude threshold. Nonzero distortion selection is independent of `rmag`, so underflow of a minimum subnormal magnitude does not silently select hold; normalized direction supplies the correct finite limiting jump. Those pure tiny-input checks pass the actual stored-control oracle. The separate zero-hold sigma selection and division by one preserve the old stress/v exactly for tested holds.

The current checker's ideal scalar corpus comparison handles one rounded-away tiny-r case, but that exception is not a general exact stored-control binding. Independent tensor/state binding is required because trace, shear magnitude and direction can differ from ideal E/r after rounding. The new checker supplies that binding. Its results do not replace the original source-algebra or path-refinement studies.

A bounded repair can use raw pairwise diagonal differences to detect/extract distortion before normalization, combined with normalized off-diagonal components, followed by algebraic traceless reconstruction. Near a common hydrostatic value, pairwise subtraction retains the physically stored adjacent differences that a rounded mean destroys. Overflow or genuinely lost direction must fail explicitly, rather than selecting the hydrostatic branch. This is an implementation suggestion, not a required new generic primitive or a change to the law. No amplitude cutoff is justified by these observations.

## Rotation failure and revised input producer

The retained original rotation failure has two distinct issues:

1. A floating matrix multiplication changed exactly isotropic strain into unequal stored diagonal values. Those wire controls describe a real, tiny deviator and can legitimately trigger a finite source shear-rigid jump. Comparing their output with a rotated hydrostatic output tests a different input. The failure must remain retained; it does not prove that a tolerance should be relaxed.
2. The candidate then computed the wrong direction and nontraceless stress for those actual controls, as independently demonstrated above. The input producer explanation does not excuse that second failure.

Exactly representable signed-permutation rotations are valid covariance cases and preserve stored hydrostatic controls. For a general orthogonal rational rotation, producing a hydrostatic tensor analytically as the identical scalar times I is a source-preserving input binding, with no change to the law or numerical gate. High-precision rational matrix rotation with a final rounding can test nondegenerate deviatoric controls; those actual rounded inputs must also satisfy the finite-law oracle. These complementary cases adequately test intended fixed-frame covariance within declared numerical budgets once the candidate defect is repaired. They do not establish covariance uniformly near every discontinuous zero-distortion boundary, which binary64 rounded tensor transformations cannot promise.

The parent's `rotation-producer-v2.json` preserves the original failure and unchanged `2e-10` gate, distinguishes new input generation, and claims no source/model change. That is a legitimate prospective correction to the input producer, not a retrospective gate relaxation. Actual new producer outcomes remain subject to independent binding and the candidate correction above.

Smallest next action: repair the candidate's distortion extraction, rerun the unchanged exact stored-input oracle (new candidate hash/result identity), then resume source-path and backend qualification. The earlier accepted design review is unchanged; this audit supplies concrete implementation failures rather than speculative requirements.
