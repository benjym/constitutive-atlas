# DP dilatancy-domain correction — native study v1

The current Drucker–Prager definition adds only `Md <= M` to its declared domain. Parameter boxes already impose M,Md>=0. The source-backed [review](../../../docs/ingestion/drucker-prager/README.md) maps OpenSees0<=rhoBar<=rho to0<=Md<=M and retains a negative-plastic-work witness for the old admitted Md>M regime. Valid-case equations, defaults, integration settings, compiler and solver are unchanged. This is a parameter-domain correction, not scientific model admission or a schema migration.

`previous-definition.json` preserves exact old bytes (SHA d40db28d8de98b7eb8597c90787d16d1f76bac0d145cabb9a5853e86d811650d). A content-addressed copy and additive source-archive maps preserve27 original catalogue document/path/hash bindings; their original documents are unchanged. `archive-inventory.json` pins those references. The old source/initialization packet remains historical and hash-bound to that definition. `formulation-crosswalk.json` carries its complete v0.3 contract forward to this guard revision, without migrating the root's legacy schema.

`prospective-freeze.json` pins327 input files before successful compilation: complete required source closure, candidate definition,83 reference requests, assessor and new permanent regression test. The old73 cases retain their stored independent expectations and original1e-4Pa/1e-9state/1e-9relative budgets. Ten added cases check three invalid parameter combinations (including one binary64 step above Md=M), valid independent requests after each rejection, the retained Md0 tensile-apex failure and recovery, and valid J2/associated boundaries. Expected failures require a nonzero exit, ok=false and exact incoming state. Recovery here means separate CLI requests, not a persistent-process or same-instance claim.

The first freeze in `attempt1/` omitted CMake-referenced test helper sources. Configuration failed and no compilation or model observations occurred. Its complete141-file input freeze and failed configure/build logs are retained. The second freeze includes those helper sources and preserves UTF-8 bytes outside the added guard; acceptance/reference mathematics is unchanged. One explicit native target then built successfully with `--parallel 1`.

`results/report.json` passes83/83 frozen cases. Raw stdout/stderr/return codes are in `results/raw.json`. All original73cases also pass their existing native unittest, and the new parameter rejection/valid-boundary unittest passes. Saved-response reassessment reproduces the report byte-for-byte. No tolerances were relaxed, no failed simulation was dropped, and all source-reference inputs precede compiled observations.

Nine archive corruption/isolation unit tests pass. The broader sibling-binding audit still fails outside this change: `archive-audit.json` compares exact HEAD maps with updated maps and records19 prior failures,15 remaining and zero new failures. Four missing sibling pins in touched map directories were supplied as required by the existing archive contract. This does not claim the historical archive suite is green.

Reproduce the native study in an isolated directory (one target/worker):

```sh
cmake -S catalogue/investigations/dp-dilatancy-domain-v1/source -B /private/tmp/dp-domain-build -DCMAKE_BUILD_TYPE=Debug
cmake --build /private/tmp/dp-domain-build --target atlas_solver --parallel 1
python3 catalogue/investigations/dp-dilatancy-domain-v1/run_study.py --solver /private/tmp/dp-domain-build/atlas_solver --output /private/tmp/dp-domain-results
```

Reassess saved responses without compilation:

```sh
python3 catalogue/investigations/dp-dilatancy-domain-v1/run_study.py --replay catalogue/investigations/dp-dilatancy-domain-v1/results/raw.json --output /private/tmp/dp-domain-replay
```

The build logs and report pin the actual executable and embedded catalogue hashes; no binary is bundled. The new canonical numerical evidence and pending source review describe this revision. Historical failed v1/passing v2 reports retain their old hashes. No generic solver capability, new model or public status promotion was added. Md0 tensile-apex infeasibility remains; parameter restrictions do not prove universal convergence. Wasm/browser packaging, hosted deployment and independent scientific review are not tested or completed by this native study. Nothing was pushed.
