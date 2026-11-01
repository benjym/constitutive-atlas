# Independent Maxwell packaging helper review

Reviewer/run: `/root/maxwell_checklist_review`, 2026-11-01. I did not author the helper or its packaging tests. Decision: **accepted as a source-only packaging prerequisite after three findings were resolved**. No unresolved blocking finding within the prospective helper scope. This accepts neither a real qualified build nor standard-builder/router integration, browser operation, scientific scope expansion or deployment.

## Findings and closure

The three synthetic initial probes each demonstrated an accepted invalid input, despite the original 11-test suite passing. Their original results are retained in `initial-findings.json`.

1. **Canonical approval scope:** the original helper accepted a simultaneously widened approval artifact and matching registry row because it only checked membership, model/status and selected bindings. I demonstrated that changed scope and removed limits passed. Final code additionally compares the entire approval to `approval_entry` generated from the validated canonical review. Durable tests alter scope, limits and experimental status in both approval and registry. My independent probe now rejects the mutation before creating a destination.
2. **Accepted interface review:** the original helper treated the interface receipt as a list of file hashes even when its decision was rejected with unresolved blockers. Final code pins the actual accepted controller-review receipt hash, checks the accepted decision and empty blockers, then verifies the five Maxwell interface files. The current generic router is checksummed separately as planned. My independent rejected-review probe now fails before output.
3. **Module containment:** the original module selection read a maxwell.js symlink outside the build directory even though the other qualification assets used containment checks. Final code reads the selected module through `local_file`; an outside-build symlink rejects. The independent probe and durable unit test use only synthetic temporary files.

These are source/preflight guard fixes. They neither manufacture an independent review of a build nor authorize broader use.

## Guard assessment

The helper requires the canonical agent approval to exist in the registry, validates the exact accepted review/model with `atlas.agent_review`, verifies supporting receipts and preserves the complete generated approval scope and limitations. Model bytes are not rewritten. It freshly generates the single-model catalogue and requires byte equality with the build's generated metadata.

The qualification binding covers the exact model, generated catalogue bytes, selected module, Wasm, current compiler/runtime/schema/model/dedicated-CMake manifest and reference-policy bytes. Qualification and separate accepted review each require exactly all five gates with strict boolean true: native references, Wasm references, transactions, parity and presets. Missing, incomplete, numeric-true, failed, stale or changed receipts reject. Reviewer identity must be nonempty and differ from implementation identity, and its path/hash and same binding must match. Relative paths are contained within the supplied build root.

Those are integrity and completeness checks, not authentication of an agent's actual work. A production build receipt must be generated from real compiled observations and a real separate review of them. The current successful unit fixtures use explicitly synthetic module/Wasm/qualification/reviewer content and never execute it. No actual current-build qualification receipt has been produced by this task. This expected human/agent-process boundary does not call for external signatures or another user approval.

Five Maxwell modules must match the exact accepted controller review; the current generic router is checksummed but is not silently granted a new independent router review. Input data are captured in memory and hashes refer to those exact copied bytes. A final compiled-source/definition preflight rejects drift before destination creation. The package allowlist contains engine artifacts, model/catalogue, canonical approval/review and escaped readable review, qualification/build-review/interface-review receipts, source manifest, identity, interface modules and per-file manifest. No raw private manual, vendor program, experimental array or standalone model page is selected. Main-atlas and source/review links remain present.

The current source manifest deliberately covers atlas Python, C++ headers/sources, schemas, the exact model and dedicated Maxwell CMake definition. Qualification binds this complete selected manifest. Numerical acceptance still uses the unchanged source/reference policy and requires future review of actual retained outputs; matching fingerprints alone are not a numerical test.

## Checks, limits and next action

`python3 -B -m unittest tests.test_maxwell_package tests.test_maxwell.MaxwellReferences -v` passes all 14 tests: 12 packaging tests and two existing source-reference tests. `python3 -B docs/ingestion/maxwell-itasca900/atlas-package-v1/independent-review/check.py` independently confirms rejection of the three initially accepted invalid cases, with destination absence on each failure. Outputs are retained beside this report and bound in `receipt.json`.

Synthetic fixture outputs are temporary and are not real qualification artifacts. No compiled module, Wasm or vendor code was executed; no build, implementation edit, stage/commit or remote operation occurred in this review. No actual web package is approved by these tests.

Coordinator may integrate the exact reviewed helper as a prerequisite. Separate actual native/Wasm qualification and accepted build review must precede production bundling. Standard-builder/router/discovery wiring and actual main-atlas browser tests remain open, including generated Blob-module execution, verified Wasm instantiation, cache/executed-interface identity, import/replay and failure/recovery. Existing scientific approval, parameter/energy/rollback exclusions and independent deployment permissions remain unchanged.
