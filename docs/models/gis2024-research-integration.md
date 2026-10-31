# GIS2024 coupled finite-path research integration

The isolated [14-state research definition](../../models/research/gis2024/hp-extracted-asbs-gis-2024-research.json) now has bounded finite-path comparisons through the common schema-generated C++ engine and its Wasm C ABI. It remains a candidate outside the public executable catalogue. The source is Mugele, Stutz and Mašín (2024), [DOI10.1016/j.compgeo.2024.106480](https://doi.org/10.1016/j.compgeo.2024.106480), [institutional full text](https://publikationen.bibliothek.kit.edu/1000171366/153009465). See the [source-rate selection](gis2024-research-rates.md) and [independent reference contract](../reviews/gis2024-finite-path-reference.md) for exact source locators, sign mapping, initialization and full18 physical parameters. No material-specific handwritten production kernel is added.

## Protocol and retained evidence

Two prescribed full-tensor, zero-spin paths (noncoaxial loading and shear reversal) and fixed-rotation companions begin from explicit stress6/e/h6/Omega. Three original segments per path are compared at rate tolerances1e-4,1e-6,1e-8; caller subdivision into seven parts is additionally tested at1e-4 and1e-8. This gives20 trajectories and204 updates per backend. Every call uses the actual previous returned14state; no reset or endpoint projection is performed. The normalized segment coordinate represents prescribed strain, not physical time.

[Native](../../catalogue/investigations/gis2024-integration-v1/native.json) and [Wasm](../../catalogue/investigations/gis2024-integration-v1/wasm.json) transcripts retain requests, responses, settings, catalogue identities, substep fractions and failure probes. The [independent review](../../catalogue/investigations/gis2024-integration-v1/independent-review/REVIEW.md) documents corruption tests and numerical limits. Every original-segment endpoint is compared in all14components against an independently coded Cartesian coupled law integrated with RK4 on16/32/64 grids. Each returned caller endpoint also passes the independent selected material-domain check; this does not expose every hidden native stage. The independent reference checks its own RK4 stages.

Global endpoint regression budgets differ from local solver tolerances. Stress/e/h/Omega have physical scales p_scale/1/R/1 and declared normalized endpoint allowances5e-3,3e-4,2e-5. These deliberately broad regression allowances are reported beside actual absolute component errors. Additional reference allowances are stress1e-4Pa,e1e-12,h1e-13,Omega1e-10; they are practical regression allowances, not rigorous uncertainty bounds. Fresh reference grid differences must lie below one quarter of each allowance. Current source/dependency pins and fresh local reference replay are checked before assessment. Historical receipt identity is exact; portable archived assessment compares actual trajectories to a fresh current reference rather than treating archived numbers as an oracle.

Observed unrotated noncoaxial maximum stress errors are approximately.017108,.00036316,.0000139753Pa at the three unpartitioned tolerances. Stress/h/Omega errors and caller-partition disagreement shrink with tighter tolerance under separately declared reference floors. Tight noncoaxial Omega errors are below the declared reference allowance, so a resolved convergence order is not claimed there. More caller subdivisions need not improve every individual component. Density is separately checked using the exact relation1+e=(1+e0)exp(-sum(trace(strain))). Maximum scaled native/Wasm parity is3.39e-17 in the retained execution.

The native budget probe fails after partial progress (two accepted substeps) and returns the exact initial14state. Invalid initial memory radius also rolls back exactly; a zero increment succeeds unchanged. A persistent Wasm instance executes an identical valid control after each budget/domain/zero probe. Full control/recovery request-response pairs are retained and independently checked for exact recovery equality. The transcript alone cannot prove temporal execution order; pinned Node runner code and its executed report provide that evidence.

## Reproduction

Use existing compiled isolated targets; builds remain serial locally:

```sh
python -m tools.gis2024_integration_study --output /tmp/gis2024-native.json
node tools/test_gis2024_paths_wasm.mjs --native-report /tmp/gis2024-native.json --wasm build-wasm/gis2024.js --output /tmp/gis2024-wasm.json
python -m tools.verify_gis2024_paths /tmp/gis2024-wasm.json
python -m tools.verify_gis2024_paths catalogue/investigations/gis2024-integration-v1/wasm.json --reference-receipt catalogue/investigations/gis2024-path-reference-v1/reference.json
python -m unittest tests.test_gis2024_path_reference tests.test_gis2024_integration_study -v
```

The investigation manifest binds source files, model, references, tests and retained records. Binary hashes identify the executed artifacts; binaries are not bundled and numerical success does not establish deterministic rebuild identity. CI reruns native/Wasm comparisons from a fresh build.

## Remaining admission gates

Interior paths leave substantial work: memory origin, full-memory and Omega endpoints, boundary-stage policy, within-segment branch changes, wider pressure/density/parameter/amplitude/duration coverage, source-backed preparation, author implementation/discretization/license reconciliation, calibration, experimental comparisons and independent human scientific review. This milestone supplies numerical integration evidence for the selected research pairing. It does not establish physical validation or public admission. Public counts remain5 executable definitions and27 candidates.
