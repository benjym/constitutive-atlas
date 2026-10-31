# Symmetric expm kernel review

Read-only review of installed Python/C++ operator and the separate Decimal oracle. No authoritative edits, native/Wasm calls or builds. Mathematical/AD review is not scientific model admission.

## Outcome

No blocking mathematical or derivative-propagation issue identified within the declared computed-Frobenius64 support. The four supplementary tests pass, as do all14installed Python operator/reference groups. C++/Wasm behavior was inspected, not executed in this lane.

## Algorithm and derivative checks

- `atlas/symmetric_expm.py:35–39` and `cpp/include/atlas/expm.hpp:43–56` implement P18(B)=sum(B^k/k!,k=0..18) by descending Horner recurrence, then scaling/squaring. The Horner index/order is correct. Row-norm scaling to<=.5 keeps truncation small; the independent oracle uses a forward adaptive series,100/160digits and a different1/8scaling policy.
- Cartesian decoding correctly divides Mandel shears by sqrt2 and output mapping multiplies by sqrt2. A six-component entrywise exponential is not used.
- Private full3×3products retain noncommuting derivative terms. With Jet arithmetic, polynomial differentiation gives the Fréchet derivative; squaring gives XL+LX. Symmetrization acts on values and all derivative channels. In exact arithmetic the polynomial and its directional derivative are symmetric for symmetric A,H, so this adds no mathematical projection to the intended function.
- There is no eigenvector/eigenvalue-gap computation and no special isotropic branch that would lose off-diagonal sensitivities. Exact repeated and nearly repeated spectra are handled by the same analytic polynomial graph. The retained oracle independently tests diagonal divided differences, isotropic derivative in all six directions and pure-shear closed form.
- `cpp/include/atlas/expm.hpp:29–60` checks inputs, every multiplication accumulation, polynomial step, symmetrization, squaring and final mapping through finite_value. The current `tensor.hpp` finite_value(Jet) checks all38derivative slots. Output assignment occurs only after success, preserving out on failure and alias safety. Sticky evaluation failure cannot be restored by a later successful call. Existing synthetic context tests address compiled failure/cancellation/lazy/rollback channels; native execution remains the parent's verification lane.
- Extra deterministic80matrix Python sample at Frobenius approximately63was compared to independent Decimal100: maximum scaled primal error3.590e−14, below the proposed2e−13normwise gate. This is empirical coverage, not a worst-case certificate.

## Limitations and concrete supplementary cases

1. **Support is computed, not exact.** Sequential hypot at Python lines14–16/C++lines31–33can round differently under component order. A retained example has norms64.00000000000001,64.0,64.0for three permutations, although its exact squared Mandel norm exceeds4096by3.9752058979e−13. This does not violate the documented computed-boundary policy, but means mathematical rotational invariance of the Frobenius norm does not imply identical near-boundary admission on all orientations/backends. Do not call acceptance exactly frame-invariant; do not add clipping. The standalone test characterizes the current computed rule without assuming a platform-independent rounding direction.
2. **Small inputs/subnormals.** Supplementary checks cover signed zero, minimum subnormal,1e−300and1e−16in each of the six channels. Finite outputs and an absolute identity-neighborhood allowance pass. Averaging/shear conversion can lose subnormal-sized entries; no small-component relative-error or correctly-rounded guarantee is established. Native test CSV parsing currently rejects ERANGE results (`tests/expm_driver.cpp`), so a future subnormal C++primitive probe should construct its input directly rather than infer kernel rejection from the CSV harness.
3. **Error interpretation.** Value/Jacobian comparisons are normwise with absolute floors. Near large spectral spread, tiny modes or components can have poor relative accuracy despite a good global metric. Computed positive definiteness or accurate inverse/logarithm is not promised and must not be enforced by eigenvalue clipping. The current tests should not be used to claim such properties.
4. **AD range.** Arbitrary finite derivative seeds can overflow internal arithmetic; the intended finite-intermediate failure policy appropriately rejects these even if a mathematical final cancellation could be finite. Parent must retain all36unit-direction comparisons and derivative-only overflow tests through real native/Wasm paths; this review did not execute those paths.

## Staged artifacts

- `python-probes.json`:80explicit inputs and errors, small-input outputs, computed-boundary example and exact Decimal norm diagnostic.
- `test_expm_supplementary.py`: four reproducible Python-only test groups, imports installed operator plus independent oracle; no repo writes.
- `reviewed-hashes.json`: directly inspected authoritative dependencies and retained oracle hash.

Run supplementary tests with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/bmar5496/code/constitutive-atlas python3 /private/tmp/atlas-expm-kernel-review-20261031-v1/test_expm_supplementary.py -v`. These tests are useful additions/characterizations, not required source-model admission tests.
