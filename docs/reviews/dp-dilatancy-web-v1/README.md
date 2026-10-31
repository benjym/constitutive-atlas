# DP dilatancy guard: bounded Wasm and local website check

The existing `Md <= M` guard passes **83/83 unchanged frozen reference cases in
Release Wasm**. All nine packaged model examples pass their 100-increment runs;
all 628 released measurement records pass browser decoding/checksum checks.
This completes WEB-dp-dilatancy-domain-v1 locally. It changes no equation,
parameter default, numerical setting, schema or admission status. No deployment
or push occurred; five hosted models remain the last verified hosted count.

## Scope and evidence

- [Original native study](../../../catalogue/investigations/dp-dilatancy-domain-v1/README.md): exact source closure and all 83 cases reused without copying or changing references/tolerances. Current definition SHA-256 is b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877.
- [Prospective freeze](prospective-freeze.json) pins source, references, collector, web modules and gates before compilation. [Release follow-up](release-prospective-freeze.json) changes only the build profile after the retained Debug trap. Emscripten 6.0.8-git; both builds use only atlas_solver, one worker and EMCC_CORES=1. The unchanged native binary is pinned by the original study; it was not rebuilt.
- [83-case report](results/report.json) checks original analytical budgets and saved-native state parity. Invalid parameters, including one ULP above Md=M, fail with exact initial state and matching native messages. Subsequent valid calls use the same persistent Wasm module. J2/associated boundaries remain valid; Md = 0 tensile-apex infeasibility remains an expected transactional failure.
- [Existing regression log](parity.log): 45 model/protocol pairs,4 increment diagnostic/rollback cases,2 hypoplastic rate cases and6 IGS history increments pass unchanged tests.
- [Package smoke](package-smoke.json):9 models,101 points each. Static checks enforce matching downloadable definitions, schemas, source URLs and project-relative Pages assets. [Experiments](experiments.log) checks all 628 released records; no additional TMD2 data were bundled.
- [Package inventory](package-inventory.json) pins the complete local package, including engine artifacts and data checksums. Generated catalogue SHA-256 matches the native study. Binaries and measurement files are not copied into this report.

The equation panel now renders every model's declared domain as text via the
existing safe element helper. No domain interpreter or model-specific UI rule
was added. Actual IAB observations are retained in ui-valid.txt,
ui-rejected.txt and ui-recovered.txt: DP completes 100 increments; the equation
panel shows Md<=M and primary source hyperlinks; setting Md = 2 with M = 1.2 gives
“invalid run specification”, stops and disables exports; Reset restores Md = 0.2
and a successful 100 increment response. This is a manual spot check, not an
automated UI suite. [Visible domain and sources](ui-domain.png).

## Failures retained

The Debug build completed, but its first DP integration trapped with
`RuntimeError: memory access out of bounds` in evaluate_model<Jet>.
[Debug logs and artifact hashes](debug-attempt/) retain the failed profile.
The underlying cause was not established; Debug Wasm is **not verified**.
One prospectively recorded retry used the repository's established Release
profile, unchanged source/stack configuration/gates, and passed. This is not a
claim that the Debug issue is fixed.

A package smoke check was started before packaging finished and rejected the
missing .nojekyll completion asset. package-premature.log/json retain it.
After the packager exited successfully, the unchanged check passed. No gate
was relaxed. The historical archive suite was not rerun; its15preexisting
sibling-binding failures from the native correction remain open.

## Reproduction

From the repository root, build the frozen source closure serially:

```sh
EMCC_CORES=1 emcmake cmake -S catalogue/investigations/dp-dilatancy-domain-v1/source -B /private/tmp/atlas-dp-web-reproduce -DCMAKE_BUILD_TYPE=Release
EMCC_CORES=1 cmake --build /private/tmp/atlas-dp-web-reproduce --target atlas_solver --parallel 1
node docs/reviews/dp-dilatancy-web-v1/check.mjs "$PWD" /private/tmp/atlas-dp-web-reproduce /private/tmp/atlas-dp-web-reproduce-results
python3 tools/build_web.py --wasm-dir /private/tmp/atlas-dp-web-reproduce --output /private/tmp/atlas-dp-web-package
node tools/test_web_package.mjs --directory /private/tmp/atlas-dp-web-package --output /private/tmp/atlas-dp-web-package-report.json
node tools/test_experiments.mjs --built-assets /private/tmp/atlas-dp-web-package/experiments
```

The exact observed command arguments/environment are in release-command-*.json.
Run `python3 -B docs/reviews/dp-dilatancy-web-v1/verify.py` to verify retained
files and replay the 83 saved responses without a compiler or engine execution.
The optional unchanged tools/test_wasm.mjs regression additionally requires the
native binary from the native study or a separately reproduced serial build.

Independent source/convention/apex review remains pending. No experimental
validation, general convergence, finite-strain, tensile-surface or scientific
admission claim follows from native/Wasm agreement. The next bounded milestone
is scientific review of the existing benchmark/model inputs; no new model or
numerical capability was added here.
