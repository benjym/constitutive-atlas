# Tresca continuous own-state history — retained failure

**Continuous-history qualification fails on both native and Wasm.** The unchanged pressure-split/exact-range candidate accepts the first three increments, commits a stress just outside the exact source-admissible set, then rejects that state as the fourth increment's parent. The remaining eight increments are explicitly not attempted. The earlier [one-step/frozen-parent study](../tresca-pressure-split-v2/README.md) remains passed within its stated scope; it did not prove continuous usability.

## Prospective study

[inputs.json](inputs.json) preserves all 12 original increments, initial sigma6/ep6 and material parameters from the independent rounded-input reference packet. Each next parent is the preceding actual accepted state, bit-for-bit. There is no reference-parent substitution, clipping, repair, skipped increment or reset after rejection. [policy.json](policy.json), the independent assessor, unchanged model/generated header, full C++ closure and wire inputs were pinned in [prospective-freeze.json](prospective-freeze.json) before any compiled observation. The ordinary uninstrumented generated candidate and shared solver are unchanged.

One explicit `atlas_tresca_history` target was built natively with `--parallel 1`, completed, then built under Emscripten with `--parallel 1`. The candidate receives the complete sequence once and advances its own state within one process. Native and Wasm each produce all scheduled-step records, including the not-attempted tail and summary. State bits are retained as decimal uint64 strings, preserving every binary64 bit, including signed zero.

The gate requires every incoming and returned committed state to satisfy the exact source range inequality, every scheduled increment to be accepted, source-valid accepted updates to meet the original 2e-9 componentwise normalized budget, and full rollback/recovery behavior. Depth remains zero, iteration limit 45 and residual tolerance 2e-10. The independent checker uses the frozen original six-plane projection at 200/280 digits and the separately proved exact Fraction/radical plus Sturm membership oracle. Actual recorded parents condition these reference calculations; the algorithm and thresholds were frozen before observation. No original source/reference parent chain is silently substituted.

## Observed failure

[assessment.json](assessment.json) gives the same result for both backends (indices are zero-based):

- Steps 0, 1 and 2 are accepted; all 72 checked update components across two precisions meet the value budget. Maximum normalized update error is 1.02e-16; independent reference cross-precision difference is below 5.48e-183.
- Step 2 starts from an exactly admissible parent but commits a stress outside the exact source boundary. Both high-precision checks give a principal-range excess of about **1.81304e-16 Pa**; both exact membership methods classify it outside.
- Step 3 rejects that parent and returns its complete incoming sigma6/ep6 bits unchanged. Steps 4–11 are not attempted and fail the all-increments gate. There are 10 recorded failed assertions per backend.
- All input bits remain unchanged, accepted increments use one unsplit step, and every attempted call is followed by successful same-process zero-load baseline recovery.

The source continuum remains [BK2022v1](https://arxiv.org/abs/2207.12719v1); [the dossier](../../../docs/ingestion/tresca/README.md) distinguishes the mathematical law from the project-derived finite backward-Euler integration. Numerical update accuracy within a residual tolerance does not establish exact admissibility of the floating committed state. Neither changing the source inequality nor widening its tolerance is justified by this result.

## Separate diagnostic and smallest next experiment

The post-observation [rounding diagnostic](rounding-diagnostic.json) has its own prospectively frozen script/question in [rounding-diagnostic-freeze.json](rounding-diagnostic-freeze.json). It is diagnostic evidence and does not change the original gate. At step 2, componentwise nearest binary64 rounding of the independent projection is identical at both precisions and **is admissible**. The actual result differs in Mandel shears 3,4,5 and plastic component 9. Thus this particular failure is not shown to be unavoidable nearest-rounding infeasibility.

[NEXT_FEASIBLE_DOMAIN.md](NEXT_FEASIBLE_DOMAIN.md) proposes a distinct private candidate experiment using the existing source stress inequality as an ordinary model domain condition, letting the existing Newton/backtracking machinery enforce feasible iterates. This is a hypothesis with an exact-root-set argument, not a proven convergence fix. It must be frozen and tested against all prior cases and this full history, with unchanged accuracy criteria; it must not be used to retrospectively pass this study.

All **65 focused software/evidence tests pass**, including deliberately corrupted chain/value/recovery checks and preservation of both earlier failed and passing studies. That software result does not make continuous qualification pass. No model is installed, admitted, published or deployed.

```sh
python3 -B catalogue/investigations/tresca-continuous-history-v1/verify.py
python3 -B -m unittest tests.test_tresca_continuous_history
```

These reopen saved evidence without running a material or build. Full process receipts, generated code, driver and local binary hashes are retained; raw source PDFs and compiled binaries are not redistributed. `run_study.py` records the original serial build recipe and checks prospective pins.
