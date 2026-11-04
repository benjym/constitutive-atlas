# Current17 reuse qualification proposal

This source-only successor reuses the already-built current640 ordinary native/Wasm engines. It does not build, claim a historical prebuild freeze, or transfer the old engine qualification. Current runtime qualification remains pending owner handoff, authentic build provenance review, independent source acceptance, and coordinator execution authorization.

`GATES.json` was written before implementation. `derive.py` constructs `collector-reuse.py` from exact original v5 source. Original `source_files`, collection body, transport, interface assertions, replay, and mathematical assessment functions are unchanged. The pair assessor changes only its expected execution-freeze identity. The policy and Wasm CLI are exact original bytes. The extra Transport subclass hashes the actual artifact/Python bindings before and after each call; whole source/reference inventory remains checked before and after collection and during pair assessment. A post-binding error is retained alongside the original exception.

The retained minimal source context has all808 original-scope current files, all seven unchanged gate/reference digests, and all five exact qualified definitions. The original701 physical assessments (including83DP),42 interface rows/87 interface calls, expected negatives, tolerances, full-state/counter comparisons and saved-pair replay remain unchanged. Seventeen embedded models are required without filtering out the five under test.

The distinct reuse handoff records CURRENT source bindings and genuine historical build records separately. The146-file numerical-test source inventory matches145 present files; its absent `tests/test_solver.cpp` is outside the ordinary solver source context. It did not historically pin `cpp/main.cpp`. Solver object dependencies, flags/link commands, generation/configuration records and the genuine owner's exact640 clean-source retention evidence must close the actual solver provenance. A late source/artifact hash must never be relabelled a historical prebuild hash. A separate accepted exact handoff review decides whether those authentic records establish reuse. Missing claims block execution; this proposal does not silently supply them.

`reuse-provenance.py.txt` specifies the concrete handoff and decision fields. `source_sha256` is the full CURRENT808 map, not a claim that another campaign captured it before its build. `raw_provenance` must retain the original records needed to interpret provenance truthfully; the exact accepted handoff decision binds their containing handoff SHA. Tool/compiler byte identities are prospective checks of the selected retained identities, not a claim of complete installed-toolchain closure. No handoff or accepted decision is fabricated here.

After owner release and exact source/build handoff acceptance, the coordinator may use these commands with NEW outputs outside the source/reference/artifact trees:

```text
python3 -B collector-reuse.py reuse-freeze --repo EXACT_640_MINIMAL_CONTEXT --handoff GENUINE_HANDOFF.json --handoff-sha256 EXACT_SHA --review GENUINE_INDEPENDENT_HANDOFF_DECISION.json --review-sha256 EXACT_SHA --output NEW_REUSE_FREEZE.json
python3 -B collector-reuse.py collect --freeze NEW_REUSE_FREEZE.json --backend native --output NEW_NATIVE_ATTEMPT
python3 -B collector-reuse.py collect --freeze NEW_REUSE_FREEZE.json --backend wasm --output NEW_WASM_ATTEMPT
python3 -B collector-reuse.py assess-pair --native NEW_NATIVE_ATTEMPT --wasm NEW_WASM_ATTEMPT --output NEW_PAIR.json
```

Run backend collection serially under the coordinator's original outer observer/timeout/first-failure/reap/resource policy. Failure attempts and raw calls stay separate and immutable. The existing artifacts are borrowed and must remain retained until consumers finish. No executable, SDK, model-generation or material call was made while authoring this packet. No extra checkout, package or build directory was created.

Reproduce source checks with `python3 -B check_source.py`:40 pure source/manufactured witnesses. The initial fixture failure is retained in `initial-source-check-failure.json`; only its inert second-mutation fixture was corrected. All manufactured temporary files were removed. `source-compatibility.json` is a saved read-only inventory comparison, not runtime evidence.
