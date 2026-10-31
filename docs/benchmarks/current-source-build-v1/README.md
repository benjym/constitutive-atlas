# Current native source/build receipt v1

One clean serial Release build of `atlas_solver` from source commit
`6ff25a9fb01de0fa9360c1bd04149877490319ef` passes the predeclared
[metadata-only policy](protocol.json). This is a current executable with a
traceable source/build receipt for a future separately frozen benchmark.
It does not identify the historical executable or establish engine equivalence.

## Scope and result

- **351 tracked source files** reconstructed from Git, hashed before build and
  unchanged afterward: CMake, Python compiler, C++ engine, models, schemas,
  fixtures and test sources needed by CMake configuration. Untracked paper work,
  experimental data and author binaries are excluded.
- The Python compiler generated the expected catalogue/header before CMake;
  both generated build files match those frozen byte hashes exactly.
- Exactly one native target, `atlas_solver`, built with `--parallel 1`.
  Six commands succeeded, including compiler/catalogue preparation, version
  queries, configure/build and one metadata-only `--describe` call.
- The compiled description equals the pre-build catalogue: **nine public drafts**,
  catalogue identity `0d2e46841e859ca94bd69fff91020a4516b24f2c50c139f61ece5748b00b3fe7`.
- Executable SHA-256:
  `960d6f8ebcc0c3296555dd6e294a3650a5ec2318108d30850216ee5a69e4f574`.
- Apple Clang21.0.0, arm64 Darwin, CMake4.4.3, Python3.14.7;
  Release `-O3 -DNDEBUG`, C++20. Exact cache, compile commands and tool versions
  are retained in [evidence](evidence/result.json). CMake lists other targets
  in its compile database; they were not built by this invocation.
- **Zero material calculations, fits or experimental replays.** Build stderr
  is empty. The process completed normally; no interruption was observed.

[Source manifest](source-manifest.json), [pre-build freeze](evidence/freeze.json),
[command and artifact receipt](evidence/result.json), and
[verification record](verification.txt) retain the source/policy/output binding.
The saved-evidence audit passes; copied corruptions of process returncode,
metadata, source manifest and runner are all rejected. A separate post-build
byte audit checked the original Git blobs, private snapshot, generated files,
executable and journal-helper identity without native execution.

## Reproduce or audit

From this checkout, audit saved evidence without compiling or executing C++:

```sh
python3 docs/benchmarks/current-source-build-v1/verify.py
```

To intentionally reproduce the build, use a new absolute output directory:

```sh
python3 docs/benchmarks/current-source-build-v1/reproduce.py /private/tmp/atlas-current-source-build-replay
```

The runner reconstructs source from the pinned Git commit, requires a fresh
output directory outside the repository, freezes expected bytes before build,
and uses the existing TMD2 command-journaling helper. Follow the repository's
single-build coordination rules. The original private executable/source/build
remain at `/private/tmp/atlas-current-source-build-v1/`; temporary storage is
not durable artifact hosting. Source is recoverable from the named Git commit.

## Limits and next bounded action

The historical VW96 law matches current mathematical fields, but the current
integrator adds endpoint-defect checks; see the
[input review](../kfs-development-checkpoint-v1/input-review.md) and
[historical source/build gap](../kfs-partition-diagnostic-v1/README.md).
Keep all historical reports and the failed refinement gate unchanged.

This receipt is not a hermetic toolchain archive, signed attestation, bitwise
cross-platform reproducibility guarantee, numerical verification or independent
scientific review. It does not promote any model or deploy the website.

Next freeze a small current-versus-archived engine comparison using the same
VW96 law, parameters, initialization and loading requests, with acceptance
criteria declared before observations. Start with a few discriminating paths;
do not rerun the calibration or full factorial campaign automatically. Keep
independent source/scientific review as a separate release gate.
