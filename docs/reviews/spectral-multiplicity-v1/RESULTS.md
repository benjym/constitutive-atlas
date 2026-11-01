# Generic spectral multiplicity capability — accepted v4

Independent [final review](independent-review/FINAL_REVIEW_V4.md) accepts the exact v4 capability and its bounded numerical/transaction evidence. The original [contract](CONTRACT.md), [policy](POLICY.md), [history expectation correction](HISTORY_EXPECTATION_V3.md) and [range-safe composition revision](COMPOSITION_V4.md) identify the final behavior without rewriting earlier failed versions.

Native and Wasm each pass73 exact-wire cases:127 successful extrema and19 expected numerical failures,7153 independent accuracy checks, all38 derivative columns,1404 nonfinite checked-input cases, generated model/history routing and rollback/recovery checks. Worst error/allowance is0.240084. Both backends independently satisfy the frozen reference bounds. One resolved near-gap case (row35) differs in derivative floating bits; bitwise parity is not claimed. The extra wire-equality diagnostic is retained in parity-wire-diagnostic.json. See [backend-results-v4.json](backend-results-v4.json), native/wasm-assessment-v4.json and exact response files.

The predicates classify the exact stored Mandel matrix via dyadic/radical arithmetic.48 existing independent360-digit stored-Mandel references are reused;24 signed/scaled exact radical repeated-pair cases add known cluster rows, with100/160-digit convergence; one distinct one-ULP case retains numerical rejection. Independent reviewer checks additionally cover322 production Python cases against polynomial Euclidean-GCD references.17 assessor corruptions reject. Source regressions cover typing, event dependency restrictions, lazy behavior, current generic spectral/formulation behavior and historical generation.76 historical source bindings in28 sidecars were preserved before the three shared DSL/compiler edits, and replay still resolves their exact snapshots. No old primitive, schema or existing model bytes changed in this task.

Retained failures: reference assembler initially assumed every inherited special request had a case key; native driver initially omitted its local vector alias; v2 history recovery incorrectly expected no successful advance event; v3 trace-before-division overflowed at DBL_MAX hydrostat; first Wasm link could not write the system toolchain cache. The latter was resolved by copying the46MB installed cache into permitted /private/tmp storage. The distinct v3/v4 study freezes and failures remain intact. Numerical references, thresholds and expected successes were not weakened; v4 improves the hydrostatic expression to meet the existing success gate. No failed version is reported as passing.

Reproduce from the repository root, choosing fresh isolated build directories:

```
python3 -B -m unittest tests.test_spectral_multiplicity tests.test_spectral_multiplicity_evidence -q
cmake -S docs/reviews/spectral-multiplicity-v1 -B /private/tmp/multiplicity-native -DCMAKE_BUILD_TYPE=Release
cmake --build /private/tmp/multiplicity-native --target atlas_spectral_multiplicity --parallel 1
/private/tmp/multiplicity-native/atlas_spectral_multiplicity < docs/reviews/spectral-multiplicity-v1/requests.txt > /private/tmp/multiplicity-native.jsonl
python3 -B docs/reviews/spectral-multiplicity-v1/assess.py /private/tmp/multiplicity-native.jsonl
```

For Wasm configure via emcmake, build the same explicit target with --parallel1 after native completes, and run the resulting spectral-multiplicity.js through node with the same requests. If the installed cache is outside write permission, copy it to an allowed temporary directory and set EM_CACHE to that copy for linking. Frozen sources/requests/references/generated contexts are hash-bound by frozen/source-manifest-v4.json. binary identities are in backend-results-v4.json; no binary distribution is needed to replay the saved assessor. Run serial builds under a coordinator handoff; no remote CI is triggered here.

This completes the generic expression capability. It does not qualify Duncan's nonlinear update, full source-path controls, model-specific tangent, experimental fit, E5 approval, catalogue integration or website delivery.
