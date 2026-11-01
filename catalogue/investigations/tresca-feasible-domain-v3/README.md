# Tresca feasible-domain v3 — continuous success, overall qualification failed

**Native and Wasm both pass all 12 continuous own-state increments. The complete frozen qualification remains failed because two original raw residual probes now reject.** This mixed result is retained without deleting inputs or changing a tolerance. No model is installed or scientifically admitted.

The distinct private [candidate](frozen/model.json) appends `principal_range_le(sigma,width)` to the ordinary model domain. Its equations, parameters/ranges, sigma6/ep6 state, initial check, derived expressions, source hyperlinks and entire shared C++ solver closure are unchanged from [pressure-split v2](../tresca-pressure-split-v2/README.md). Only algorithm identity/description and that domain condition differ. The physical continuum remains [BK2022v1](https://arxiv.org/abs/2207.12719v1); finite backward-Euler integration is project-derived.

## Why test this change

For the exact residual root, `r_sigma=0` implies `sigma=R(T)` in the source-admissible set C. Requiring C removes no exact constitutive solution. The existing generic Newton/backtracking code evaluates the model domain on trial states, so the added condition restricts computational iterates to feasible stress. It does not clip a committed state, change k or soften the yield inequality. [The preceding history failure](../tresca-continuous-history-v1/README.md) showed that an accurate but slightly inadmissible computed root could not restart; its independent nearest-rounded projection was admissible for the failing step.

Before compiled observations, the [independent current-probe inventory](current-probe-inventory.json) identified exactly one original current-state probe outside C: `scaled-face--80`. That probe is a mathematical residual extension away from a physical solution; its original supplied parent is valid. It was retained in full, with no rejection exemption. The unchanged inherited assessor labels its failures `source-valid-case-rejected`; that label refers to the original case gate and does not establish that its arbitrary current probe is physically admissible under the newly imposed domain.

## Prospective scope and results

[policy.json](policy.json), both unmodified copied sub-assessors, original 219-request corpus and 12-step sequence, candidate/generated code and full source closure were frozen in [prospective-freeze.json](prospective-freeze.json) before compilation. One explicit `atlas_tresca_feasible_domain` target was built natively with `--parallel 1`, completed, then built under Emscripten with `--parallel 1`. Each binary ran both corpus and history modes using regular-file stdin. The driver only wraps the original drivers in separate namespaces and dispatches their modes; material and solver code are unchanged. The two branch-capture lines in the corpus header remain removable byte-for-byte instrumentation.

[assessment.json](assessment.json) records, per backend:

- **Continuous history passes:** 12/12 own-state increments accepted, all incoming/committed stresses exactly source-admissible, no reset, clipping, repair, parent substitution or skipped increment. All 288 update components at 200/280 digits meet the original 2e-9 normalized value budget; maximum error is 1.165e-10. Full input preservation and baseline recovery pass.
- **Original corpus fails:** 192 acceptances and 27 rejections over all 219 requests. The only failures are `scaled-face--80/double` and `scaled-face--80/jet`; the new domain rejects that out-of-C current probe. All other cases pass their inherited gates: 2,304 values and 27,360 derivative components, with zero derivative branch coverage gaps. Maximum value error is 1.165e-10 and derivative error 4.14e-14.
- Source-invalid initialization, the actual tentative-Newton iteration-budget failure with full rollback, and same-process recovery retain their original checks.

The iteration limit remains 45, depth zero, residual tolerance 2e-10, value tolerance 2e-9 and derivative tolerance 2e-8. No gate changed after observation. The complete conjunction of both gates is false on both backends. [Backend comparison](backend-comparison.json) separately records stream/result agreement; independent references, rather than backend agreement alone, establish accuracy.

All **69 focused software/evidence tests pass**, including source/candidate/generator identity, preservation of the mixed gate, exact inventory replay and additional derivative/recovery corruptions. This is not an overall material qualification pass.

## Next bounded interface task

This experiment demonstrates that physical solution admissibility and the mathematical residual's evaluation domain need separate representation. Making C the residual domain fixes the continuous path here while preventing the two original extension evaluations. [NEXT_SOLUTION_CONSTRAINTS.md](NEXT_SOLUTION_CONSTRAINTS.md) specifies the proposed generic schema/runtime separation, preserving raw residual evaluation and enforcing constraints through normal feasible-step/commit validation. It is a design proposal, not an implemented or qualified capability.

```sh
python3 -B catalogue/investigations/tresca-feasible-domain-v3/verify.py
python3 -B -m unittest tests.test_tresca_feasible_domain
```

These inspect saved evidence without builds or material execution. Full generated sources, driver, receipts and local binary hashes are retained; compiled binaries and raw source PDFs are not redistributed. Earlier one-step passes and continuous failures remain unchanged. Browser/mixed-control behavior, parameter-expression overflow/representability, calibration and scientific admission remain separate gates. Nine public models remain unchanged; no push or deployment occurs.
