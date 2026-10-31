# DSL evolution audit (read-only, 2026-10-31)

Scope: change atlas/dsl.py and append wrappers to tensor.hpp; compiler.py and history_compiler.py remain unchanged. No builds, compiled execution, Git mutation or repository writes in this audit.

Observed current source identities:
- atlas/dsl.py: d98844ee61060aca4ca39198bf261552f29ebc480abcf196cc2e836016e8cb6d
- atlas/compiler.py: 4c7ffb54a59ec2f0ad8afc90e755243ea100d4172790de7ae4466f1e749c9292
- atlas/history_compiler.py: 0747d2e61a5d848a449c47486aad433a8a5de2ef81389883562fd359cf6c7b30

## Runtime contexts still requiring action

1. tests/test_ingestion_packets.py::test_clay2005_v2_independent_guard_review runs docs/ingestion/hypoplastic-clay-2005/guard-review-v2/test_audit.py. Its 4 original groups exact-compare audit.run against results.json and directly hash all reviewed-inputs.json/files, including live dsl.py. No registered existing closure contains this packet. Bounded new closure can start from source-rates-v1/clay-capsule.json plus complete exact guard-review-v2 packet. Preserve all 4 groups and full original result, then wrap the historical assertion; current guard semantics may have a separate check.

2. tests/test_ingestion_packets.py::test_clay2005_additive_source_correction_and_spd_defects executes rate-review-v1/probe.py --check evidence.json and its test_audit.py (4 original groups). probe.run first directly checks reviewed-inputs.json/repository_files, including live dsl.py, before evaluating original two DSL counterexamples. The clay source-rate capsule does not contain this review packet. A separate bounded closure or additive combined reviews closure is necessary. Do not replace direct historical assertion with current hash substitution.

3. tests/test_ingestion_packets.py::test_barodesy2015_oracle_limits_remain_reproducible runs barodesy-sand/rate-review-v1/test_review.py (3 groups). audit.run directly checks reviewed repository dsl.py bytes. The exact review packet IS already present in source-rates-v1/sand-capsule.json and sand-prospective-v1/capsule.json, but their entries do not execute these 3 original review groups. Reuse archived exact bytes in a separately registered entry/capsule; do not mutate existing capsule identity.

4. tests/test_clay2014_rate_evidence.py::test_retained_source_raw_and_numerical_evidence runs tools/clay2014_rate_study.py::verify and tools/clay2014_rate_assessment.py::assess. identity() regenerates source_pins from LIVE files including dsl.py and tensor.hpp, and verify compares whole identity. Archive sidecars cannot repair this runtime assertion. finite-tensor-v1 contains the original rate tools/report dependencies but NOT this test module, and its entry executes only the four finite-study families. Preserve this exact standalone original test group in a bounded new closure (may reuse sources from finite capsule). Note tensor changed already, so restoring pre-tensor bytes from registered finite capsule is necessary; a live-only snapshot now is insufficient.

## Already protected execution contexts

- source-rates-v1 registry sand/clay preserve complete v2 source reports and 11/18 original groups, with old dsl/compiler bytes.
- sand-negative-v1 preserves the original compiled failed report comparison and 6 original groups.
- sand-prospective-v1 preserves original prospective mapping audit and 8 original groups.
- finite-tensor-v1 preserves 89 groups in 11 original modules across isotropic/wider/clay-original-failed/clay-controlled, including old dsl/compiler/tensor.
- transport-audit-v1 preserves preliminary/fixed generic transport witnesses.
- tests/test_source_rate_runtime.py deliberately compares current numerical fields only and checks current runtime hashes; retain as current behavior test, not historical proof.

## Identity-only additional dsl redirects

All of these current source maps currently have NO dsl.py entry. Snapshot exact current dsl.py and add document-bound redirects before mutation, preserving originals. This does not preserve interpreter execution by itself.

- catalogue/investigations/barodesy2017-runtime-v1/manifest.json
- catalogue/investigations/barodesy2017-hydro-ad-v1/manifest.json
- catalogue/investigations/barodesy2017-integration-v1/manifest.json; native.json/source_pins; wasm.json/source_pins
- catalogue/investigations/barodesy2017-wider-integration-v1/manifest.json; native.json/source_pins; wasm.json/source_pins
- catalogue/investigations/clay2014-rates-v1/manifest.json; preobservation-native.json; native.json/source_pins; wasm.json/source_pins
- catalogue/investigations/clay2014-paths-v1/manifest.json; preobservation-source.json; native.json/source_pins; wasm.json/source_pins
- catalogue/investigations/clay2014-controlled-resolution-v1/collection-freeze.json
- catalogue/investigations/checked-log1p-v1/manifest.json (files LIST of path/hash rows); review/verification.json (pins map).

Main live identity consumers: tests/test_barodesy2017_hydro_evidence.py via verify_manifest_files; tests/test_log1p_evidence.py via checked_receipt; tests/test_clay2014_rate_evidence.py (also runtime issue above). Finite family root tests now use capsules. Historical native/wasm source_pins should be preserved regardless of current consumer.

Extending sidecars changes their bytes. Hydro manifest pins the source-map documents for barodesy integration/runtime and checked-log1p. Those originals are ALREADY archived in tensor-identity-v1 secondary bindings; retain their exact objects/redirects. tensor-identity-v1 tests bind document identities and selected objects, so do not overwrite inventory originals casually.

## Review provenance only

These docs pin current dsl.py but no root test currently directly rehashes those pins, except the runtime review contexts above. Keep original reviewed-inputs unchanged and archival resolution explicit if used:
- docs/reviews/tensor-trace-accuracy-v1/reviewed-inputs.json
- docs/reviews/tensor-trace-implementation-v1/reviewed-inputs.json
- docs/reviews/frozen-source-evolution-v1/observed-source-inventory.json
- docs/ingestion/barodesy-sand/{rate-study-v1/manifest.json,rate-study-v2/provenance.json,rate-review-v1/reviewed-inputs.json,compiled-plan-review-v1/reviewed-inputs.json}
- docs/ingestion/hypoplastic-clay-2005/{rate-study-v1/checks.json,rate-study-v2/checks.json,rate-study-v2/manifest.json,rate-review-v1/reviewed-inputs.json,guard-review-v2/reviewed-inputs.json}

Older pre-current DSL versions (5bdb057a..., c5836e4e...) already have source snapshots and sidecars from symmetric-expm/checked-log1p migrations. Compiler/history-compiler need no new archive solely for unchanged bytes; frozen emitted models remain historical artifacts. Fresh generation through changed DSL requires new study identity.

## Suggested smallest sequence

1. Preserve exact current dsl.py bytes once; establish the four missing historical contexts above (reuse existing archived source files where possible).
2. Add identity-only redirects for current dsl receipt set; original source documents and gates unchanged.
3. Implement dsl/tensor candidate and run focused current semantic tests plus registered historical wrappers. Compiler/history_compiler unchanged.
4. New generated DSL/native/Wasm context study with its own prospective policy. A plain C++ ternary/operator result does not establish generated DSL failure propagation.
