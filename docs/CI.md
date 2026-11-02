# CI and publication

Routine feedback targets five minutes. Full numerical qualification remains a
separate, slower workflow; its equations, references, tolerances and retained
failures have not changed. A cold compiler cache can exceed the feedback target.

## Fast CI

`verify.yml` runs on pushes and pull requests, with a stable final `checks` job.
Superseded runs on the same branch/PR are cancelled.

- Canonical SQLite export checks approval/model/review/supporting-file integrity.
- Model validation, language/initialization/approval unit tests, public profiles
  and JavaScript contracts run without building or executing material studies.
- Code and numerical-input changes also build just the ordinary Linux native and
  Wasm solvers. Four smoke cases check a nonzero elastic increment, a hold,
  independent Hooke-law/void-ratio references, native/Wasm transport agreement,
  an unknown model and malformed strain. These do not replace model qualification.
- Prose/media-only changes skip the compiled job. Unknown files, missing diff
  history, new branches and manual runs require it. Fast contracts always run,
  so documentation edits still receive a terminal status rather than a pending
  path-filtered required check.

The local equivalent of the source/contracts job is:

```sh
python3 -B tools/ci_fast.py
```

After building the two ordinary solvers, the compiled smoke command is:

```sh
node tools/ci_smoke.mjs --native build-ci-native/atlas_solver --wasm build-ci-wasm/atlas.js
```

## Full qualification

`qualification.yml` retains every scientific command from the previous
`verify.yml` at source revision `104161159a6fbed784769e22050ecba0538f669e`:

- Linux/Python 3.12 and macOS/Python 3.14 native checks;
- both Wasm platforms, model-specific studies and native/Wasm parity;
- historical/exact macOS replay, convergence and research studies;
- all existing package guards and the controlled-path/interface qualification.

It runs nightly at 15:17 UTC, manually through **Full qualification**, and for
changes to numerical code, models, schemas, test/build tools, catalogue/data,
workflow configuration, and executable/reference/archive inputs in `docs/`.
Ordinary prose and web-only changes do not request the full scientific matrix.
There is no claim of qualification for a skipped revision.

Controlled-path qualification runs once, independently of the long native/Wasm
jobs. The duplicate standalone controlled-path workflow and redundant manual
macOS workflow are retired; manual full qualification retains their coverage.
Long Wasm shell steps are split into visible timed study/build sections. The
full workflow keeps its native builds and exact build receipts where they are
part of the existing backend qualification; Pages does not repeat them.

## Pages

`pages.yml` follows a successful **Fast CI** run originating from a push to
`main`. PR completions and failures cannot publish. Manual publication is also
restricted to `main`.

It checks out the exact upstream tested SHA, checks the checkout identity, and
passes that SHA to the package builder for release identities. It builds only
the public Wasm engines needed by the site and restores existing approved,
hash-bound model assets with the unchanged provisioning guards. It does not run
the exhaustive native qualification studies or historical replay.

The unchanged standard web builder runs every existing per-model package guard.
The final artifact also passes the ordinary-engine smoke, experiment/package
contracts and supported-input package tests. Only that tested directory is
uploaded and deployed. Publication is serialized and is separate from full
qualification; it does not wait for that nightly/relevant-change matrix.

This is an explicit scheduling change, not new scientific approval. New models
still require their independent approval and delivery checklist. A compiler or
solver change still warrants examining the full qualification result even when
the fast checks have passed.

The publication build is not promised to finish in five minutes: it retains all
package guards and may need cold Wasm builds or approved data downloads.

## Caches and status checks

Fast smoke and publication use compiler-object caches keyed by OS, architecture,
workflow and source inputs, with matching-prefix fallback. They regenerate
catalogues and rerun checks on every run. Generated sites and passing test
results are never cached. All Wasm workflows cache the pinned Emscripten 6.0.8
SDK separately by OS and architecture. Every CMake build remains one explicit
target with `--parallel 1`.

Use **Fast CI / checks** as the routine required check when configuring branch
protection. GitHub reported `main` as unprotected during this change; no remote
repository setting was modified. Full qualification has its own terminal
`result` job. Requiring that result on every PR would retain the long merge gate.

Local syntax validation uses actionlint. Actual GitHub runner timings, cache
hits, publication and the native/Wasm smoke must be confirmed after an
explicitly authorized push; local source checks alone do not establish them.
