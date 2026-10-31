# Algorithm and JSON interface

## Exact stored inputs and spectral reference

Binary64 hex is decoded to its exact rational Fraction. For canonical E,nu, compute `K=E/[3(1−2nu)]`, `G=E/[2(1+nu)]` exactly. The Mandel elastic operator is `K tr(v)I+2G dev(v)`. Compute every trial component `−parent−C loading` and each of38 propagated directions `−dparent−C dloading` exactly before any Decimal rounding. Cartesian off-diagonal components equal stored Mandel shear divided by mathematical sqrt(2).

The copied independent spectral helper solves the centered characteristic cubic. Its stationary points bracket the three real roots, refined by bisection; diagonal matrices use exact coordinate eigenvalues/projectors. This is independent of the candidate cyclic Jacobi algorithm. Isolated projectors are polynomial products over complementary roots. Their derivatives use the spectral reduced resolvent; a repeated complementary pair uses its grouped complement. No differentiation through a numerical eigensolver is performed.

Working precision is the frozen base280 or360 plus the nonnegative extra specified in reference-policy.json. Exact Fraction component complexity and trial exponent span drive that extra, which is especially needed for mixed-scale middle values and near-repeat/projector cancellation. Values are emitted with73 significant decimal digits; construction and all checks use the declared higher precision.

Angles lie in the source interval(0,pi/2). Sine/cosine Taylor recurrences converge with an absolute last-term cutoff10^−(precision+8); beyond their initial terms these alternating series have decreasing term magnitudes. Machin's `16 atan(1/5)−4 atan(1/239)` checks the upper domain endpoint. Cross-precision agreement and derivative/identity checks complement those analytic series properties; this packet does not implement directed-rounding interval arithmetic.

## Physical derivatives

Branch roots and returned principal stresses use the source H0 equations. For each branch, differentiate its affine numerator and positive denominator: `dgamma=(dN−gamma dD)/D`. Differentiate the grouped reconstruction including both principal return values and projectors. Elastic returns the trial directly; face requires every selected eigenvalue simple; left requires isolated minimum and upper-pair sum; right requires isolated maximum and lower-pair sum; apex is `c cot(phi) I` in source signs. Undefined alternatives are explicitly tagged; no eigenvector or tangent is invented at a repeated selected eigenspace.

For38 input columns material coefficients are constant. Return Atlas stress is the negative source tensor; residual is `current−returned_atlas`, hence its derivative is `dcurrent−dreturned_atlas`. Current input is independent of old parent stress and loading. This preserves the distinction between the residual's current-variable Jacobian and the constitutive update tangent.

Separate parameter directions E,nu,c,phi,psi hold current/parent/loading fixed. K/G, sine/cosine, source denominator and eigenprojector chain rules are included. In particular apex Atlas stress has `d/dc=−cot(phi)I`, `d/dphi=+c csc²(phi)I`; E/nu/psi derivatives there are zero. Parameter sensitivities are an independent scientific interface, not a claim that production parameter storage supports Jet seeds.

## Output layout

Each gzip JSON has identity, base_precision, exact input_sha256, columns38, ordered cases and unresolved failures. A case has id, actual working_precision and two explicitly separate interfaces:

- `canonical`: exact stored physical parameters with high-precision trigonometry.
- `resolved_coefficients_diagnostic`: exact frozen binary64 K,G,sf,sd,cf coefficients with c retained; values/branches only. It may report invalid resolved coefficient domain when physical canonical input is valid but rounded sine equals1.

A reference interface contains coefficients, source trial Mandel6, ordered tension-positive eigenvalues/gaps, eigen method, strict selected_branch, classifier guards, branch endpoint distances, natural scales, internal checks and branches.

For each branch, status is `defined` or `undefined-selected-repeated-spectrum`. Undefined branches list required isolated zero-based principal indices (max0,mid1,min2). Defined branches contain source_principal_return, gamma, source_interval_admissible, returned_atlas Mandel6 and residual Mandel6. Canonical branches additionally contain directions[38] and parameter_directions keyed E/nu/c/phi/psi; each entry has returned_atlas Mandel6 and residual Mandel6. The elastic entry includes an unused `matrix:null` placeholder; consumers should use returned_atlas rather than internal construction metadata. Coefficient diagnostic branches explicitly mark derivatives not computed.

Internal checks independently enforce unique source-admissible interval, selected branch's differentiable definition, returned order, selected yield/complementarity, flow subgradient bounds/order/sum and spectral/projector derivative identities. Source flow is recovered from the finite-update relation and tested against the source subdifferential characterization. The reported natural residuals are reference construction diagnostics, not candidate tolerances.

## Interpretation near boundaries

All branch expressions are evaluated independently, including mathematically defined inadmissible alternatives. The high-precision strict source selected label is distinct from a proposed rounded implementation's branch. Boundary ownership follows the source proof, but adjacent fixed-branch derivatives need not match. `check_derivatives.py` finite-differences each fixed branch, never the discontinuously selected map across a branch boundary. Its two steps, columns, representative cases and error gate were frozen before that check.
