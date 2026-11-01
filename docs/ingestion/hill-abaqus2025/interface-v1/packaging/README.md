# Guarded Hill main-laboratory package handoff

Task PACKAGE-hill-abaqus2025-v1; agent `/root/hill_interface`; 2026-11-02. Own files are `tools/build_hill_laboratory.py`, `tools/test_hill_package.mjs` and this directory. No shared hooks, scientific approval, builds or compiled execution were performed.

`bundle(dest, build)` in the Python builder first validates the accepted independent agent review and its generated registry approval for the exact final Hill model. It regenerates the dedicated catalogue and requires byte equality with the supplied build. The accepted checklist must explicitly hash-bind `execution-v1/build-receipt.json`, `references.json`, `negative-requests.json` and `POLICY.md`. The supplied `hill.js`, `hill.wasm` and generated catalogue must each match exactly one corresponding artifact digest from that reviewed build receipt. A model ID, fresh metadata or a green build alone cannot substitute for those exact bytes. Checks happen before writing package assets; a nonempty prior Hill package is preserved by rejecting reuse.

The builder copies the ten-parameter/seven-state main-laboratory modules, creates `material-point-hill/`, writes the runtime identity and generates `review.html` with relative links to the laboratory, exact model, approval/checklist, dossier, reviewed build receipt and references. Scope, all-state meaning, lack of experimental validation, source rights and readable primary source hyperlinks are visible. Copyrighted originals are not redistributed. The exact file manifest covers every package file except itself, plus both copied Hill interface modules.

The Node checker verifies the complete expected manifest file set and every digest before module import or Wasm instantiation. It checks the model/approval/checklist/catalogue identities and reviewed receipt bindings, then uses verified Wasm bytes with the common-engine instantiate hook. It runs every frozen reference case and complete states against the existing prospective policy, repeats exact saved-request replay, confirms the public preset, verifies directional coefficient changes affect response, checks all negative requests and same-instance recovery, and repeats the already prospectively defined low-iteration material-failure rollback. Saved result corruption must be rejected. It does not invent a tolerance or change a source/reference/model.

Parent execution after accepted review and registry integration:

```sh
PYTHONPATH=. python3 tools/build_hill_laboratory.py /absolute/site /absolute/hill-wasm-build
node tools/test_hill_package.mjs /absolute/site /absolute/report.json
```

The standard website builder can call `bundle(dest, build)` after constructing the ordinary atlas; the coordinator owns that shared hook and controller registration. These tools do not substitute for actual main-laboratory browser qualification or live verification.

Checks actually performed: Python AST parse; Node syntax check; four pure reviewed-artifact digest guard checks (valid, absent, malformed and ambiguous). `static-checks.json` records success and zero compiled calls. The full package/runtime checks remain unexecuted by this worker pending the accepted review/registry and parent execution handoff. No failed observations were produced in these static checks.
