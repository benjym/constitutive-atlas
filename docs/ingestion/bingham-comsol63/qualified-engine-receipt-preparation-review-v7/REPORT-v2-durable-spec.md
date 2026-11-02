# Durable spec supplement

Decision: **accepted**, exact source mapping and no-write validation only. Reviewer `/root/bingham_review`, 2026-11-02. REPORT-v1 and its bindings remain unchanged.

Spec `01c42780cd1f2ee08b28dd007375ec2c32772bf6de2b2d70796a57ee0385c06c` preserves all 53 actual input roots, paths and hashes from `048001adf9506ace7f82be5ce5dfc5a9e24348e713dcc8176eb8f184ff0a3197`. Exactly eight review_path values change: native_binary, module_js, module_mjs, wasm, native_metadata, wasm_metadata, native_header and wasm_header. Each uses the distinct canonical `docs/ingestion/bingham-comsol63/qualified-engine-evidence-v5/<role>/<basename>` destination; no other spec fields change. This is the documented durable evidence mapping, with no claim the evidence has already been copied.

Exact production no-write validation independently passes on the durable spec with the same blocked process/output-write guard, all 53 roles, both saved original 136/272/7,771 assessments and parity, zero files written and E5 acceptance false. `DURABLE-DELTA.json` records the comparison; `validate_durable.py` and `durable-validate.log` reproduce validation. The coordinator must copy exact bytes to these evidence destinations and bind them and the staged candidates in final independent E5. No actual evidence copy, candidate assets, installation or scientific acceptance is made here.
