# Software baseline runs

The complete initial software baseline is [2026-10-30-r3](2026-10-30-r3/manifest.json), built from source commit `0c3d6dfbcb63715cf95da9d059b963a8d0bbe472` in a fresh exported tree with an empty SDK cache. All fifteen ordered checks passed: 81 Python tests and both native C++ suites, the 29-case elasticity oracle, browser data-import checks, 25 public native/Wasm combinations, five temporal cases, six timed-schedule cases, five Terracotta author-reference histories, website packaging and catalogue consistency. These suites have different scopes; their counts are not a number of independently reviewed models.

| Run | Source commit | Outcome | Interpretation |
| --- | --- | --- | --- |
| [2026-10-30](2026-10-30/manifest.json) | `ffdb92fc8e49` | Failed | Native checks passed; a fresh Emscripten system-library build failed because relative paths were derived through the macOS `/var` alias. The runner now resolves temporary paths before configuring the cache. |
| [2026-10-30-r2](2026-10-30-r2/manifest.json) | `e17ef3f` | Failed | Native/Wasm checks and packaging passed; catalogue recording failed because it assumed filenames equalled model IDs (`clock.json` versus `test-clock`). Source-to-ID mapping is now explicit and tested. |
| [2026-10-30-r3](2026-10-30-r3/manifest.json) | `0c3d6dfbcb63` | Passed | All checks, catalogue recording and artifact-integrity verification passed. |

Failed records and their captured logs are retained. Early runs predate automatic controller-traceback retention, so the second failure's recorder error is explained here rather than represented as a failed numerical test. No original failure record was edited to show success.

See [capture and reproduction instructions](../../docs/SOFTWARE_BASELINE.md). The successful snapshot separates five public definitions, four temporal verification fixtures and one restricted Terracotta research draft. Review, literature coverage, experimental accuracy, data redistribution and manuscript readiness remain separate gates.
