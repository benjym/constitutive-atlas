# Reproducible software baseline

BASE-01 records a committed software snapshot with build and numerical-check provenance. It does not constitute an independently reviewed model collection or a scientific release.

## Capture

Use Python 3.12 or later, CMake, a C++20 compiler, Node.js and Emscripten. The first capture records the exact installed versions; the project CI currently pins Emscripten 6.0.8. Commit the baseline controller before running it, then use a new destination:

```sh
python3 tools/capture_baseline.py --ref HEAD --output catalogue/baselines/2026-10-30
```

The controller resolves the full commit and tree IDs, exports that revision with `git archive`, and builds in a fresh temporary directory with a separate Emscripten cache. It does not build from the shared working tree, copy ignored datasets, include untracked files or reuse existing build products. To prevent a newer controller from silently redefining an older run, its two source files must match the target revision. Check out the target revision before reproducing a historical baseline.

The destination must not exist. A record has its own run ID and is never overwritten by capture. Failed commands retain their logs and a failed manifest; the runner exits unsuccessfully. A setup failure before export/inventory creation can leave an incomplete failure record that does not pass integrity verification.

## Retained evidence

`manifest.json` records the full source commit/tree, run identity/time, platform, Python/Node/CMake/Emscripten and actual native compiler versions, selected native/Wasm CMake configuration and flags, source-pinned compiler/engine/language identity, supported model-schema versions, and explicit limitations. Independent semantic versions for the engine, compiler and language remain an open representation task; the manifest does not invent them.

The manifest links a SHA-256 inventory of every exported source file, the three generated catalogue hashes and per-model source hashes. The scopes are deliberately separate: public definitions, synthetic temporal fixtures and the restricted Terracotta research catalogue. Native executables and Wasm modules/wrappers are hashed as build products; those binaries are rebuilt rather than committed.

The required ordered check suite is:

1. Public model structural/semantic validation.
2. Fresh native configuration/build and verbose CTest execution, retaining named test results.
3. The 29-case Cartesian elasticity oracle and integrity verification of its historical evidence record.
4. Fresh Emscripten configuration/build.
5. Browser experimental-import unit checks, public native/Wasm parity, temporal-fixture parity, ordered-schedule parity and Terracotta research-reference parity.
6. Website packaging and explicit equality of native/Wasm/packaged public definitions, catalogue metadata and public executable identities.

Each check retains its exact argument vector, exit status, duration and hashed combined stdout/stderr log. The new elasticity results retain full inputs, expected/actual states and tolerances. No third-party experimental archive is downloaded or bundled by the baseline controller. Experimental accuracy, data rights, manuscript generation, literature coverage and independent scientific review remain separate gates.

## Verify and reproduce

```sh
python3 tools/capture_baseline.py --verify catalogue/baselines/2026-10-30/manifest.json
```

Verification reads files only; it never executes commands obtained from a manifest. It checks retained artifact hashes, unique source paths, model/inventory consistency, required catalogue and toolchain identities, and that a passing record has every successful check in order plus a passing analytical report. It is an integrity/consistency check, not cryptographic authorship or independent mathematical review. Historical binaries are identified by their hashes; the verifier does not claim to reconstruct an absent binary.

For a rerun, use the source commit in the manifest and a new output directory. Match the recorded tools and configuration for the closest reproduction; inspect numerical acceptance criteria and case outcomes across platforms. Temporary path prefixes, timing, timestamps and binary bytes can legitimately differ. Do not edit an old report or its hash to represent a changed result: create a new baseline run.

The existing elasticity evidence remains a historical, source-pinned report. `atlas.cli evidence --current` checks its declared source-file scope; a baseline supplies separate fresh-build evidence for the entire exported snapshot. Neither workflow promotes the model's review status.
