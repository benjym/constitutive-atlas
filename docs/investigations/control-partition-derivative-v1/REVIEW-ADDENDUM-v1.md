# Independent design-review response: bounded h-convergence requirement

This additive requirement refines DESIGN.md/POLICY.md before implementation. Earlier frozen files are preserved. Separate reviewer agrees bounded h reduction is the narrow approach and notes that accepted-partition equality does not prove expression/reset branch identity. Because no generic branch-signature diagnostic currently exists, require directional finite-difference convergence as well.

Within the same total budget of11positive probes at h0/2^k, k=0..10, require two consecutive amplitudes h andh/2 whose accepted partitions both match the base partition/affine audit. Form both slopes against the same unchanged base trial. Accept the smaller-h slope only if both are finite and

`abs(d_h-d_half) <= 1e-3*max(abs(d_h),abs(d_half),1 Pa per unit strain)`.

This is a new prospective derivative-stability guard, not a material residual/control acceptance tolerance. The1Pa/strain floor is explicitly dimensional; the controlled stress outputs in both protocols are Pa and their directional inputs are dimensionless strain. Preserve the existing nearzero derivative failure threshold after this check. Do not demand a positive derivative: stable negative slopes can be physically legitimate. If a probe fails/mismatches or its slope is nonfinite, clear the prior comparison candidate. A stability failure may retain the current comparable slope only as the previous value for the next consecutive half-step, never as an accepted derivative. Exhaustion, unrepresentable perturbation or lack of a stable consecutive pair fails the control update with unchanged parent state.

The guard bounds but cannot mathematically guarantee differentiability at every kink. It must not be advertised as a full branch signature or analytic tangent. It limits reliance on a single accidentally comparable probe and directly addresses the reviewer concern without adding replay or AD layers. The maximum call count remains11; two successful comparable probes are needed. The synthetic jump fixture must therefore recover at h0/2andh0/4and use the latter slope, whereas the exact-boundary fixture must fail after11probes.

Additional prospective fixture: smooth analytic constant-lateral-stress elasticity, finite stable directional slope and source analytic root; unavailable consistent probes must roll back, then the same untouched parent must successfully handle a separately feasible control request. All other design/policy limits remain in force.
