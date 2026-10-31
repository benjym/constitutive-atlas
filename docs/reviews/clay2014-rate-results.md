# Clay2014 printed-equation fixed-plane instantaneous rates

The [seven-state declarative research variant](../models/clay2014-printed-am-fixed-plane-research.md) passes37 independently evaluated Cartesian rate cases in native C++ and persistent Wasm, plus16 finite rejection/recovery pairs per backend. Each transport has70 responses including the descriptor. The original stress Frobenius and separate void-rate budgets, exact seven-channel zero-loading checks and tighter native/Wasm parity policy were fixed before compiled observations. The largest backend difference consumes0.007245638717652371 of its parity budget. Native stress errors consume at most0.09839406350206506 of the independent-reference budget.

Three material-plane orientations/signs, three pressure scales, mixed/reversed/zero loading, canonical shear and isotropic loading, isotropic anisotropy ratios and a densely rotated companion are included. Both backends run the entire corpus in a single instance; each invalid request is followed by the original control and must reproduce its complete response. Inputs are not silently normalized. This is instantaneous rate recovery, not failed finite-increment rollback or scientific validation.

Source review selected the printed Eq14 Am and proposed Eq49 exponent, replacing both density exponents. It also found printed Am differs from trace(L:I) for general anisotropy. Both values remain explicit; no calibration repair or final-publisher equivalence is claimed. The [source checklist](../models/clay2014-fixed-plane-checklist.md) and [independent model review](clay2014-independent-model.md) locate this discrepancy. AppendixB IGS retains its independent factor4.5 conflict and is excluded. Finite spin, evolving material axes, AD, finite paths, physical preparation, experiments and public model admission remain open.

Native and Wasm builds ran serially, one target and one job at a time. Pre-observation receipts retain source/generated-header/artifact identities; native/Wasm generated headers match. No author source was executed. No remote CI or deployment result is claimed.

The first Wasm raw audit failed because its JSON-digest comparison distinguished integral floats from integers after Node serialization. The [retained negative receipt](../../catalogue/investigations/clay2014-rates-v1/original-wasm-audit-negative.json), original collector, reports and source pins remain unchanged. An additive [reviewed assessor](clay2014-additive-raw-audit.md) uses the original strict numeric identity for opaque parsed JSON: finite0.0/0 equality is accepted, while boolean aliases and changed values reject. All original numerical gates remain unchanged. Eight regressions cover this correction, and29 collector-corruption tests cover full rates, source/raw bindings, exact recovery and artifact mutation. The final assessment binds both original reports, both raw transports and both assessor sources without rewriting a historical source hash.

Reproduce after building only `atlas_clay2014_rate_probe` in native and Wasm build directories:

```sh
python -m tools.clay2014_rate_study --native build/atlas_clay2014_rate_probe --output /tmp/clay-native.json
node tools/test_clay2014_rates_wasm.mjs --native-report /tmp/clay-native.json --wasm build-wasm/clay2014-rates.js --output /tmp/clay-wasm.json
python -m tools.clay2014_rate_assessment --wasm-report /tmp/clay-wasm.json --native-report /tmp/clay-native.json --wasm-transport /tmp/clay-wasm.transport.json --native-transport /tmp/clay-native.transport.json --artifact build-wasm/clay2014-rates.js --output /tmp/clay-assessment.json
```

The original collector's Wasm `--report` audit retains its observed serialization limitation; use the additive assessment command above. Portable archival replay omits `--artifact`; it checks retained byte receipts without claiming to reopen unavailable executables. The optional flag verifies current loader/binary bytes.
