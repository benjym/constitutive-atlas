# Barodesy 2017 instantaneous rate study

The isolated seven-state body-law model uses the shared schema/compiler/evaluator. Native C++ and persistent-module Wasm pass 111 canonical independent rates, three additional valid stress-scale witnesses and 16 rejection/recovery pairs. The public catalogue still marks the model as a candidate. Source choices and numerical support are described in the [implementation report](../models/barodesy2017-research-rates.md).

## Reference and acceptance

The independent Cartesian oracle imports no production model or DSL. Verification regenerates the complete canonical corpus, source metadata, derived diagnostics and 80/140-digit matrix-exponential results, then reruns 160-digit refinement. The largest 140/160-digit normalized-exponential difference is below 1.7e-129 and rounded rates agree. Scalar constants/loading/density stages remain binary64: this is not an arbitrary-precision whole-law certificate.

The fixed seven-component normwise budget is 2e-13, normalized by max(1, oracle rate norm). Supplementary checks require every independently zero channel to remain zero, void closure within four binary64 representable steps, and each stress-component error within 2e-13 of the source-derived envelope ||sigma|| ||de|| |c3| (|f|+|g|). This envelope can be large near cancellation; no all-component relative-accuracy claim follows.

Native maximum normalized error is 2.6375055313110176e-15; Wasm maximum is 2.667196322363043e-15. Maximum component-envelope error is below 1.4e-15, void closure is exact in this corpus, and native/Wasm primal parity is below 1.2e-15.

## Boundaries and transport

Review found that an invariant determinant identity could admit an indefinite stress through cancellation. The model now uses normalized Cartesian minors with an explicit 64-epsilon interior margin. Actual rounded rank-loss/indefinite tensors are rejected in both backends; safely interior tensors pass at stress scales 1e-50, 1 and 1e50. This is conservative numerical support, not a certified SPD classifier or the full physical source domain.

Other finite rejection cases cover near-K0 directions, zero stress, negative void ratio, loading/deviatoric norm underflow and wrong vector lengths. Every rejection is followed by a bound control response; Wasm retains the same module. Malformed/nonfinite CSV parser conformance remains outside this finite-input corpus.

The isolated C ABI `atlas_barodesy_rate(model, parameters_csv, state_csv, increment_csv)` wraps generated evaluate_model with current=previous. Its response includes exact model/hash/request echoes and either seven finite rates or null. The legacy public API is unchanged. Description must match the full model and parameter order. Native exit status must match strict Boolean success; raw report checkpoints and transport companions survive parse, acceptance and numerical failures.

Artifact bytes are checked during current execution. Historical numerical replay may skip unavailable artifact bytes explicitly, while enforcing artifact structure, pinned source/reference identities and full fresh numerical comparisons. An explicit native transcript location makes Wasm archives relocatable without changing their original SHA binding. Receipts are provenance checks for trusted code, not a defense against malicious executables or a reproducible-build attestation.

## Reproduction

Build targets one at a time with --parallel 1. Then run:

```sh
python3 -m tools.barodesy2017_rate_study --native build/atlas_barodesy_rate_probe --output /tmp/barodesy-native.json
node tools/test_barodesy2017_rates_wasm.mjs --native-report /tmp/barodesy-native.json --wasm build-wasm/barodesy-rates.js --output /tmp/barodesy-wasm.json
python3 -m tools.barodesy2017_rate_study --verify /tmp/barodesy-wasm.json --native-report /tmp/barodesy-native.json
```

The [retained runtime manifest](../../catalogue/investigations/barodesy2017-runtime-v1/manifest.json) binds source, tests, references, build settings and raw evidence. Instantaneous primal success establishes neither finite integration, material derivatives outside the separate bounded AD study, experimental calibration nor scientific/public admission.
