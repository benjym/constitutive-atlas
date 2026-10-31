# Exact nonzero hydrostatic Barodesy AD study

This additive research packet verifies a separate generated-model probe for the zero-spin Medicus/Fellin 2017 **body Eqs. 1–10**, with body density based on 2p and the fixed 1000 Pa scale. It leaves the model, regular-direction driver and shared compiler unchanged. Actual native and Wasm runs now pass the bounded study; this is not a model admission.

The packet contains 36 exact-hydrostatic requests: London, Dresden, and Weald Table 2 parameters; s=±0.001, ±0.1, ±1 in E=sI; and an anisotropic SPD stress plus a dense rotation rounded to actual binary64 inputs. Void ratio is 0.8. The independent reference evaluates the same supplied binary64 inputs in Decimal arithmetic at 100 and 160 digits. Largest normalized precision difference across rates and all 91 Jacobian components is approximately 4.05377e-98. This is observed refinement, not a rigorous rounding certificate.

Thirty-one pure Python protocol/reference test groups pass. They include full reference regeneration, actual Python DSL **primal-only** comparisons for all 36 cases, strict verifier corruption tests, and mocked native transport tests. The largest Python stress-component relative error against the Decimal reference is 2.7585961365838057e-14 and void closure differs by at most one ULP. JavaScript syntax validation passes. The retained actual Jet runs are assessed separately below.

## Additive files

- `tools/reference_barodesy2017_hydro.py`: independent stdlib Decimal source-body reference and analytic 7×13 Jacobian. No Atlas/operator/other rate-oracle imports.
- `tools/barodesy2017_hydro_ad.py`: complete case matrix, strict collector/verifier, fresh independent reference comparison, raw retention, and CLI.
- `tests/barodesy_hydro_ad_driver.cpp`: separate actual generated `evaluate_model<Jet>` C ABI/CLI; all 13 seeds simultaneously.
- `tools/test_barodesy2017_hydro_ad_wasm.mjs`: persistent actual C ABI collector.
- `tests/test_barodesy2017_hydro_ad.py`: pure Python tests; subprocesses are mocked.
- `catalogue/investigations/barodesy2017-hydro-ad-v1/reference.json`: retained independent inputs and analytic reference, not a compiled result.
- `docs/models/barodesy2017-hydro-first-derivative.md`: source choice and first-derivative derivation.
- `CMakeLists.txt`: authoritative separate target reusing existing `atlas_barodesy_models` generation.
- `tools/barodesy2017_hydro_transport.py`: strict raw transport correspondence audit.

The source-bound manifest pins implementation, references, reviews and retained run evidence. Existing rate/material AD tools provide utilities; their script hashes are bound in reports. No legacy or regular-driver edits are needed.

## Probe and numerical contract

C ABI: `atlas_barodesy_hydro_ad(model_id, parameters_csv, state_csv, increment_csv)`. The native CLI accepts the same four strings or `--describe`. The model must have the complete expected generated self-description and explicit parameter order. State order is six Mandel stresses then void ratio. The 13 Jacobian columns are six current stresses, void ratio, and six Mandel loading components. Parameters are fixed and previous-state values unseeded because this body law has no previous-state dependence. All unused Jet derivative slots must remain zero.

Exact hydrostatic classification compares all three input normals and requires all three input shears to equal zero. It additionally requires a nonzero scalar and nonzero representable norm. A computed deviatoric norm is not used to decide whether ±0.1I is hydrostatic. Zero, regular nonhydrostatic, and a one-ULP normal mismatch are excluded from this probe's support. Failure makes both rates and Jacobian unavailable; there is no zero-output substitute.

Every response binds model ID/hash, ordered parameters, full state/loading, exact column order, strict Boolean status, finite 7-vector and 7×13 outputs, or the exact failure envelope. Reports bind full model definition, parameter order, oracle/study/utility-script hashes, and backend artifact bytes. Artifacts are hashed before and after collection. Skipping artifact byte access with `assess(..., check_artifacts=False)` still validates path/hash shapes and means those bytes were not verified now.

The independent verifier recomputes each complete 100/160-digit reference and all metrics. Stress-rate and nonzero stress-Jacobian components use `abs(actual-reference)/max(1,abs(reference)) <= 2e-12`. Void primal/derivative entries must lie within four ULPs of the independent reference; structurally zero Jacobian components must be exactly zero. This prevents large Pa-valued channels from masking incorrect dimensionless closure or forbidden shear derivatives. Loading Euler homogeneity is also checked. No threshold is changed after compiled observation.

