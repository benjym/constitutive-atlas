# Independent candidate v3 representability review

Reviewer `/root/occ_selection_review`, 1 November 2026. This additive review leaves previous candidate/review/failure identities intact. The reviewer read the retained native-v1 transaction response but built or executed no compiled artifact. This is bounded source/portable review, **not E5 approval** or a passing transaction assessment.

**Accept the two v3 guards as a source-preserving correction of the observed representability defect.** Reviewed candidate SHA-256: `637ba72335c3464fec427c773d214d21d06e9e26bc737d15307aae2f67111b34`. Exact comparison with v2 shows only the domain changed:

```text
p_end > 0 * pref
trace(sigma_end) / (3 * pref) > 0
```

The unchanged source relation requires strictly positive pressure and logarithmic pressure/packing coordinates. A target exponential rounded to zero is not an admissible positive-pressure solution. The first guard rejects that target independently of a still-positive current Newton unknown. The second additionally requires stress assembly to retain a positive target mean in the normalized pressure representation needed by the next log evaluation. Neither adds a physical cutoff, changes a source branch or alters the finite equations. They implement the contract's existing representability requirement.

Evaluated-node finiteness already rejects nonfinite target pressure, stress, volume, packing coordinates and other derived quantities. A zero/nonfinite v_end cannot pass its subsequent alpha/log-derived evaluation. q_capacity is explicitly nonnegative. No additional mandatory source primitive or tension/principal-stress restriction is justified by this defect. These checks protect representability; they do not promise relative accuracy throughout binary64's range.

## Independent checks

```sh
python3 -B docs/ingestion/original-cam-clay/control-selection-v1/independent-review/candidate-v3-check.py
python3 -B docs/ingestion/original-cam-clay/control-selection-v1/independent-review/candidate-v3-guard-check.py
```

All407 exact stored-input finite-law cases pass the unchanged `2e-10` gate. The new checker changes only candidate filename/result identity from the independent v2 checker and preserves the original bisection/Fraction input binding. Results are in `candidate-v3-results-637ba72335c3.json`.

The guard witness starts at p50000 Pa, pc100000 Pa with v set by OCC packing, and prescribes stored diagonal increments `(-.3333,-.3333,-.3333)`. V2 evaluates p_end=0 and admits its domain. V3 rejects explicitly. This reproduces the mathematical defect's mechanism without executing native/Wasm. `candidate-v3-guard-results.json` preserves exact inputs/results and both model hashes.

## Preserved failure and residual conditioning limit

The retained native-v1 accepted-prefix request expected failure with rollback. Instead it returned success,4 quarter substeps, stress around `1e-48 Pa` and v439.87300967663458 while later target pressure underflowed. That is a failed frozen study. The v3 fix must be tested against the same expected outcome under a new exact model/build/evidence identity; no pass is inferred here and the v1 failure must remain visible.

There is a separate, concrete absolute-residual conditioning limit even when the target pressure remains positive. The portable guard study constructs a possible current state for p_n50000 Pa/pc_n100000 Pa and de=`(-.3,-.3,-.3,0,0,0)`. Target pressure is `1.1599856702799458e-168 Pa`. A hypothetical current stress `1e-48 I Pa`, with exact endpoint v17.666918500247778, passes the v3 domain and has scaled equation residual `1e-51`, below the engine's `1e-11` residual criterion. Its uneliminated zero-distortion elastic log-recovery mismatch is `-.6252630949841702`. This is a portable residual-conditioning witness, not an observed v3 compiled result or a newly imposed numerical gate.

Thus the correction is sufficient for the **zero/nonrepresentable target** failure, while it does not cure poor relative pressure/history accuracy at arbitrarily small positive stresses. The new `candidate-v3-numerics.md` correctly discloses that limitation. E5 applicability and public numerical scope must retain it concretely and bind approval to actually qualified pressure/parameter/history scales. Do not advertise these two domain guards as establishing all-positive-pressure relative accuracy or as resolving the generic absolute-scaled-residual conditioning issue. No source completeness claim is invalidated by an explicitly bounded numerical accuracy scope, and no unrequested generic runtime change is warranted by this review.

Smallest next action: coordinator reruns unchanged source/transaction/parity gates against the exact v3 candidate in execution-v2, preserves the v1 failed transaction, and supplies actual final backend evidence plus this limitation for independent E5 review.
