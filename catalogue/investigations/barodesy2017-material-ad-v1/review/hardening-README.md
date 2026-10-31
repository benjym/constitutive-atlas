# Focused material AD verifier hardening

Replace only `def assess_case` in tools/barodesy2017_material_ad.py with assess_case.py.fragment; assess_case.diff is a local function-only diff. It does not replace the collector/archival fixes being installed concurrently. Install tests/test_barodesy2017_ad_identities.py. Existing tests/test_barodesy2017_material_ad.py already provides an exact analytical void row in its Richardson mock (line13); no change or tolerance relaxation is needed.

Changes preserve the2e-8FD and2e-10identity budgets and grid unchanged:

- Analytic void-row expected zeros must be exact. Nonzero values must be within4binary64 representable steps; Boolean/nonfinite checks remain inherited from strict7x13validation.
- AD primal values reuse fresh independent source-derived rate.channel_checks: exact-zero channels, fourULP void closure and the source stress-envelope percomponent bound, alongside existing norm budget.
- Independent density derivative identity: J_e(stress)=c3*r*c5*density^c5*sigma/(1+e).
- Pressure-density identity: J_sigma*sigma=stress_rate+lambda*(1+e)*J_e for stress rows; void row remains zero. This correctly avoids an invalid assumption of degree-one stress homogeneity: density^c5 changes as pressure^(lambda*c5).
- New retained metrics density_void_column_error and pressure_density_scaling_error use the preexisting2e-10identity budget/normalization. The formulas use separately evaluated Cartesian source scalar terms, not FD fits or production Jet results.

Testing: six new groups pass with the function applied as an in-memory overlay, plus all27existing AD tests:33total. Mock Jacobians are Richardson central differences with exact analytic void row and are never represented as actual AD evidence. Tests cover exact-zero corruption at1e-12,4vs5ULP boundaries, source-density/pressure identity errors small enough to pass2e-8FD but large enough to violate2e-10identity, and primal void closure corruption. No native/Wasm/build calls occurred. Actual matrix must be recollected after script freeze because sourcehash and metrics changed.

Parent review report at /private/tmp/atlas-barodesy-ad-review-20261031-v1/REVIEW.md explains seed/scale correctness and limitations:21regular cases only, no zero/hydrostatic/nearhydroAD, scalar binary64FD with Decimalexpm only, observed grid refinement rather than rigorous derivative error certificate. These changes add verification; they do not grant integration or scientific admission.
