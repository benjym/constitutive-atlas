# Laboratory q observable correction v1

This distinct, prospectively frozen study passes. The [original browser loading study](../browser-loading-provenance-v1/README.md) remains failed:11reported q values at exactly isotropic stored IGS stresses exceeded its strict parity gate. No original failure, reference or threshold was replaced.

The sole production numerical change is a double-only stored-Mandel observable in `stress_observables.hpp`, called by the laboratory response serializer. Pairwise normal differences and scaled hypot avoid cancellation from subtracting a rounded mean. Exactly isotropic stored stresses return positive zero. Constitutive deviators, AD, model definitions, integration and controller calculations are unchanged.

The202-file prospective freeze preceded all new compiled calls. Independent35-case exact-rational references, dual800/1200digit roots and midpoint certificates use the unchanged32u*q+8minsub bound over specified components |value|<=1e300. Both native and Wasm pass35cases, including12exact isotropic zeros. This is bounded evidence, not a guarantee over every finite binary64 tensor.

The unchanged browser checker passes101paired cases/163298numeric comparisons under its original current1e-10 and legacy1e-7 relative-to-max(1,magnitude) limits,90same-instance Wasm export/import replays,90direct legacy backend comparisons and failed-prefix/recovery. Exact before/after comparison covers13650paired output points and382raw API calls. Only point.q and response.elapsed_ms are excluded; all other numeric kinds and binary64 bits, including signedzero, are exact.17legacy numerical/tangent pairs and45model/protocol,4rollback,2rate and6IGS regressions pass.

`assessor-audit/` retains original false-pass witnesses for signedzero/type/nested-q changes and their closures. The final source audit passes28source and4observer-retention checks; preflight passes35ideal probes/101ideal invariance pairs/22negative cases. Assessor output `candidate_calls:0` describes saved-output assessment; actual probe/backend observations are retained in native/, wasm/ and post/ with command receipts and artifact hashes.

Builds were coordinator-owned and serial, one explicit target per command with --parallel1 and EMCC_CORES1. No model admission or deployment follows. Browser packaging and actual UI checks remain separate work.

Replay without executing compiled artifacts:

```sh
python3 -B catalogue/investigations/laboratory-q-cancellation-v1/verify.py
```

Add `--artifacts` to hash the six original local compiled artifacts while they remain available. Frozen scripts retain original private execution paths as provenance; replay assessors resolve archived paths locally. The saved-evidence verifier and this summary were added after observations and are covered by evidence-manifest.json, not the prospective manifest.
