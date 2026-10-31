# Explicit laboratory controls, version 0.1

This additive experimental interface supplies exactly the same cumulative loading values to native and WebAssembly callers. It does not change a constitutive law, the axisymmetric controller, legacy sine generation, browser defaults, or old exports/imports. The retained Mohr–Coulomb cyclic parity failure remains failed; this implementation is not a replacement assessment of that study.

C entry point:

```
atlas_run_controls_with_settings(model, parameters_csv, initial_csv,
                                 protocol, controls_bits_csv, settings_csv)
```

The last two CSV arguments are strings. Parameters, explicit initial state and the six integration settings retain their existing contracts. Empty settings select the reported defaults. The controls wire contains 2..5001 comma-separated **exactly 16 lowercase hexadecimal digits**, one IEEE 754 binary64 bit pattern per cumulative control, most significant digit first. No whitespace, prefix, empty token, trailing comma, NaN or infinity is allowed. The first control must be numeric zero; either sign is accepted and retained. Subnormal finite bit patterns are accepted. A Python producer can encode each double with `struct.pack('>d', x).hex()` and join with commas.

Protocols 0, 1, 2 and 4 consume axial strain change relative to the initial point, bounded in absolute value by 0.1. Protocol 3 consumes deviator stress change in Pa relative to the initial point, bounded in absolute value by 1e8. These retain the original laboratory meanings, including protocol 4 applying the specified strain to all three normal components. The original controller receives the subtraction of consecutive controls in binary64; protocol 3 controls a stress **increment** from the accepted parent, so accepted outer residuals may accumulate. Absolute prescribed-q enforcement is not introduced here. All intermediate increments are also bounded by twice the cumulative limit. Repeated/reversed/nonuniform values are permitted. This interface has no time, cycle count, interpolation or waveform sampling assumption. Scientific suitability and temporal resolution remain the caller's responsibility.

The response retains the existing material/run fields and numerical settings, with additional `api_version: experimental-laboratory-controls-0.1` and `loading: {version: laboratory-controls-0.1, encoding: ieee754-binary64-hex, controls: [...], controls_bits: [...]}`. Numeric controls support plotting; **controls_bits is authoritative for replay and signed zero**. `steps` equals the number of supplied increments; legacy `target` and `cycles` fields are omitted. A successful response has one point per supplied control. A material/control failure retains only the successfully committed prefix; the full input controls remain in loading metadata. Invalid wire input produces the ordinary `{ok:false,message:...}` API failure. No partially parsed input is run.

The native CLI uses `--mode run-controls --laboratory-controls-file FILE`, with model, parameters, initial state, protocol and optional integration settings. The file contains the exact bits CSV (no terminating newline or embedded NUL). The C ABI uses a NUL-terminated string; its terminator is not a wire character. Other modes reject the file option. Run-controls rejects target/steps/cycles and unrelated options. The existing run mode and C API are unchanged.

The response's historical `schema_version: 0.1` is an envelope version, not permission to import it through the existing browser importer. This experimental API is not wired into the browser, and no new browser export/replay claim is made. A future waveform producer needs its own version/identity and prospective reference study. A future browser integration must explicitly handle both legacy and explicit loading identities; it must never silently reinterpret old run specifications.

Binary64 exactness is a caller-input guarantee, not a universal guarantee that constitutive outputs agree bit for bit on every architecture/compiler. The test study records its supported toolchain and checks selected common-input examples; historical numerical gates remain independent.
