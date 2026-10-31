# Browser loading provenance source audit v1

Bounded source-only pass for AUDIT-browser-loading-provenance-v1. Owned private packet only. No production waveform execution, material API call, native/Wasm execution, build, shared edit or admission claim. Parent must freeze and run the prospective runtime study separately.

## Findings and closures

1. Initial exact-response validator omitted catalogue/schema identity; app rejected only truthy mismatched hashes. Final validator requires explicit nonempty expected catalogue hash, exact response hash and schema_version0.1. App rejects absent/mismatched hashes; worker carries the expected catalogue into the bridge. Export also binds result model/hash. Negative cases cover missing/empty/wrong catalogue and missing/wrong schema.
2. Initial backend runner lacked the POLICY-mandated direct legacy API comparison. Final runner records direct same-engine native/Wasm legacy calls and compares complete parsed responses except elapsed time. Legacy native/Wasm1e-7 parity remains separate from current exact-path1e-10 parity.
3. Initial backend runner overwrote its output. Final runner rejects pre-existing result or raw journal before engine import. Raw C API output is retained before helper validation on both backends.
4. Python freeze/execution preservation relied on assert. Final scripts reject optimized Python before imports/actions. Isolated execution of their first AST node compiled with optimize2 proves immediate refusal; no remainder is executed.
5. Staged build_web.py is proposal source only and has no complete isolated packaging asset tree. Accepted scope: pre-integration tests check package fixture/copy lists; after integration the parent runs the actual repository builder against the frozen-built nine-model engine and records supplemental actual package receipts. This audit does not claim staged packaging can run or has passed.

Original and revised source snapshots preserve findings; final/ pins reviewed closures. `initial-findings.json` documents the first source counterexample recipe. No original production failure was observed because production code was never executed by this worker.

## Source conclusions

Integer phase/quadrant/reflection, exact pi/2 literal, degree23 per-operation recurrence and zero/product-sign rules match the original Fraction/RNE design. Monotonic generation has its own linear-rne-v1 identity and exact final target. target_bits is authoritative; numeric zero sign loss through JSON is allowed while complete generated bits are verified. All arithmetic remains caller loading; frozen C++/compiler/schema/material record bytes equal production and model math/thresholds are unchanged.

0.1 imports explicitly retain legacy selection and reject newer loading metadata. Generated-only0.2 imports regenerate the complete path, reject contradictory producer inputs/bits, bind saved result identity and recompute untrusted saved results. Raw arbitrary paths are outside this contract. Success requires the complete exact point-control sequence; failure permits only its leading committed prefix, including zero points. UI retry uses the selected loading mode. Worker and app both verify exact loading before display/export. Numeric result transport is checked before JSON export loses zero signs.

The source corpus is bound to the original immutable p180 oracle:1080phasecases/9720control bits; all250ramp fixture samples independently reconstructed with Fraction and binary64 rounding. These checks verify fixture provenance, not production waveform output. The prospective production test covers these fixture bits, import/wire/settings negatives and zero/subnormal roundtrips. The backend plan covers101pairs,90same-instance import/export replays, limited-budget failed prefix/recovery, defaults and direct legacy API equality. Those planned gates remain unexecuted in this audit.

## Reproducible source checks

- `python3 -B check_reference_binding.py`: original source SHA pins and9720cyclic/250monotonic fixture binding pass.
- `python3 -B check_final_source.py`:11closure/source checks pass; optimized execution guards tested through first-node-only AST execution.
- `source-closure-checks.json`:8initial identity/UI/source closure checks.
- `source-invariance-checks.json`:C++/compiler/schema/material bytes unchanged; nine-model generated catalogue.

Source-only review cannot establish that a JavaScript engine executes the specified rounding, that actual browser import/UI interactions work, or that compiled controllers succeed. The prospective independent-bit gate and frozen runtime/browser/package studies supply that evidence. No original failed sine gates are replaced or relaxed. Smallest next action: parent pins this packet, freezes all final implementation/reference/policy/test bytes, then runs pure producer checks before any serial compiled study.
