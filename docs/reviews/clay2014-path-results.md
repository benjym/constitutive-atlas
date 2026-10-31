# Clay2014 finite-path result: retained failed refinement

The frozen fixed-plane printed-Am/proposed-Eq49 study **fails** its predeclared endpoint-refinement requirement in native and Wasm. Each backend completed 24 trajectories, 288 actual chained updates and 295 raw responses. Four of 144 endpoint contraction inequalities fail in each backend, on the seven-caller isotropic reversal path. Original reports, raw companions, failed assessments, pre-observation sources, serial build logs and exact artifact receipts remain unchanged.

The [independent whole-matrix diagnosis](clay2014-path-negative-diagnosis.md) separates the four failures from passing all-caller stress/void/volume accuracy budgets, partition contraction, rotated covariance and after-progress rollback/recovery. The separately assessed native/Wasm state-and-parent comparison has maximum scaled difference 1.234e-16 against its 5e-11 bound. That partial comparison does not grant full parity acceptance while the frozen numerical study fails.

An [independent scalar midpoint replay](clay2014-midpoint-negative-diagnostic.md), without Atlas constitutive or production imports, reproduces the retained hydrostatic states at their actual accepted fractions. Loose and middle tolerances accept the same first-segment partition, so the endpoint error cannot contract there. Unloading also changes error cancellation. This evidence explains the failure without supporting a material-law repair or relaxation of the original gates.

## Reproduce the retained evidence

Run from the repository:

```sh
python3 -B -m unittest discover -s tests -p test_clay2014_path_negative_diagnosis.py -v
python3 -B -m unittest discover -s tests -p test_clay2014_midpoint_diagnostic.py -v
python3 -B -m tools.diagnose_clay2014_paths --output /private/tmp/clay2014-negative-fresh.json
```

Use a fresh output filename. These commands inspect retained observations and replay independent Python references; they do not build or execute native/Wasm artifacts. The portable diagnosis checks artifact identities against retained receipts without requiring binaries in a fresh checkout. Its optional `--check-artifacts` reopens the exact local artifacts; the retained local-artifact diagnosis records the earlier successful byte check.

The original build runner is retained byte-for-byte under `catalogue/investigations/clay2014-paths-v1/build-runner.py` because the command records pin its hash. It is a historical local runner with absolute machine paths, not a portable build entry point. The source-only transport documentation gives the generic build/collection commands. Do not rerun it over the retained directory.

## Next study and remaining gates

A separate prospective controlled-resolution hydrostatic study should predeclare caller-piece subdivision, accepted-fraction checks, analytical references and contraction gates before any new compiled observations. It should test order versus actual resolution; local adaptive tolerances do not guarantee strict global-error contraction at every endpoint. Keep this original failed study immutable. Wider nonisotropic controlled-resolution studies and constitutive derivatives remain separate work.

The exact formulation remains a research variant. Printed Am versus trace(L:I), Appendix B IGS normalization, publisher reconciliation, physical preparation, material-axis transport/spin, experimental validation and independent scientific/public admission remain open. The [source-linked model dossier](../models/clay2014-printed-am-fixed-plane-research.md) defines its current scope. No new public executable or deployment is claimed.

## Integration checks

Seventy focused Python test groups passed (47 path/reference/transport/negative groups, seven scalar diagnostic groups, 14 evidence-export groups and two browser contract groups). The browser contract wrapper also checks JavaScript navigation/rendering behavior and ES-module syntax. Retained-manifest integrity and the real 18-record export pass; the added study exports as failed with its current research definition. No new build, compiled execution, deployment or remote CI occurred during this integration step. Commands and counts are retained in `catalogue/investigations/clay2014-paths-v1/integration-checks.json`.