The invalid corpus inherits the rate study's finite invalid requests unchanged, then adds explicit zero/nonhydrostatic/one-ULP-nonhydrostatic/wrong-loading-count requests. The original inherited/scope corpus contains 20 requests and is recomputed from the installed rate corpus. Independent review added 28 exact-hydrostatic state/parameter rejection cases at both signs: indefinite/zero stress, negative void ratio, each parameter just outside both bounds and lambda=kappa. The total is 48 invalid/recovery pairs. Inherited nonhydrostatic K0 requests test **scope rejection**, not a hydrostatic K0 continuation. Each rejection is followed by the first valid control, which must reproduce exactly.

## Same-instance transport and failure retention

Native collection runs this separate driver's `--stream` mode once, sending description followed by all valid requests and invalid/control pairs. All generated evaluations therefore occur in one process. Stream exit 0 means the transport completed; expected constitutive rejections still return strict `ok:false` envelopes. The four-argument CLI independently retains exit 0 for successful response and exit 1 for rejected response. These are different, explicit transport contracts.

The native collector writes a companion `<output>.transport.json` before invoking the process, then retains raw stdout/stderr/exit status before parsing or accepting any result. A malformed/partial/abnormal response remains available in that companion, including timeout output. Parsed rows are checkpointed before numerical assessment. Wasm uses one module instance and flushes raw C ABI strings and partial rows before validation. Reports retain `exact_hydro_AD_validated=false`; successful independent assessment returns a separate bounded success summary. A collection-complete flag describes collection, not scientific acceptance.

## Actual compiled results

Both Release targets were built one at a time with `--parallel 1`. Each backend passed all 36 actual generated-model 7x13 Jacobians and 48 rejection/recovery pairs in one process/module. Maximum component error against fresh 100/160-digit analytic references was 2.77874e-14, within the predeclared 2e-12 budget; void closure and derivatives differed by at most one ULP. Native/Wasm values and Jacobians matched exactly for this matrix. The raw auditor matched all 133 descriptor/valid/invalid/recovery calls per backend to the retained reports. Separate native four-string CLI calls confirmed exit 0/1 for valid/rejected requests.

The [retained packet](../../catalogue/investigations/barodesy2017-hydro-ad-v1/manifest.json) binds unmodified reports, raw companions, fresh assessment and build receipt. [Independent review](barodesy2017-hydro-independent-review.md) preceded compiled execution and supplied the exact-hydro domain supplement. Its independent Cartesian Decimal differences corroborate all 13 directions for both signs and three soils; they do not establish arbitrary near-hydrostatic Jet accuracy. No remote CI result or reproducible-build claim is made. Retained no-execution replay validates receipts and numerics without reading current binary bytes.

## Commands after a separate serial build

Pure checks: `python3 -m unittest discover -s tests -p test_barodesy2017_hydro_ad.py`.

Fresh independent retained reference check: `python3 -m tools.barodesy2017_hydro_ad --verify-reference`.

Native collection: `python3 -m tools.barodesy2017_hydro_ad --native /absolute/path/to/atlas_barodesy_hydro_ad_probe --output /private/tmp/barodesy-hydro-native.json`.

Wasm collection: `node tools/test_barodesy2017_hydro_ad_wasm.mjs --native-report /private/tmp/barodesy-hydro-native.json --wasm /absolute/path/to/barodesy-hydro-ad.js --output /private/tmp/barodesy-hydro-wasm.json`.

Independent verification: `python3 -m tools.barodesy2017_hydro_ad --verify /private/tmp/barodesy-hydro-wasm.json`. If the native transcript moves, pass `--native-report-path /new/path/native.json`; the stored original hash must still match. The verifier independently checks both native and Wasm analytic comparisons and component parity, rather than accepting JavaScript parity alone.

## Explicit limits

Only exact nonzero hydrostatic first derivatives are targeted. The local reference retains general nearby-evaluation helpers from the reviewed derivation, but the probe, study matrix, and accepted reference API do not admit near-hydrostatic inputs. Fixed Decimal precision can flatten extremely tiny nonhydrostatic corrections in those helpers; they are not an all-binary64 near-hydrostatic oracle. The pure Python primal comparisons do not evaluate Jet derivatives.

The source's body-versus-appendix density discrepancy and printed spin expression remain unresolved. Finite-spin transport, zero-loading derivatives, near-hydrostatic production Jacobians, second derivatives, all-parameter/all-state validation, integration, experiments, and public admission remain outside this packet. The successful compiled runs establish only this bounded first-derivative gate. Isotropic finite integration is assessed separately in the prior finite-path study; this packet supplies no integrated tangent or wider path result.
