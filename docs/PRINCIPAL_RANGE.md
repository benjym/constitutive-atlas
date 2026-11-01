# Exact inclusive principal-range predicate

`principal_range_le(A,Y)` returns a Boolean deciding whether the largest minus smallest eigenvalue of the exact tensor encoded by A is at most Y. A must be a symmetric tensor and Y a scalar with matching units. Mandel order is `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`. Equality, repeated spectra and hydrostatic zero width are included.

All operands must be finite and Y nonnegative. The exact dyadic/radical invariant computation scales and subtracts pressure before any floating invariant arithmetic; it avoids rounded eigenvalues and yield tolerances. The implementation supports Python interpretation, generated model initial/domain checks and lazy branches, and experimental history expressions. Native/Wasm Jets validate all 38 derivative seeds of both operands, but produce no derivative of the Boolean. Event/reset guards reject dependencies on this value-only query, including dependencies hidden in numeric aliases.

For example, an initial check may use `principal_range_le(sigma,2*k)` when sigma and k have stress units. Invalid executed operands fail the evaluation even when a branch result would otherwise conceal failure. Unselected lazy branches are not executed. No supplied state is projected or repaired.

Exactness applies to the finite binary64 operands received by the predicate. Arithmetic used to construct A or Y can already have lost information or overflowed; an overflowing `2*k` still fails as a nonfinite expression. This operation does not certify constitutive integration, selected spectral derivatives, calibration, initialization representability or scientific admission.

[Mathematical proof and independent oracle](reviews/certified-spectral-range-v1/README.md) establish the gap-polynomial decision. [Runtime qualification](reviews/exact-principal-range-runtime-v1/README.md) records the frozen 303-case Python/native/Wasm comparison, nonfinite seed rejection and transaction checks.
