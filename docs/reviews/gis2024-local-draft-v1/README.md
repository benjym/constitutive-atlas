# GIS2024 local integration: failed-default checkpoint

IMPL-gis2024-local-draft-v1 remains **incomplete**. On1November2026 the
pre-installation check found that the unchanged standard browser example
(drained1% strain,100increments, maximum subdivision depth14) rejects its first
update. The complete initial14-state point is retained. No model, catalogue,
web asset, numerical tolerance or default was changed; no installation,
packaging, browser execution, build or deployment occurred.

The original failed result is retained verbatim inside
`default-check-process.json`. `default-check-freeze.json` binds its script,
inputs and policy before execution. The source-linked v0.3 draft and earlier
[bounded laboratory-route pass](../gis2024-laboratory-route-v1/README.md)
remain unchanged. That pass covered1e-5strain or20Pa; it was never evidence for
the ordinary1% interface example. The model's
[primary source](https://doi.org/10.1016/j.compgeo.2024.106480) and
[formulation crosswalk](../../ingestion/hypoplastic-generalized-igs-2024/README.md)
retain separate scientific and initialization limitations.

## Five-case bounded diagnosis

`diagnostic-freeze.json` fixes exactly four direct first-outer-trial increments
and one full run before their observations. The original trial has axial
increment1e-4 and initial lateral guess-0.2times axial in both radial directions.
The smaller comparison is1.25e-6, matching the previously studied small example.
Only diagnostic requests vary maximum depth14/20; no persistent default or
acceptance gate changes.

| First trial axial increment | Depth14 | Depth20 |
| --- | --- | --- |
|1.25e-6|accepts,28substeps|accepts,28substeps|
|1e-4|rejects,0accepted/15rejected candidates; full rollback|accepts,130substeps|

The larger accepted depth20 run reports minimum internal fraction2^-16,
corresponding to a recursive candidate at depth15 because the accepted two
half-steps each record2^(-depth-1). The default14cap cannot visit that candidate.
This follows the unmodified `advance_recursive` acceptance/bisection logic.
A separate diagnostic full drained1%/100increment run at depth20 completes101
points. It is **not** a newly qualified default or independent finite-trajectory
accuracy result. No parameter, tolerance, domain or radius projection was tuned.
The evidence supports a work-limit explanation for this failure; it does not
establish general stability, model accuracy or arbitrary boundary support.

## Concrete example handoff

`example-proposal.json` packages the already-qualified saved Wasm case
`model-example-origin/p1/monotonic/exact` as the existing scoped laboratory
JSON document: explicit14-state input/history,19parameters,8increments,
1e-5strain, exact controls and its explicit depth20settings. Its source case
predates the failed ordinary-default run. `example-provenance.json` pins the
original evidence archive and raw receipt. The ordinary failed default is
retained separately; the proposal does not replace or relabel it.

`prepare_example.mjs` invokes the current pure document creator/parser and
proves lossless full-specification import of this saved result. It loads no
engine and makes no new constitutive call. The proposal is private review
material in this packet, not a published example or browser test.

Next bounded implementation: a **generic, explicit laboratory-example loader**
using the existing scoped document/import validation, exact model/catalogue
binding and visible replacement of all inputs/settings. Label the selected
loading/settings and its limited evidence. Do not silently increase global
subdivision defaults, rewrite the mathematical model, hide the failed1%case,
or imply specimen preparation/calibration. The record must keep model defaults,
numerical settings and named loading examples as separate identities.

After that separately claimed capability and its preparation/reset/import tests,
resume StagesB/C of the [integration plan](../gis2024-browser-preparation-v1/INTEGRATION_PLAN.md):
archive exact shared-source bindings, install the unchanged draft, disclose
pending review/unassessed applicability, package the exact engine and complete
actual browser B01–B12. Existing ten-model ordinary-default regression must stay
intact. A successful explicit example does not turn the retained global-default
failure into a pass.

## Saved-only reproduction

```sh
python3 -B docs/reviews/gis2024-local-draft-v1/verify.py
```

This checks frozen/result identities, original rollback, the five diagnostic
outcomes and fractions, and the example's binding to original raw evidence.
It never loads Wasm, builds, integrates or opens a browser. Diagnostic scripts
remain acquisition records, not rerun commands into this immutable checkpoint.
No scientific admission, installation or deployment follows from this report.
