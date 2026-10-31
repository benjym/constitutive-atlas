# Strict saved-observation JSON — Mohr–Coulomb checkpoint correction

FIX-mc-saved-json-v1; 1 November 2026. **The three retained raw-JSON false passes reproduce on the original assessor and reject on a separate revised copy.** No backend observation, model integration or scientific admission follows.

The original replay assessor silently accepted duplicate `ok` keys in replay and rejection responses and an exponent-overflow value in an unused rejection field. Ordinary `json.loads` keeps the last duplicate and converts `1e999` to infinity; `parse_constant` alone does not catch that exponent. Main response parsing and replay/recovery parsing had different policies.

`tools/strict_observation_json.py` now provides one decoder for saved binary64 observations: duplicate keys reject at every depth after string unescaping; constants NaN/infinity and numbers outside finite binary64 range reject wherever they occur. Integer `-0` is retained as floating negative zero for wire comparisons; ordinary integer tokens, boolean flags, signed float zeros, finite limits and subnormal rounding retain their intended types/values. This validates decoding, not response schema, physics, provenance or scientific correctness. Large integer tokens within binary64 range remain Python integers; exact integer representability is not claimed.

The separate `revised/` assessor copies use that decoder for container files, descriptors, paths, physical parity, exports, replays, failures and recoveries. Replay call consumption validates every raw call, including otherwise unused fields and describe output. The [exact delta](changes.patch) changes parsing only; constitutive equations, reference values, acceptance budgets, process-policy assertions and initial-state rules are untouched. `original/` preserves the exact parent checkpoint scripts. The two original private stage directories remain unchanged; this packet does not overwrite their audit or claim their broad tasks complete.

## Reproduction and results

From a checkout, without a solver or build:

```sh
python3 -B docs/reviews/mc-saved-json-v1/replay.py
python3 -B docs/reviews/mc-saved-json-v1/check_paths.py
PYTHONPATH=tests python3 -B -m unittest test_strict_observation_json test_evidence_archives -v
```

- `fixture.json.gz` contains eight exact, checksum-pinned synthetic source-ideal input/journal files from the retained audit fixture. They are manufactured assessor inputs, not measurements or native/Wasm outputs. `fixture-pins.json` identifies their uncompressed bytes. Each replay runs the original/revised Python assessor in a fresh interpreter; it never invokes a solver.
- [Replay results](results.json): the valid frame passes both versions (14 export/import replays, 12 rejection/recovery pairs, 53 raw-call bindings). All three known false passes reproduce on the old version and reject on the revision. The original 18 corruption recipes still reject, as do five additional raw corruptions. Every subprocess return code/stdout/stderr is retained for 27 cases × two revisions.
- [Path results](path-results.json): the revision accepts all 14 source-ideal paths/834 points under the unchanged path gates. It rejects duplicate and overflow raw fields in both path and parity assessors. Self-parity covers 14,178 synthetic scalars; this is decoder/assessor compatibility, **not backend agreement or independent equation verification**. The independent reference remains in its existing canonical packet and is checked against its original manifest hash, not duplicated or modified here.
- Five focused decoder tests cover nested/escaped duplicates, unused-field nonfinite values, huge integers, types, signed zero, minimum subnormals, maximum finite values, underflow, encodings and invalid JSON. Those and fourteen archive tests pass (19 total). No full-project test pass is claimed.

`original-witness-results.json` preserves the original three accepted witnesses. The packet manifest pins all files; the canonical helper/test hashes are recorded separately. Running replay scripts intentionally regenerates result reports, so preserve the current packet before changing its checks. Original numerical studies and their failed outcomes are unchanged.

## Next integration gate

The broader MC browser tasks remain deferred. For any resumption, copy the four revised assessor scripts plus `strict_observation_json.py` into a **new prospective closure**, include the complete pinned source/reference/request catalogue, rerun the original full preflight suite and commission independent final execution/freeze review before any compiled observation. Existing `verify()` prerequisites are deliberately not bypassed in a production CLI; the synthetic harness directly exercises assessor functions and does not certify that missing full closure.

Recommended process signal/error/status consistency and nonempty failure-message checks remain outside this decoding correction. Schema/rejection semantics, raw receipt closure, source accuracy, native/Wasm runs, nine-model regressions, package/browser checks and scientific admission remain separate gates. No new model family, numerical framework, native/Wasm build, material call, root MC installation, push or deployment occurred.
