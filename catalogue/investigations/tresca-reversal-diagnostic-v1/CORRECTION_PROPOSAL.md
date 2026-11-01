# Proposed correction: certified centered-middle comparison

This is a design proposal, not a runtime change or a passing Tresca qualification.

## Established cause

The actual saved parent and increment generate the diagonal trial deviator
`[10.666666666666668, -5.333333333333334, -5.333333333333334, 0, 0, 0]`.
Its exact stored-input principal range is `16 + 2^-49`, greater than width 16.
The certified range predicate therefore correctly enters plastic branch selection.
Both binary64 expressions `3*vmid` and `trace_trial-width` round to -16, so the
current strict lower-corner comparison is false. The selected face branch asks for
`projector_min` at a repeated minimum. The pinned spectral implementation requires
an isolated selected eigenvalue (`frozen/cpp/include/atlas/numerics/symmetric_spectral.hpp`,
`isolated` and `projector_checked`); it rejects this projector, and the generated
finite-expression guard propagates failure. The same branch is observed in the
real Jet evaluation, which fails before a Newton correction or backtracking.
The raw residual also rejects at an independently admissible physical solution.
This is not evidence of an iteration-budget or feasible-descent stall.

## Generic predicate candidate

Provide a certified Boolean comparison with semantics

`3 * middle_eigenvalue(A) - trace(A) > w`, for a finite symmetric Mandel tensor A
and finite nonnegative w in the same units. The corresponding lower comparison
uses the same predicate on `-A`. Final naming and supported argument contract
belong to a separately claimed design task. Avoid evaluating rounded eigenvalues,
precomputing a rounded centered tensor, or rounding the threshold before the
comparison.

A proof route uses `S = 3*A - trace(A)*I` and `B = S - w*I`, formed in exact
stored-input arithmetic. `trace(S)=0`, `trace(B)=-3w<=0`. The middle eigenvalue of
B is strictly positive exactly when B has two positive eigenvalues. For three
real eigenvalues with nonpositive trace, that is equivalent to

`e2(B) < 0 and det(B) < 0`.

If two eigenvalues are positive, the negative eigenvalue has magnitude at least
their sum, forcing a negative pair sum and determinant. Conversely a negative
determinant permits either three negative eigenvalues or two positive ones;
the negative pair sum excludes the all-negative case. A zero determinant cannot
have two strictly positive eigenvalues with nonpositive trace. Thus equality
remains false, preserving the source's strict branch convention.

Let `J = trace(S*S)/2`; then `e2(B)=3*w*w-J` and
`det(B)=det(S)+J*w-w*w*w`. The existing exact Mandel machinery represents the
required rational/radical expressions, but reuse must be independently verified.
Do not evaluate these polynomials in ordinary binary64. In particular, do not
form `3*A`, `trace(A)`, `3*w`, squares or cubic intermediates in binary64 first:
finite input can overflow or erase the sign being certified.

## Required independent design evidence

- Prove both directions, strict equality, w=0 and repeated-spectrum behavior.
- Confirm exact Mandel factors, determinant radical signs and scale/pressure
  invariance against an independent characteristic-polynomial/Sturm oracle.
- Include this exact reversal and its negation, hydrostatic shifts, all existing
  Tresca branch cases, near face/corner transitions, rotations and noncoaxial
  tensors, extreme finite inputs, subnormal widths and equality cases.
- Specify finite primal/seed rejection, sticky failures, Boolean value-only
  transport, dimensional typing, generated contexts and history consumers.
- Keep the two source comparisons strict; do not replace `<` with `<=` as a
  rounding workaround or silently change selected boundary derivative policies.

Only after that design passes should a distinct generic DSL/runtime capability
be implemented and qualified. A new private Tresca record may then replace its
rounded corner predicates while preserving equations, parameter ranges,
constraints and original budgets. Re-run all original 219 requests/all 38
columns, the 12-step continuous history and the complete 29-request laboratory
corpus with their unchanged gates. Retain all earlier failures. A successful
numerical revision would still require source/formulation review and separate
public activation.
