# Tresca pressure-split v2 — private one-step/restart qualification

**Both native and Wasm pass the prospectively frozen 219-request qualification.** This is a private research algorithm variant of the [BK2022v1 continuum law](https://arxiv.org/abs/2207.12719v1), with separately project-derived backward-Euler integration. It is not an installed or scientifically admitted model. Full state sigma6/ep6, source hyperlinks, material parameters, domains, tensor/sign/frame contracts and loading inputs are preserved.

The candidate combines the [source-equivalent pressure-split residuals](../../../docs/reviews/tresca-pressure-split-v1/README.md) with the [qualified generic exact principal-range predicate](../../../docs/reviews/exact-principal-range-runtime-v1/README.md). It uses that predicate for strict initial sigma membership and the computed trial-deviator yield decision. Corner selection and spectral return expressions remain unchanged. The independent [high-precision transformed residual references](../../../docs/reviews/tresca-pressure-split-v1/README.md) preserve the original complete returned states/history and all 38 update directions; only the algebraically equivalent plastic residual rows change. This candidate has its own identity in [frozen/model.json](frozen/model.json).

## Gate and outcome

[policy.json](policy.json), [assess.py](assess.py), full source closure, original/instrumented generated headers, literal wire inputs and reference pins were bound by [prospective-freeze.json](prospective-freeze.json) before any compiled candidate observation. Every original v1 request and byte of compressed wire input is retained: 183 evaluations/solves over all 61 cases, 12 frozen-parent history restarts, 23 negatives and one actual tentative-Newton rollback transaction. Value tolerance remains 2e-9 normalized by max(1,abs(reference)); all 38 derivative-column tolerances remain 2e-8. There is no input deletion, fitted tolerance or adjacent-branch derivative exemption allowing a full pass.

Each backend ran one serial Release target, `atlas_tresca_pressure_split`, with `--parallel 1`; native completed before Wasm began. Both used regular-file stdin prospectively, with complete successful 219-row execution receipts. The driver records branch selection through exactly two removable instrumentation lines; stripping them restores the normally generated header byte-for-byte. No handwritten constitutive kernel is added.

[assessment.json](assessment.json) reports, for each backend:

- 194 expected acceptances and 25 expected rejections; zero failures or derivative coverage gaps.
- 2,328 checked value components, maximum normalized error 2.32e-15.
- 27,816 checked residual derivative components (61 cases × 12 components × 38 columns), maximum normalized error 4.14e-14.
- All accepted solves use exactly one unsplit backward-Euler step. All input bits and same-process baseline recovery checks pass.
- The iteration-budget transaction actually changes a tentative full state, then fails and returns the exact incoming sigma6/ep6 state. Immediate baseline recovery succeeds.

The original failures are concretely resolved: the 2^60 Pa hydrostatic case now selects the upper return and preserves the three plastic components `(0.625,0.25,−0.625)`; the dense near-yield Jet case selects the independently required face derivative; source-invalid rounded history parent7 and its negative duplicate both reject. [The original v1 assessment](../tresca-rounded-backends-v1/assessment.json) remains failed and unchanged.

[backend-comparison.json](backend-comparison.json) separately records exact shared status/branch/diagnostics and the floating differences between native/Wasm. Independent-reference agreement, rather than backend agreement alone, establishes this bounded numerical result. All 61 focused regression tests pass, including frozen-source reopening, normal generator reproduction, deliberate value/column37/membership/branch/rollback/recovery corruption, and the prior generic DSL/evidence suite.

## Reopen and next gate

```sh
python3 -B catalogue/investigations/tresca-pressure-split-v2/verify.py
python3 -B -m unittest tests.test_tresca_pressure_split_backends
```

These commands inspect saved evidence and do not evaluate a material or build anything. `run_study.py` retains the serial build recipe and verifies all prospective pins before a compiled stage. `native-artifacts.json` and `wasm-artifacts.json` bind the local binaries; binaries remain outside the repository. Original raw source PDFs are not redistributed.

This study compares each source-valid history restart against a frozen reference parent and requires rejection of source-invalid parent7. It **does not prove a continuously accepted loading history using the candidate’s own rounded committed state**. Do not repair, clip, skip or reset a rejected step to claim such a path. The next bounded study must freeze a complete continuous sequence and its acceptance policy, then retain the actual committed/rejected trajectory and independently check the source membership and update accuracy. Browser laboratory behavior, mixed controls, experimental calibration and scientific admission remain separate gates.

Exact membership concerns the computed finite binary64 operands; it cannot undo prior trial arithmetic rounding or overflowing `2*k`. Recombined absolute stress can lose an unrepresentable small deviator at a large mean. All 61 frozen cases are retained and pass their original numerical budgets, but this is not an unlimited finite-parameter guarantee. Nine public model definitions remain unchanged; no installation, publication, push or deployment occurs here.
