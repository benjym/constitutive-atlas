# Exact multiplicity controls and selected extreme derivatives v1

Separate generic capability CAP-spectral-nonsmooth-numeric-v1,2026-11-01. Prospective design; implementation and compiled observations follow independent review and an exact numerical-policy freeze. Existing individual-eigenvalue/projector contracts remain unchanged. No new model-specific kernel or schema profile.

## Exact predicates

Add Boolean single-symmetric-argument DSL functions `principal_max_repeated(A)` and `principal_min_repeated(A)`. They classify the exact symmetric matrix represented by the stored finite binary64 Mandel components, whose Cartesian off-diagonals are stored shear divided by exact sqrt(2). They are not comparisons of rounded eigenvalues, tolerance clusters, or numerical sinks. Units are arbitrary consistent tensor units; Boolean predicates are dimensionless. Both return true at a triple repeat. Every primal and all Jet seeds must be finite before classification. Checked C++ output is unchanged on failure, with normal sticky expression/history failure routing. Their dependencies are forbidden in located reset/history event guards under the existing spectral-control policy; ordinary lazy controls and domain checks are supported.

Let `B=3A-tr(A)I`, represented exactly in the same Mandel coordinates. Put `j=tr(B²)/2` and `d=det(B)=r+s*sqrt(2)`. All components, j,r,s are exact dyadic rationals; reuse the existing determinant arithmetic, without floating centering. Its characteristic polynomial is `x³-j*x-d`. The exact discriminant is

```
delta = 4*j³ - 27*d²
      = (4*j³-27*(r²+2*s²)) + (-54*r*s)*sqrt(2).
```

Because rational1 and sqrt(2) are independent, delta is exactly zero iff both rational coefficients are zero. If j=0, B=0 (real symmetric Frobenius norm), a triple repeat; both predicates true. Otherwise delta=0 identifies exactly one repeated pair. Its eigenvalues are `(u,u,-2u)` with u nonzero. The determinant is `-2u³`: negative means repeated maximum; positive means repeated minimum. Use the existing exact radical-sign operation. If delta is nonzero both predicates false. No approximate tolerance, eigen decomposition, clipping or gap floor is used by these predicates. Mathematical discriminant nonnegativity is not a floating assertion.

## Generic lazy numerical construction

For tensor A, form these expressions inside lazy branches (never eagerly bind a restricted primitive):

```
amax = select(principal_range_le(A,0*p_ref), trace(A)/3,
              select(principal_max_repeated(A), principal_upper_sum(A)/2,
                     principal_max(A)))
amin = select(principal_range_le(A,0*p_ref), trace(A)/3,
              select(principal_min_repeated(A), principal_lower_sum(A)/2,
                     principal_min(A)))
```

`p_ref` here supplies the units of A; it is not an argument or scale for exact multiplicity. At a triple repeat trace/3 is the exact mathematical extreme. At a repeated maximum, half the upper pair sum is the exact maximum; the minimum is isolated. At a repeated minimum the converse holds. Otherwise ordinary simple selected extrema apply. Existing numerical isolation/range/decomposition failures still apply to those selected operations and pair sums. In particular a true but too-small nonzero gap is a reported numerical resolution failure, never merged into a tie or excluded as a physical law domain. Explicit finite-expression overflow remains a reported range failure even where an algebraically different expression might avoid it; the new API does not worsen the existing trace/pair-sum range contract.

For a simple extreme, the Jacobian row is contraction with its rank-one spectral projector. At a repeated extreme of multiplicity m, the selected row is contraction with `P_cluster/m`; at a hydrostat it is `tr(H)/3`. For a maximum, its convex spectral directional derivative is `lambda_max(P_cluster H P_cluster)` on the cluster, and the Clarke subdifferential consists of unit-trace positive semidefinite tensors supported there. `P_cluster/m` is one such tensor: it is the average of rank-one projectors along an orthonormal cluster basis. Minimum follows by sign reversal. Thus the construction selects a rotation-covariant Clarke subgradient for each scalar extreme; it does not supply a unique classical derivative or the nonlinear directional derivative at ties.

Do not infer that arbitrary downstream tensor/scalar compositions of these selected rows form a Clarke generalized Jacobian of the whole composed constitutive residual. For example choosing max and min subgradients independently need not arise along a common distinct-spectrum sequence. The solver receives a declared branch linearization. Smooth-region AD is classical; equality/tie cases expose only that selected linearization. Numerical qualification must assess whether it solves the requested residual rather than promising semismooth convergence from the scalar proof alone.

Under passive orthogonal basis changes, `P_cluster` transforms as a tensor, so the exact construction is covariant. A rounded rotated binary64 Mandel tensor need not retain the exact multiplicity of its unrounded precursor; reference labels must be based on the exact stored matrix, not intended eigenvalues. Test representable exact rotations separately from rounded near-repeat rotations.

## Required prospective execution policy

Freeze exact source closure and independent fixtures before native/Wasm observation. Cover zero/hydrostatic, double max/min, distinct spectra, their coordinate permutations, representable rotated repeated pairs, rounded rotations, one-ULP near ties, extreme scales/subnormals, signed zeros/nonfinite primals/seeds and all38 columns. Independently derive multiplicity via exact characteristic factorization/known exact eigensystems rather than duplicating the discriminator as the only oracle. Test classifier corruption rejection and lazy branch behavior: unselected invalid individual extrema never execute; eager aliases still fail as before. Preserve qualifier/signed-event rejection and all existing primitive gates.

Check numeric composite primals against independent high-precision or exact known spectra; tie derivatives against independent exact cluster projectors and smooth derivatives against existing stored-Mandel references. The directional derivative at a tie is deliberately not the selected row. Include covariance, boundary/tie versus nearby resolved-spectrum behavior, existing unresolved-gap rejection, sticky failures, untouched direct checked outputs and recovery. Generated model/history contexts must use ordinary compiler paths. Native and Wasm serial targets, no edits to existing helper bytes. Final tolerances/corpus/source freeze will be a separate POLICY file before compilation.
