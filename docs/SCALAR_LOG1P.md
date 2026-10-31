# Checked scalar log1p

`log1p(x)` computes the dimensionless scalar natural logarithm of `1+x` using the stable library primitive. It accepts finite `x > -1`, preserves signed zero and tiny inputs, and rejects invalid arguments. The implementation identity is `scalar-log1p-libm-checked-v1`.

Python uses `math.log1p`; C++ uses `std::log1p`. Jet derivatives use direct division `seed/(1+x)` in all 38 channels. Inputs, value and derivatives must be finite. Checked C++ calls preserve the output on failure, including aliasing; the generated material evaluator accumulates a sticky failure flag. Selected branches remain lazy. History calls throw into the existing transaction boundary, preserving the original snapshot and counters on failure. State and observable scale expressions cannot use this checked operator because those callbacks have no failure channel.

## Evidence and reproduction

The [independent reference corpus](../catalogue/investigations/scalar-log1p-reference-v1/log1p.json) retains 38 actual binary64 inputs, including signed zeros, subnormals, tiny values, the next representable value above -1 and the largest finite value. Decimal logarithms at 500 and 650 digits check precision refinement. The independent reference does not call the production primitive.

The [retained study](../catalogue/investigations/checked-log1p-v1/manifest.json) binds core code, fixtures, references and raw responses. Each backend checks all 38 derivative channels, six schema values and 6×38 schema derivatives, with 27 named execution/failure contexts per call. Ten invalid domain/parser requests test rejection; Wasm follows each rejection with a fully assessed control call in the same module.

The predeclared budget is four representable binary64 steps per channel, with exact zero/nonzero identity. Signed-zero identity uses a separate Boolean because JSON can erase the sign. Native maxima are zero steps for values and one for derivatives. Wasm maxima are one for primitive values/derivatives and two for schema values; native/Wasm parity is at most two steps. The schema value is the binary64 expression `1+log1p(x)`, so its reference includes that separate rounded addition. This is bounded numerical evidence for the operator, not scientific validation of a constitutive model.

Build and run one target at a time:

```sh
cmake --build build --target atlas_log1p_probe --parallel 1
python3 -m tools.log1p_study --binary build/atlas_log1p_probe --output /tmp/log1p-native.json
cmake --build build-wasm --target atlas_log1p_probe --parallel 1
node tools/test_log1p_wasm.mjs --native-report /tmp/log1p-native.json --wasm build-wasm/log1p-fixtures.js --output /tmp/log1p-wasm.json
python3 -m tools.log1p_study --report /tmp/log1p-wasm.json --native-report /tmp/log1p-native.json --output /tmp/log1p-assessed.json
```

The [Barodesy implementation checklist](models/barodesy2017-implementation-checklist.md) needs this stable operation near hydrostatic loading. Body/appendix source differences, instantaneous constitutive derivatives, finite paths and scientific admission remain separate gates. No public model is promoted by this operator change.

## Limits

The four-step budget is measured for this corpus and platform pair, not a universal libm error bound. The numerical derivative corpus seeds each of 38 channels with one; fixed additional contexts test large seeds and overflow. The 27 synthetic context checks repeat unchanged on each corpus call. Finite rounded seeded derivatives, including underflow to zero, are accepted by the primitive. The corpus zero/nonzero rule therefore does not imply universal rejection of lost derivative increments. See the [independent review](../catalogue/investigations/checked-log1p-v1/review/REVIEW.md).
