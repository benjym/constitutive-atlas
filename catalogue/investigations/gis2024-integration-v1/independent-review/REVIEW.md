# GIS2024 finite-path integration: independent bounded review

Reviewed 2026-10-31. Repository read only; no builds, native or Wasm calls. Numerical reassessment imports only Python reference/verifier code and retained JSON.

## Result and corrected blockers

The current installed verifier resolves the four retained corruption probes. Native 20-trajectory/204-update evidence reassesses exactly; the Wasm 20-trajectory/204-update evidence also passes fresh independent reference assessment. Recomputed maximum scaled native/Wasm difference is 3.3881317890172014e-17, with matching native report receipt. This supports this strictly interior, zero-spin finite-path regression milestone. It does not establish scientific/public admission or boundary/saturation integration readiness.

Original verifier snapshot accepted four false positives: failed-probe settings replaced by {}, nonsensical failed diagnostics, and invalid Omega=2 or hnorm=.01 (R=.0001) at an intermediate seven-partition endpoint with the next call rechained. These are reproducible in audit_runner.py; observations.json pins the original snapshot. Installed tools/gis2024_integration_study.py now checks settings and partial failure diagnostics (lines145-165), applies independent zero-direction material-domain validation at every returned caller endpoint (lines101-104), pins reviewed dependency receipts (lines18-20,37-42), and preflights the selected model/state/parameter contract (lines73-85). postfix-observations.json records all four probes rejecting. No unresolved reference-trust blocker was found for this bounded matrix.

## Numerical interpretation

Requests chain actual returned state between calls; partitioned paths split the same full-six segment increment with a final residual correction. Identical original segment endpoints receive comparison against an independent Cartesian fixed-step RK4 reference. Rotated companions are independent path cases. Local rate tolerance, global endpoint regression budgets and reference budgets are separate quantities. Reference uncertainty allowance is a declared practical allowance, not a rigorous mathematical bound.

The 16/32/64 reference grids have stress/h/Omega observed ratios approximately15.58–16.13, compatible with fourth-order smooth-segment RK4 in these cases. Reversals occur at segment boundaries. This does not prove a universal order for branch crossings or arbitrary paths. The e relation is checked independently through exact volume evolution and is floating-point limited. Fine-grid differences and conditional Richardson estimates cannot certify absolute error.

The declared global stress endpoint allowances are about583.33,35,2.3333Pa for tolerances1e-4,1e-6,1e-8. Actual retained errors are much smaller: e.g. unrotated noncoaxial stress .017108/.00036316/.0000139753Pa. h and Omega errors also shrink. Noncoaxial tight Omega errors (~3.23e-11) lie below the declared1e-10 reference allowance; claiming a resolved convergence order there would be too strong. Tight caller subdivision need not improve every channel: unrotated noncoaxial tight stress error is about1.83e-5Pa with seven partitions versus1.40e-5Pa unpartitioned. The supported observation is shrinking caller-partition disagreement as tolerance tightens, not monotonic improvement from extra caller partitions.

Every returned caller endpoint now passes the independent selected source domain. This is not a check of every hidden native integration stage; the independent RK4 reference separately checks its own stages. Selected starts stay strictly inside h radius and Omega bounds and away from memory origin. No boundary-invariance, saturation-start, preparation, experimental-data or source-parameter calibration claim follows.

## Failure and persistent-runtime evidence

Actual native budget failure occurs after2 accepted substeps and6 rejections, accepted fractions[.0078125,.0078125], and returns the exact initial14state. The invalid-initial-h probe fails with zero progress and exact initial-state rollback. The zero update succeeds unchanged. These are retained distinct from successful trajectory comparisons.

The Node runner actually chains204 Wasm updates, compares scaled state parity and executes an identical valid control after budget/domain/zero calls in the same module. Its source asserts exact returned response recovery. The retained JSON stores probe responses and a persistent_recovery_verified boolean, rather than full recovery/control responses; Python reassessment independently validates the probe responses and204path updates, but cannot reconstruct those unretained recovery calls from the boolean alone. Treat persistent recovery as an executed runner assertion with pinned source, not a fully independently replayable archived recovery transcript. Recording those pairs would strengthen archival evidence; this is not a blocker for the scoped path comparison.

## Provenance and reproduction

Reference exact replay is a local numerical gate. Portable archived reassessment may bind a historical reference receipt while comparing actual trajectories to a fresh current independently evaluated reference; this must not be described as bitwise portable reference identity. Literal reviewed dependency hashes prevent fresh replay silently blessing changed constitutive/reference code.

Run only Python:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/bmar5496/code/constitutive-atlas python3 /private/tmp/atlas-gis-integration-review-20261031-v1/audit_runner.py
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/bmar5496/code/constitutive-atlas python3 -m tools.verify_gis2024_paths /private/tmp/atlas-gis-path-integration-20261031-v1/wasm.json

Retained observations.json, postfix-observations.json and wasm-reassessment.json pin the reviewed artifacts. No claims about binary provenance beyond the reported/hash-bound supplied artifacts are inferred. The review did not rerun the binaries.

## Remaining gates

- Separate finite-path boundary/origin/saturation policy and demonstrable solver behavior; do not infer this from interior paths.
- Wider stress/density/amplitude/parameter/path-duration coverage, including genuine within-segment branch changes.
- Source preparation protocol, independent physical validation and experimental comparisons.
- Scientific/public model admission and appropriate paper/website status remain separate decisions.

## Recovery archive post-fix

The latest Wasm report now retains recovery_control and three recovery_responses (after budget/domain/zero). Current tools/verify_gis2024_paths.py binds the control to the actual selected first tight trajectory call, validates each response using the normal contract, and requires exact request/response equality for all recoveries. Fresh Python verification passes all20trajectories/204updates plus these recovery transcripts. The earlier archive-only gap is closed for this evidence. This does not independently prove runtime temporal ordering; that remains supported by the pinned Node runner and its executed report.

## Repository archive adaptation

The parent adapted audit_runner.py to find the adjacent retained native.json and source-bound reference receipt. The separate raw JSON duplicates are not required: all parsed request/response records are retained in native.json. Archived numerical assessment is recomputed rather than compared bitwise to a historical summary. Historical observations retain original private staging paths as provenance. Reproduce from the repository root with:

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 catalogue/investigations/gis2024-integration-v1/independent-review/audit_runner.py

Alternatively use PYTHONPATH=. with the runner file path. Native/Wasm binary execution is unnecessary for this archive audit.
