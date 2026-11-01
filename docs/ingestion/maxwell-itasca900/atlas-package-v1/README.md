# Maxwell standard-packaging prerequisite

[build_maxwell_laboratory.py](../../../../tools/build_maxwell_laboratory.py) prepares engine-maxwell and the accepted main-laboratory modules for the standard builder. It creates no standalone page. Shared routing, builder invocation, discovery and workflow remain unchanged until the separately owned integration step.

Before publishing assets, the helper validates the canonical accepted scientific record, requires the exact generated approval_entry and matching registry entry, resolves supporting receipts, and compares a freshly generated single-model catalogue with build metadata. Full canonical approval equality preserves scope, limitations and experimental status, not merely the model hash. It requires the exact accepted controller-review receipt and unchanged five reviewed interface files; the shared router receives its current checksum and later integration review remains required.

## Required real build receipt

The build directory must contain maxwell.js (or maxwell.mjs), maxwell.wasm, generated/models.json, maxwell-qualification.json and its referenced independent review. Qualification schema_version is maxwell-qualified-build-1; model is the exact Maxwell ID, status passed, and implementation_run identifies the actual implementation run. All five gates must be boolean true: native_references, wasm_references, transactions, parity and presets.

Its binding contains model_sha256, catalogue_file_sha256, module_sha256, wasm_sha256, source_manifest_sha256 and reference_policy_sha256. The source manifest captures current Atlas Python, C++ source/headers, schemas, dedicated Maxwell CMake and model. Existing frozen reference-cases.json remains the acceptance policy. The independent_review path/hash resolves within the build directory; that record must be accepted, identify a separate reviewer_run and bind identical gates/identities. These are receipt checks, not external authentication or proof that a scientific review happened. Actual separate-agent review of real retained results remains mandatory; do not synthesize production passing receipts.

Public assets include exact model/approval/scientific review, readable review, qualification/build-review/interface-review, source manifest, package identity and every file hash. Module/build paths are contained. Hashes refer to captured copied bytes; a final source-manifest comparison rejects drift before output publication. The helper does not promise crash-atomic replacement of an existing output directory; use a fresh destination for release construction.

## Evidence

```sh
python3 -B -m unittest tests.test_maxwell_package tests.test_maxwell
```

[Final reviewed output](tests-reviewed.log):14PASS, twelve packaging tests and two existing Maxwell reference checks. Temporary fixture modules/Wasm and review receipts are explicitly synthetic and never executed. Tests check complete public hashes/source links, missing/failed/coercible/incomplete gates, stale engine/catalogue/source/reference, separate review/path/hash, unregistered or jointly widened approval/registry, rejected interface review, altered reviewed interface, module symlink escape and source drift before publication. No native/Wasm build or material call occurred.

Initial/intermediate outputs remain retained. Separate review found three real gaps: canonical approval equality, acceptance of the interface review decision, and module-path containment. All were corrected with durable negative tests. Exact parent [input bindings](inputs.json) and separate review record identify the accepted implementation.

Next: freeze actual current source and unchanged references, obtain prospective review and a serial execution handoff, qualify native then Wasm, retain failures and obtain a real accepted qualification receipt. Then narrowly wire standard packaging/router/discovery, run required package checks and exercise the real main-atlas browser including cache/verified Blob loading. E4/currentE6–E8 remain open; no live, broad-domain or experimental approval follows from these tests.
