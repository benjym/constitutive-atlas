# Corrected J2 backward-Euler qualification v2

The exact corrected model is
`a28068cbb8cfc660e49eb648d6ce7fcbf993ea50b45e8eb0d325c6b75f4ffc3b`.
The [signed trial consistency correction](../CORRECTION-v2.md) removes the
reversed-stress root found by the independent reviewer. The first candidate and
all its numerical successes remain separately retained as scientifically
rejected evidence. No shared compiler, schema, C++ solver or handwritten model
kernel was changed.

The [prospective plan](PLAN.md), 97-input [source freeze](execution-freeze.json)
and project-only source archive precede the fresh native and Wasm builds. Both
serial single-target Release builds completed. AppleClang21 and Emscripten6.0.8
toolchains, artifact hashes and commands are recorded in build-receipt.json.
Raw source originals remain private under the source receipts. The Wasm cache
was copied to private writable storage before configuring, so no protected
shared-cache write or endpoint-protection bypass was required.

Each backend passes 115 independent-reference cases / 230 calls at the unchanged
v1 limits: stress error <=0.002 Pa, history <=2e-10, strict-branch stress tangent
<=0.2 Pa and history tangent <=2e-8. The worst main-study stress error is
1.361e-9 Pa. Every success uses exactly one unsubdivided BE step. Cases include
all tensor components, hydrostatic/tensile/compressive pressure, three hardening
choices including H=0, zero/yield holds, reversal, nonproportional changes,
nonzero history, malformed/overstressed states, forced failure/full-layout
rollback, same-module recovery, and complete two8x6update tangents. Identical
requests replay exactly per backend; both independently satisfy the reference
and physical parity limits. These are named mathematical increment checks,
not an exact continuous nonproportional-path claim.

The frozen paths.json/check_paths.py additionally propagate actual accepted
endpoints through the two loading histories, twice each:54calls/backend.
All27increments satisfy the original stress/history bounds and exact repeat
replay. The [examples](../../../../examples/j2/README.md) run these histories
with the common native CLI and explicit parameters/state/settings.

A separate default-study freeze precedes16additional cases /32calls/backend
at the model's illustrative default parameters, with the same original physical
budgets. This supplements the lower-stress main study rather than changing its
cases or limits. The maximum default stress error is1.431e-6Pa and maximum
stress-tangent error0.008834Pa; history error is below1e-17. Full parameter
bounds remain unqualified. The independent v2 review checks these results and
the complete saved request metadata separately from the parent assessor.

Reproduce assessments without compiling:

```sh
python3 -B tools/study_j2.py assess docs/ingestion/j2-linear-hardening/execution-v2/native-raw.json
python3 -B tools/study_j2.py assess docs/ingestion/j2-linear-hardening/execution-v2/wasm-raw.json
python3 -B tools/study_j2.py parity docs/ingestion/j2-linear-hardening/execution-v2/native-raw.json docs/ingestion/j2-linear-hardening/execution-v2/wasm-raw.json
python3 -B docs/ingestion/j2-linear-hardening/execution-v2/check_paths.py assess docs/ingestion/j2-linear-hardening/execution-v2/native-paths-raw.json
python3 -B docs/ingestion/j2-linear-hardening/execution-v2/check_paths.py assess docs/ingestion/j2-linear-hardening/execution-v2/wasm-paths-raw.json
python3 -B docs/ingestion/j2-linear-hardening/execution-v2/check_defaults.py assess docs/ingestion/j2-linear-hardening/execution-v2/native-default-raw.json
python3 -B docs/ingestion/j2-linear-hardening/execution-v2/check_defaults.py assess docs/ingestion/j2-linear-hardening/execution-v2/wasm-default-raw.json
python3 -B -m unittest tests.test_j2 -v
```

Seven source/analytical/integrity test groups pass, including the exact rejected
root and four manufactured raw-output corruptions. An early pre-freeze assertion
used an arbitrary excessive magnitude for the nonzero bad-root residual; its
failure and exact-formula correction are retained, without altering numerical
acceptance limits. Source completeness, automated technical review, bounded
project admission and experimental validation remain separate. Human scientific
signature, physical calibration/validation, finite rotations, pore-pressure
coupling, stress-control protocols, continuous-path refinement, nonsmooth
tangents, public-browser packaging and whole-envelope robustness are not supplied.
