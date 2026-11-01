# Independent Maxwell browser transport review

Run: `/root/maxwell_checklist_review`; date: 2026-11-01. Separate reviewer of the transport implementation; I did not author it or its tests. This is a bounded transport review, not renewed scientific approval, current engine qualification, packaged-browser verification or deployment approval.

Decision: accepted for the prospective `atlas-contract-v1/PLAN.md` transport scope after the three findings below were resolved. No unresolved blocking finding in the inspected transport contract. Exact implementation, tests, common ABI, presets, saved responses and review output hashes are in `receipt.json`.

## Findings and closure

1. Exact result shape: the initial `verifyResult` accepted an unknown top-level field and an unknown point field; both also survived export/import. This contradicted the prospective exact-field requirement. The coordinator added exact result/point key checks against the common ABI and durable mutation tests. I read the corrected checks and independently verified both mutations reject.
2. Sparse direct-call strain-rate arrays: the initial `forEach` skipped deleted components. The coordinator uses `Array.from` to expose holes and added a sparse-rate mutation. My independent probe verifies rejection. The parameter/state/strain vectors likewise use `Array.from` so direct-call tensor holes are rejected.
3. Restart fixture coverage: the initial durable tests covered only main raw responses. The coordinator added both transaction raw files and explicitly checks restart start times 4 and 8 seconds. I independently validated all eight restart calls, including complete initial state/strain/rate, request encoding, export/import and full replay.

The parent retains initial and intermediate test logs in the enclosing packet. These findings are not relabeled as having passed initially; this decision applies to the final hashed files.

## Assessment

Strict parsing first applies native JSON grammar, then rejects duplicate decoded property names at every object nesting level, nonfinite numeric overflow and lossy plain integer tokens. Quoted text cannot create false numeric tokens. Decimal/exponent tokens retain native binary64 semantics, consistent with the existing strict-JSON policy. Controls require complete exact fields, finite six-component initial stresses/strains/rates, positive machine-bounded material inputs, fixed solver settings, safe unique IDs, 1–100 segments, 1–200 samples/segment and 1000 total samples. Endpoint/sample representability is checked before dispatch. Input bounds do not imply numerical qualification.

The 15 ABI arguments match `cpp/main.cpp::atlas_run_schedule`: seven strings and eight numeric values; every segment contributes duration, sample count and six quantity/kind/value triples. Hold values serialize as zero and rate values stay explicit. No target controls enter this restricted interface. Sampling uses the same start-plus-duration-times-fraction expression and final endpoint rule as `schedule.hpp`.

Successful responses require exact model/catalogue identity, all echoed controls/units/settings, exact sample/event sequence and complete six-component stress state, stress observable, strain and rate histories. Initial state/strain/rate equal the request. Transition state and accumulated strain stay continuous. Only stress-controlled components at right transitions are null rates; finite values remain required for all other components. Returned diagnostic counters are safe nonnegative integers and residuals finite nonnegative numbers. This is transport validation, not a newly imposed numerical error gate.

All four presets are checked against unchanged source example JSON with fixed solver defaults expanded. The prepared oedometer state and its mixed transition nulls are retained. Tests cover both backends and repeated calls, and explicitly reject deliberately coarse settings and unsuccessful schedules. The complete ordered response, including unplotted tensor components and diagnostics, participates in deterministic replay equality.

Import requires exact package provenance equality to the trusted identity supplied by its caller, exact envelope/request keys, and ABI arguments reconstructed from explicit controls. Identity authentication and actual engine/package acquisition belong to the future worker/controller. Structural import alone cannot authenticate arbitrary finite numerical values: actual replay/reference qualification remains required. The enclosing README states that limit correctly.

## Checks and next action

`node check.mjs` (from this directory, or use its repository-relative path) independently checks 32 successful saved responses, eight restarts, all 15 ABI arguments, full export/import/replay, strict-JSON rejections and the resolved shape/sparse mutations. No compiled engine is loaded. `check.stdout.json` reports pass.

`node --test tests/test_maxwell_atlas_contract.mjs tests/test_sls_laboratory_contract.mjs tests/test_timed_route.mjs` passes all 14 groups in `tests.log`. Builds and compiled/material calls: zero.

Coordinator may integrate this exact transport-only contract. Main-atlas routing, worker/controller identity validation, packaging, fresh native/Wasm qualification and actual browser/replay operation remain separate open delivery work. The existing scientific approval and its energy/domain/rollback exclusions are unchanged. No implementation edits, staging, commits or remote actions were performed by this reviewer.
