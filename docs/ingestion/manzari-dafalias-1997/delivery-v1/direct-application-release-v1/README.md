# Working combined atlas — local release qualification

Manzari–Dafalias1997 original constant-m/first-b_ref variant works in the main atlas laboratory. Exact model SHA-256:28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064. The separate accepted scientific review remains f57edebc6f7c9c5fb4c4f4acb9e8de3f95513093b71daf31c0c9c3ba3c2f0110. Main catalogue:17 definitions;51 reader profiles.

## Actual passing checks

- Serial current17 native and Emscripten builds; smoke;45 scoped native/Wasm cases across17 models and56,931 physical scalar comparisons.
- ci_fast.py:41 Python/66 Node tests,17 definitions and51 profiles.
- check_md1997_numerical_ci.py --build /private/tmp/atlas-md1997-direct-app-v1/native --output /private/tmp/atlas-md1997-direct-app-v1/ci-numerical-v2: expected binary64 diagnostic failure retained; actual native run passes; unchanged external Decimal assessor passes588 comparisons. Raw output/bindings are in ci-numerical/. Local AppleClang21/Python3.14/Node26/Emscripten6.0.8; hosted/Linux/full qualification workflow has not run.
- Exact native fixture-contract check and atlas_recorded CTest pass under explicit-gis20-occ-restart-duncan-sclay1-v6.
- Standard builder stages through Hill pass (package-final-v3.log). That invocation remains FAILED at the historical controlled-time source pin. After separately accepted package-only compatibility fix, the final standard bundle stage was resumed with tools/build_controlled_time_web.py, followed by the unchanged test_controlled_time_package.mjs:8 public histories and2 failure/recovery cases PASS. The builder's final .nojekyll step was completed. No earlier passing numerical stage was skipped or relaxed.
- Full test_supported_package.mjs passes17 ordinary requests and1 registered alternative example; declared unsupported default remains visible. The original failed metadata-membership report and independently reviewed additive format extension are preserved.
- Actual completed-package browser: drained and undrained101-point paths, all14 state entries finite, exact physical import/replay, seven fetched asset hashes equal package bytes, zero console errors/warnings. Only nondeterministic elapsed_ms differs on replay. Desktop plots and390px public-profile viewport visually inspected; no horizontal overflow. Earlier same-app invalid-input/recovery/reset and unsupported-control checks remain retained.

## Scope

Original1997 constant-width Table1 example, fixed-frame infinitesimal effective stress. Qualified monotonic drained/undrained examples are exposed; plastic cycles, stress control and oedometer remain refused. No experimental validation, general parameter-box, noncoaxial plastic or finite-rotation claim.

## Files and release state

package-files.json hashes all1550 completed package files (1,109,256,310 bytes), including the existing994-experiment public dataset. Browser exports/screenshots and actual test reports are retained here. Final site: /private/tmp/atlas-md1997-direct-app-v1/site-v3. Source: /private/tmp/atlas-md1997-current-main-integration-v1/source.

Scoped local release prepared; remote push, hosted CI and live delivery require explicit new authorization under AGENTS.md. The concrete branch is model/md1997-local-qualified-20261105.

Task-owned browser md1997-direct and loopback server8767 are stopped. Four exact redundant copies were removed after verifying retained sources/package:3,242,968bytes reclaimed. cleanup.json lists exact retained locations. Final builds/package/source and unique failed/diagnostic contexts remain for publication and reproducibility; no other agents' resources were touched. Cosmetic whitespace in two exact reviewed/hash-bound files is retained, with git diff --check diagnostic saved.
