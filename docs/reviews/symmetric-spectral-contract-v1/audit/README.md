# Independent analytical audit: symmetric spectral contract v1

2026-10-31. NUM-symmetric-spectral-contract, audit worker `sanisand_loading_source`. Read-only review; no Atlas imports, author-code execution, builds, shared edits, numerical admission, or floating eigensolver selected. This packet is an analytical subset. The parent task remains WIP until its separate floating algorithm, accuracy/classification/failure policy and stored-Mandel reference corpus are frozen.

## Finding

The expanded proposed API is mathematically sufficient for the selected constant-cohesion isotropic elastic, nonassociated Mohr–Coulomb H=0 source domain, including complementary repeated spectra. No blocking algebraic defect identified. This conclusion depends on lazy branch evaluation and correct value-only qualifier enforcement. It does not establish a floating implementation or global classical differentiability.

The first extrema-plus-trace proposal had a material numerical gap: for binary64 diagonal `(1e300,1,-1e300)`, even an exact trace rounded to1 yields middle0 through `(trace-min)-max`; exact middle is1. The parent accepted separate `principal_mid[_value]` and `principal_upper_sum/lower_sum` operations with stable internal evaluation rather than naive trace subtraction. These remove the API-level need for that unstable reconstruction. They do not themselves specify a stable algorithm or certified branch decision.

`reviewed-contract.md` is the exact candidate read during this review. `review-inputs.json` records its hash and pinned model source inputs. The parent subsequently advised that its evolving draft includes the apex parameter caveat below; no claim is made that the mutable draft still equals this snapshot. The authoritative constitutive source is [Sysala–Cermak arXiv1508.07435v3](https://arxiv.org/abs/1508.07435v3), private PDF SHA256 `bf35ee09d500b8e21aabdddbdfac363c5f68368f150890c60343bc62447c83ca`. Source pp7–13 Eqs3.1–4.29 supply the law/branches; pp14–16 Eqs5.3–5.11 and Remarks5.1–5.2 discuss consistent tangents. This audit reuses the previously visually read pinned source and exact ingestion formulas, not a new journal-version equivalence.

## Branch and derivative sufficiency

Use source tension-positive ordering a>=b>=c, with the pinned Atlas sign/order conversion. Elastic returns A directly and accepts all repeats. The strict face interior has a>b>c; ordinary three eigenvalues and extreme projectors reconstruct the return with middle projector `I-Pa-Pc`. Source left edge requires only isolated c, upper-pair sum a+b and Pc; source right edge only isolated a, lower-pair sum b+c and Pa. Coaxiality/source branch inequalities ensure that a selected edge does not require the projector of its repeated pair. A repeated complementary eigenspace is legitimate, including repeated trial pairs. Apex returns cohesion*cot(phi)*I, with no spectral derivative operation. Triple-repeat plastic trial therefore remains admissible at the apex. Do not eagerly evaluate an unused simple-extreme or projector branch.

For simple selected eigenvalue lambda and projector P, any symmetric Cartesian H obeys:

- `Dlambda[H]=tr(P H)`.
- `DP[H]=sum_j (Pj H P + P H Pj)/(lambda-lambda_j)`, excluding the selected index.
- If the complement has repeated value mu, combine it: `DP=((I-P) H P + P H (I-P))/(lambda-mu)`. No internal repeated-pair denominator occurs.
- Upper/lower pair-sum derivative is `tr((I-Pisolated) H)` and therefore exists across internal pair crossings as long as the complementary extreme remains isolated.

These follow by differentiating AP=lambda P, P²=P, symmetry and traceP=1. For left reconstruction `R=ra(I-Pc)+rc Pc`, derivative is `Dra(I-Pc)+Drc Pc+(rc-ra)DPc`; right is analogous. Face requires projector variations as well as principal-value derivatives. Nonassociated tangent need not be symmetric; principal-axis diagonal sensitivities alone are insufficient.

Apex zero tangent applies only to trial-stress directions for fixed parameters in an open apex sector. If parameters are seeded, `D(cohesion*cot(phi))=cot(phi) Dcohesion - cohesion*csc²(phi) Dphi`, with phi in radians. Atlas compression sign reverses this result. At cohesion5, sinphi3/5, cosphi4/5 the two source coefficients are4/3 and-125/9. A generic AD expression must retain these parameter columns.

A repeated selected minimum/maximal eigenvalue has no general classical derivative: diag(1,1,4)+t*diag(-1,1,0) has minimum1-|t|. Returning an averaged derivative or choosing a basis would change the stated contract. This does not prohibit value-only queries or isolated-complement pair sums.

## Qualifier and equality constraints

The candidate `guard_flow.py` was read as a dependency prototype, separate from production name/shape/dimension checks. Its data-versus-control separation is appropriate: value-only numerical arithmetic and transitive aliases propagate taint; comparisons consume it as a primal Boolean; select propagates both numerical branch qualifiers, excluding its predicate. Thus `select(value_only_predicate, ordinary1, ordinary2)` can supply a branch derivative, whereas value-only arithmetic in either result arm must reject a numerical sink even when that arm is currently unselected. Cancellation such as0*value_only cannot launder taint. All numerical sinks, including scales, initial recipes and reset assignments, need the same enforcement; aliases must be checked transitively. Boolean-as-number and unknown names remain the separate validator's responsibility. Every input seed must still be validated; value-only does not authorize acceptance of NaN derivatives.

Source equality ownership selects elastic for Ftrial<=0, an edge at the face upper boundary, and apex at the edge upper boundary. At such boundaries, report the selected branch/one-sided tangent; it is not a unique classical derivative of the complete map. Source Remark5.2 skips proof at remaining boundary points, so the audit does not upgrade every chosen boundary matrix to a proven generalized Jacobian element. Event/reset semantics require their own integration review.

## Exact checks and limits

Run `python3 check_projectors.py > reproduced.json`, then compare parsed JSON with results.json. Python standard library Fraction arithmetic only. Four cases (two simple extremes with complementary repeats, distinct min/max), each with38 exact symmetric directions, produce152 rows. Each row checks Cartesian symmetry, traceDP=0, differentiated idempotence and eigenrelation, and covariance under both an xy rational rotation and a dense rational orthogonal rotation:304 rotated checks. The dense rotation has all entries nonzero, so rank-one projectors exercise all six symmetric components. Complementary repeated cases also equal the group formula; all152 pair-sum derivative identities pass. Two retained witnesses cover nondifferentiability and unstable rounded middle recovery. Failed assertions:0.

The38 directions label a complete column batch, not a proof of a production Jet ABI. These are rational Cartesian fixtures, not exact spectra asserted for rounded Mandel encodings. They do not test an eigensolver, source classifier, observed native/Wasm execution, transactional output, sticky failures, or a constitutive implementation. Transactional output/full-seed validation/lazy runtime evaluation are necessary design constraints that remain unimplemented and unobserved here.

Floating ordering, isolation-resolution diagnostics, irrational eigenvalue rounding, near-boundary classification, subnormal scaling, intermediate/final overflow, derivative inverse-gap growth, convergence budgets and recovery require separate prospective policy/reference work. Finite matrices can have unrepresentable eigenvalues; finite projector derivatives can also suffer intermediate range failures. Do not add an epsilon gap, stress floor, averaged eigenvalue or smoothed yield surface as a substitute for reporting unresolved numerical resolution. Exact mathematical branch inequalities alone do not certify classification from rounded spectral values.

Smallest next action: parent incorporates these API/qualifier/tangent constraints, retains WIP status, and scopes the independent floating policy/reference study before any compiled observations. No further algebraic blocker found in this bounded review.
