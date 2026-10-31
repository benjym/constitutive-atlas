# Checked symmetric matrix exponential

The expression language now accepts `expm(A)` for a dimensionless symmetric second-order tensor and returns the dimensionless symmetric matrix exponential. Mandel order is `[xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz]`. Scalar `exp` retains its scalar meaning. This resolves an algebra requirement of the [2017 clay barodesy candidate](reviews/barodesy-clay-2017-source-packet.md); it does not admit a new scientific model.

## Algorithm and support

Version `symmetric-expm-taylor18-frobenius64-v1` decodes the six components into a Cartesian symmetric 3×3 matrix. It scales by an integer power of two until the Cartesian infinity norm is at most 1/2, evaluates the degree-18 Taylor polynomial by descending Horner recurrence, then squares back. Private full matrix multiplication preserves noncommuting derivative terms. Averaging paired offdiagonal entries after each product suppresses floating-point asymmetry. No spectral decomposition, eigenvalue-gap division, clipping or isotropic shortcut is used.

The mathematical exponential is defined for every finite symmetric matrix. This implementation deliberately supports inputs whose **computed** Mandel Frobenius norm, accumulated by sequential binary64 `hypot`, is at most 64. Inputs above that bound are rejected. Acceptance near the boundary can differ with rounding, component order, orientation or platform; exact frame-independent boundary acceptance is not established. This implementation bound must be distinguished from a constitutive law's physical admissibility domain.

Every input, product, accumulation, polynomial stage, squaring and output must be finite. C++ checks values and all 38 available Jet derivative slots. Finite derivative seeds may still cause intermediate overflow, which produces checked failure. `tensor_expm_checked(A, out)` leaves `out` untouched on failure and supports input/output aliasing. It computes the full Fréchet derivative through ordinary Jet arithmetic, including all offdiagonal directions at repeated eigenvalues.

Results have a normwise accuracy contract with an absolute floor. Small components and small spectral modes are not guaranteed high relative accuracy. Subnormal contributions may round away. Computed positive definiteness, inverse/logarithm accuracy, correct rounding and a rigorous worst-case error bound are not claimed.

## Expression and transaction semantics

The ordinary compiler uses a sticky evaluation-success flag. A failed evaluated `expm` remains a failure even when multiplied by zero, masked by a later comparison, or followed by a successful call. Only the selected arm of `select` executes. Derived expressions are eager; unsupported arguments must therefore be protected inside a lazy expression, rather than by a later domain condition.

Checked failure is supported in derived terms, domain/initial checks, equations, observables, increment-reset guards and values, and the separate transactional history compiler. History failures retain the original values, generation, preparation epoch and event sequence. Failed material updates and failed replay linearizations retain the parent state and expose no usable tangent.

`expm` is rejected in state/observable scale expressions: those existing scale callbacks have no checked-failure return channel. The internal flag identifier `atlas_eval_ok` is reserved. Physical-time expressions preserve their dimensional stage-time/rate types; normalized path coordinates are not reinterpreted as seconds.

## Verification

The [independent Decimal reference](design/symmetric-expm-decimal-reference.md) uses a forward adaptive power series, differentiated term recurrence, a different scaling threshold of 1/8 and precision refinement from 100 to 160 digits. It imports no Atlas kernel. Its corpus treats the actual supplied binary64 input as authoritative, including rounded rotations.

The retained [study packet](../catalogue/investigations/symmetric-expm-v1/manifest.json) contains native and Wasm request/response transcripts for 44 matrices. Each compares all six outputs and all 36 Jacobian entries both through the primitive and a generated model expression. Cases include zero/isotropic matrices, repeated and nearly repeated spectra, offdiagonal and rotated matrices, scaling thresholds and the supported endpoints. Fresh 160-digit replay gives worst scaled errors of approximately `8.99e-15` for values and Jacobians, below predeclared normwise budgets of `2e-13` and `1e-12`. Native/Wasm maximum scaled difference is approximately `1.02e-16`.

Each call also checks 29 named expression/transaction contexts, including derivative-only failure, aliasing, sticky failure, lazy branches, reset rollback, history rollback/recovery and a common-engine accepted-partition tangent recurrence. There are 23 invalid range/parser probes per backend. Wasm executes them in one module instance and repeats the valid control after every failure. CSV parser rejection of subnormal ERANGE inputs is a harness restriction, separate from primitive support. Supplementary Python tests exercise signed zero, subnormals, every input channel, computed-boundary behavior and 80 deterministic matrices near norm 63.

Reproduce with serial isolated builds:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target atlas_expm_probe --parallel 1
python tools/expm_study.py --binary build/atlas_expm_probe --output /tmp/expm-native.json
emcmake cmake -S . -B build-wasm -DCMAKE_BUILD_TYPE=Release
cmake --build build-wasm --target atlas_expm_probe --parallel 1
node tools/test_expm_wasm.mjs --native-report /tmp/expm-native.json --wasm build-wasm/expm-fixtures.js --output /tmp/expm-wasm.json
python tools/expm_study.py --verify /tmp/expm-wasm.json --native-report /tmp/expm-native.json
python -m unittest tests.test_symmetric_expm tests.test_reference_symmetric_expm tests.test_expm_study tests.test_expm_supplementary -v
```

The isolated synthetic catalogues are not packaged as public constitutive models. Barodesy still needs source-declared zero/hydrostatic branches, body/appendix variant selection, full instantaneous rates and integration/reference evidence. The [implementation checklist](models/barodesy2017-implementation-checklist.md) specifies those next gates.
