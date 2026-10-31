# Versioned laboratory loading

The browser defaults to caller-generated exact controls. Native and Wasm receive identical cumulative binary64 controls through `atlas_run_controls_with_settings`. This removes backend libm differences in sine-generated loading; it does not change the constitutive equations, material integration, strain-path protocol definitions or physical-time support.

## Browser producer and wire contract

`web/loading.mjs` defines `laboratory-waveform-0.1`: monotonic `linear-rne-v1` and cyclic `cyclic-sine-rne12-v1`. A run has1..5000increments and0..100cycles, at least16increments per nonzero cycle. Amplitude bounds follow the laboratory protocol (0.1strain or1e8Pa for stress control). Controls are cumulative, beginning at positive zero. Zero amplitude produces positive zeros; cyclic exact zero crossings and quarter extrema are explicit. Other cyclic values use integer phase/quadrant reduction and a specified12term sine polynomial with separately rounded ECMAScript binary64 operations. Negative subnormal nonzero products preserve their sign. The producer is a numerical waveform definition, not an exact transcendental sine claim.

Loading metadata contains:

- `version: laboratory-controls-0.1` and `encoding: ieee754-binary64-hex`;
- producer `version`, `algorithm`, `target_bits`, `steps`, `cycles`;
- `controls_bits`, one16lowercase-hex big-endian binary64 encoding per point.

`normalizeLoading` regenerates and checks every control bit from the producer declaration. `target_bits` preserves the sign of a zero target through ordinary JSON numeric canonicalization. The engine accepts literal paths more generally; this browser version imports only paths matching its declared producer. Absence of loading metadata selects legacy backend waveform semantics; it never silently upgrades an older request.

The exact-control CAPI returns experimental API `experimental-laboratory-controls-0.1` with result schema0.1, complete authoritative control bits and numeric echo, model/parameter/initial identity, protocol, increment count, numerical settings and committed output prefix. It has no legacy target/cycles fields. The browser validates identity, exact control echoes, point-prefix controls and full output length on success. A failed calculation may return an empty or shorter committed prefix; no uncommitted state is plotted. Legacy responses must not contain newer loading/API metadata. The worker and main thread both check returned settings/loading; main-thread response acceptance also requires the current catalogue hash.

## Saved runs and UI behavior

The run envelope version is separate from the engine result schema and model-definition schema:

| Run envelope | Loading semantics | Import behavior |
| --- | --- | --- |
|0.1|Legacy backend ramp/sine|Restore legacy selection and recompute; absent numerical settings receive documented defaults. Reject injected newer loading metadata.|
|0.2|Declared exact browser producer and bit path|Validate producer/bits/result identity, restore current selection and recompute.|

Both envelopes retain the model catalogue hash. Import rejects another catalogue and never displays saved response arrays as computed observations. Recomputed raw engine numeric controls are checked before export; after JSON export, the authoritative bit arrays preserve signed zero even when numeric JSON has canonicalized it. Export includes the exact specification and current computed result. Unknown outer versions/keys and conflicting provenance are rejected. CSV remains a table of plotted response channels; JSON carries loading provenance.

Solver settings expose current/legacy loading selection. Changing it creates a new run under that choice. Import restores its choice, retry preserves it, and Reset returns to the current default. Labels identify loading versions without implying model validation.

## Verification and retained failures

The original [browser study](../catalogue/investigations/browser-loading-provenance-v1/README.md) remains failed. Its strict1e-10parity gate exposed11qserializer differences at exactly isotropic stored IGS tensors. The distinct [observable correction study](../catalogue/investigations/laboratory-q-cancellation-v1/README.md) uses unchanged thresholds and independent35stored-value references; it passes101paired cases and proves all other fields unchanged across382raw calls. No tolerance relaxation or material-law change was used.

Durable checks:

```sh
node tools/test_loading.mjs
node tools/test_browser_loading.mjs build/atlas_solver build-wasm /private/tmp/browser-loading.json
node --test tests/test_web_package.mjs
node tools/test_web_package.mjs --directory web/dist --output /private/tmp/packaged-loading.json
```

The first command checks independent rational-oracle fixtures without material calls. The second uses both compiled backends for every current executable model, including both loading versions,90export/import replays for nine models, direct legacy calls and limited-prefix/recovery. Output files must be fresh to preserve observations. Package checking uses the package's own exact-loading default run for each model. GitHub Actions includes the pure and backend gates before packaging/upload; adding those local workflow commands does not itself publish anything. Browser UI observations and local package results are recorded separately from source/software checks and scientific admission.
