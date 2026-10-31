# Completed Pages artifact check

The current nine-model production package passes the new local pre-upload gate: nine successful default drained-triaxial runs, 101 points each (909 total), complete explicit illustrative states, finite plotted channels, exact initial states, matching numerical settings and the expected runtime catalogue hash. The checker loads the packaged Wasm and packaged `numerics.mjs`, not separate build artifacts.

Static checks pass for unique runtime/catalogue identities, identical downloadable definitions, version-appropriate schema files, HTTP(S) source URLs and linked HTML assets beneath `/constitutive-atlas/`. External source availability is not fetched or established. Eight negative/contract tests cover stale definitions, catalogue disagreement, duplicate IDs, unsafe URLs, missing assets, root-relative links and the legacy schema filename.

The first new-checker run failed before engine execution because it incorrectly assumed all schema filenames contain the version. That failure is preserved in `initial-checker-failure.json`. The corrected checker uses the same v0.1 filename convention as `atlas/model.py`; all numerical inputs and acceptance policies are unchanged. No package/model/engine change or rebuild was needed. `packaged-runs.json` retains every successful specification and response. `package-receipt.json` copies the prior production package hash receipt unchanged; `verification.json` binds this check's sources and results.

CI now runs the package contract tests and completed-package check after `build_web.py`, before Pages upload. Local publication readiness advances; remote CI, push and deployment have not run. The public website remains at five models. These are software smoke checks, not tangent verification, independent equation review, experimental validation or scientific admission.

Reproduce against an equivalent freshly built production package:

```sh
node --test tests/test_web_package.mjs
node tools/test_web_package.mjs --directory /private/tmp/atlas-nine-model-production-web-v1 --output /private/tmp/packaged-laboratory.json
```

The existing 17-case settings/tangent suite also passed against the nine-model production native/Wasm artifacts before this change. Eight focused Python browser/catalogue/clay2005 tests pass. No native or Wasm compilation was performed for this gate.
