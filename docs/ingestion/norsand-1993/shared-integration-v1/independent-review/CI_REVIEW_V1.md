# Independent controlled-path CI static review

Task `CI-controlled-path-target-v1`; reviewer `/root/norsand_path_review`,
2026-11-01. Reviewed the new `.github/workflows/controlled-path.yml` only;
performed no workflow execution, remote action, build or compiled candidate call.

**Accepted for static CI configuration scope.** No blocking static finding
remains. Actual GitHub execution, Linux toolchain compatibility and SDK
installation success remain unobserved; this decision is not a CI pass receipt.

The workflow runs the selected Python contract/formulation/state tests, then
builds the durable native Debug target and checks its 58 frozen requests before
installing the selected Emscripten 6.0.8 SDK and building the Wasm Debug target.
Both builds name only `atlas_path_capability` with `--parallel 1`. Model paths
select the same research candidate and two analytical fixtures as the accepted
durable-target study. Generator ordering preserves the frozen request indices.
Linux `.so` and Wasm `.mjs`/`.wasm` paths match the CMake target definitions.

Native and Wasm runs use the same retained request file and runners, and the
unchanged strict checker evaluates both outputs together. The workflow adds no
material-specific formula, tolerance adjustment, publication, deployment or
remote scientific approval. Repository content permissions are read-only.

Always-run artifact upload retains result JSON, generated metadata/equations/API,
both CMake caches and the compiled native/Wasm artifacts. This resolves the
initial retention omission: exact library/module/binary hashes recorded by the
runners can be checked against the uploaded binaries. The existing Python
native opt-in skips remain disclosed in separate local unit evidence; these
workflow unit tests must not be described as executing those skipped tests.

Exact workflow, durable target, requests/runners/checker and this report are
bound in `ci-review-bindings-v1.json`. This is separate from the accepted local
durable-target numerical evidence and from E5/browser/live delivery decisions.
