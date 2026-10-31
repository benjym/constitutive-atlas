# Generic symmetric spectral contract — candidate v1

2026-10-31; NUM-symmetric-spectral-contract. This prospective contract supports the complete bounded [Mohr–Coulomb H=0 formulation](../../ingestion/mohr-coulomb/README.md) through generic expressions. It is not a model kernel, installed DSL extension, selected floating eigensolver, or a claim of compiled verification. Production code remains unchanged. Implementation and numerical observation require a separate prospective freeze after review.

## Representation and operations

Input A is a finite real symmetric 3×3 tensor represented by six Mandel values `(xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz)`. Let eigenvalues be a≥b≥c, and P_a/P_c be the orthogonal rank-one projectors for an isolated maximum/minimum. Eigenvector signs are never exposed. Proposed generic operations:

| Expression | Result / dimensions | Differentiation contract |
| --- | --- | --- |
| `principal_max_value(A)` | scalar a, same dimensions as A | Value-only classifier; no derivative supplied |
| `principal_min_value(A)` | scalar c, same dimensions as A | Value-only classifier; no derivative supplied |
| `principal_mid_value(A)` | scalar b, same dimensions as A | Value-only classifier; no derivative supplied |
| `principal_max(A)` | scalar a, same dimensions as A | Classical derivative only if a>b |
| `principal_min(A)` | scalar c, same dimensions as A | Classical derivative only if b>c |
| `principal_mid(A)` | scalar b, same dimensions as A | Classical derivative only if a>b>c |
| `principal_upper_sum(A)` | scalar a+b, same dimensions as A | Classical derivative if b>c; a=b supported |
| `principal_lower_sum(A)` | scalar b+c, same dimensions as A | Classical derivative if a>b; b=c supported |
| `projector_max(A)` | dimensionless symmetric P_a | Requires isolated a; b=c is supported |
| `projector_min(A)` | dimensionless symmetric P_c | Requires isolated c; a=b is supported |

Value-only extrema accept repeated and hydrostatic spectra; they do not differentiate arbitrary eigenvectors or assign an averaged derivative to a multiple eigenvalue. All operations check input values, and Jet entry points check all38 incoming derivative components for finiteness. A value-only Jet may internally hold zero derivative storage for transport, but those zeros are **not derivatives** and must never become a numerical output through the validated DSL.

The ordinary simple-eigenvalue and pair-sum operations have the same isolation requirement in Python/primal and AD execution. This prevents a definition from passing primal execution and then acquiring a hidden AD-only domain restriction. Only the selected extreme must be simple; rejecting the complementary repeated pair would unnecessarily exclude legitimate edge states. A triple repeat cannot provide either individual projector. A repeated selected extreme is an operation-domain failure, not an instruction to choose an eigenvector, round apart a tie, or perturb stress.

## Static value-only dependency discipline

Maintain a dependency qualifier in addition to existing shape/dimension types. `principal_*_value(A)` is value-only. Numeric arithmetic, all numeric functions, tensor construction and derived aliases propagate the union of value-only dependencies without algebraic cancellation. Thus `0*principal_max_value(A)` remains value-only. Each derived value is checked in declaration order; unknown names, forward references and cycles remain errors under the existing validator.

A scalar comparison consumes these dependencies to produce a Boolean. Shape/dimension validation still prohibits Boolean-as-number expressions. `select(condition,then,else)` checks the condition but its numerical result depends only on the union of the two branch qualifiers. The comparison is a primal branch decision, as with existing selects; the chosen branch supplies its numerical derivative. Both branches must be statically valid even though only the chosen branch is dynamically evaluated. Derived guard scalars can be reused in predicates, including a prospective plastic multiplier computed only to classify a branch.

Reject any value-only dependency reaching an equation RHS, observable, state/observable scale, reset assignment, initial-state expression, or other numerical output. State values and parameters cannot carry this qualifier. Initially allow it only in comparisons used by selects, domain checks and initial checks; reset guards/events require their own integration review before using it. Do not permit exporting a value-only numeric observable under a normal differentiable type. No schema field should make this optional. These checks are required for every model-validation/code-generation entry point, not only the website.

`guard_flow.py` is a source-only candidate dependency-analysis prototype. It is separate from production shape, dimension, name and model validation; passing it is not complete expression/model validation. `check_guard_flow.py` contains positive/negative examples including aliases, masked arithmetic and nested selects. Its prototype returns dependency sets; the future validator must reject a nonempty set at each numerical sink.

## Classical tensor derivatives in simple selected eigenspaces

For arbitrary symmetric Cartesian direction H, a simple eigenvalue λ_i with rank-one projector P_i satisfies

`Dλ_i[A](H) = tr(P_i H)`.

For simple selected i, the derivative of its projector is

`DP_i[A](H) = sum_{j != i} (P_j H P_i + P_i H P_j)/(λ_i-λ_j)`.

If the complement has a repeated pair λ_j=λ_k, combine it as `P_comp=I-P_i` and use the single shared denominator. This expression is independent of a basis chosen inside that repeated eigenspace. It follows by differentiating `A P_i=λ_i P_i`, `P_i²=P_i` and symmetry; it is a project derivation, not a promise about a floating eigensolver. The derivative satisfies `P_i DP_i + DP_i P_i=DP_i`, `tr(DP_i)=0` and the differentiated eigenrelation. These identities provide independent residual checks.

For an isolated middle eigenvalue use its projector in the same formulas. For an isolated lower extreme, the upper-pair sum derivative is `tr((I-P_c) H)`; for an isolated upper extreme the lower-pair sum derivative is `tr((I-P_a) H)`. These sum primitives retain repeated-pair support without subtracting large rounded extrema from a small trace.

Mandel output uses the same shear factors as input. The input norm and inner product are Frobenius norm and contraction; neither raw tensor shear vectors nor engineering strains can be substituted. For each of38 Jet columns, map its six input entries to H, apply the same derivative formula, and map back. The last six columns represent loading controls; the other32 are state/unknown directions. Do not silently drop zero-primal/nonzero-derivative columns. Output failure is transactional: leave a caller's prefilled output unchanged and set the checked expression's sticky failure flag. Lazy selects must not evaluate projector or simple-eigenvalue operations in an unselected branch.

## Full-domain branch construction for the pinned MC source

Use the exact pinned source sign/order conversion. The following statement is in source tension-positive coordinates, applied to `-S_trial` for the Atlas compression-positive stress. Guard trial eigenvalues use value-only a,b,c directly; guard multiplier formulas use value-only arithmetic. Classify elastic/face/left/right/apex by the exact source inequalities in FORMULAS.md. Recompute differentiable branch scalars inside the lazy selected expression; do not reuse the value-only multiplier as a numerical multiplier.

- Elastic: return A directly, including hydrostatic and repeated spectra. No simple-extreme/projector calls.
- Face: trial eigenvalues are distinct under the strict face inequalities. Use ordinary a,b,c. Reconstruct with P_a, P_c and `P_b=I-P_a-P_c`.
- Source left edge: use ordinary isolated c, `principal_upper_sum(A)` and P_c. Return `r_left*(I-P_c)+r_c*P_c`. No individual a or b derivatives/projectors, even when a=b.
- Source right edge: use isolated a, `principal_lower_sum(A)` and P_a. Return `r_a*P_a+r_right*(I-P_a)`. No individual b or c derivatives/projectors, even when b=c.
- Apex: return `c_cohesion*cot(phi)*I` in source signs. No spectral derivative/projector. Hydrostatic plastic trial is supported; zero trial-stress tangent only applies in an open interior apex sector. Keep cohesion/friction dependence as ordinary scalar expressions: if parameters are seeded, the source apex derivative is `[cot(phi)*dc-c_cohesion*csc(phi)^2*dphi]*I`; never zero all parameter derivatives merely because the trial-stress tangent is zero.

Use source equality ownership: yield Ftrial<=0 is elastic; a face upper-limit equality belongs to an edge; an edge upper-limit equality belongs to apex. This selects a branch derivative, not a unique classical derivative at a nonsmooth transition. The analytical audit notes source Remark5.2 does not prove every remaining boundary case; do not claim every selected boundary matrix is a proven generalized-Jacobian element. A later public tangent API must expose nonsmooth/branch-boundary status rather than promising a unique classical tangent there. Fixed accepted-partition AD replay already has its own limits; spectrum work must not silently upgrade its meaning.

## Floating algorithm and observation gate (not yet selected)

The initial draft used exact algebraic identities `b=trace(A)-a-c`, `a+b=trace(A)-c` and `b+c=trace(A)-a`. The independent audit identified a floating counterexample: diagonal `(1e300,1,-1e300)` has exact trace1 but left-associated `(trace-a)-c` yields0. `mixed-scale-witness.json` retains this diagnostic; `initial-contract.md` retains the original proposal. The current API therefore includes a direct middle value/eigenvalue and group-safe pair sums; do not implement them as naive trace subtraction. A stable floating algorithm and reference accuracy for such mixed-scale cases remain separate requirements.

Exact source branch inequalities do not imply exact classification from rounded eigenvalues or scalar arithmetic. In particular, near-boundary ownership and unresolved numerical cases need a prospective policy; do not advertise the exact algebraic branch test as a certified floating classifier.

Exact mathematical multiplicity and numerical resolution are different. Do not merge close eigenvalues into a physical cluster, divide by a silently floored gap, average stress, or smooth the MC surface. A numerical implementation must specify scaling, convergence criterion, error diagnostic, iteration budget, ordering/equality reproducibility and separation checks **before execution**. Isolation is needed for the selected derivative/projector, not for value-only extrema. Failure to resolve an isolated gap is a reported numerical failure; it is not a new constitutive domain bound. Improve precision or algorithm when necessary rather than claiming a repeated pair makes the model unsupported.

No floating gap threshold, stress scale, Jacobi sweep limit, eigenvalue clipping rule or acceptance tolerance is adopted by this contract. Those must be frozen with an actual implementation and independent reference corpus; this design task does not claim the prospective execution-policy gate complete. A finite tensor whose true extreme overflows binary64 may fail with an explicit range diagnostic; do not return a clipped value. Subnormal/large-value cases require scale-aware arithmetic, including derivative intermediates, and must be represented in the frozen corpus.

The [LAPACK symmetric-eigenproblem guide](https://netlib.org/lapack/lug/node89.html) distinguishes eigenvalue and gap-dependent eigenvector errors and reports nonconvergence. It is numerical background, not a borrowed executable implementation or a rigorous certificate for a yet-unselected solver. The [pinned MC preprint](https://arxiv.org/abs/1508.07435v3) supplies constitutive branch and grouped-projector motivation; this generic API and guard qualifier are project design choices.

## Required separate numerical study

Before compiled observations freeze: all candidate helper/compiler bytes, independent references, inputs, output/derivative metrics, convergence/gap diagnostics, equality policy, failure/recovery sequences, and budgets. Required coverage:

1. Ordered diagonal spectra and all coordinate permutations; zero, hydrostatic, selected double repeats and complementary repeats. Both successful value-only calls and explicit unsupported individual-projector requests.
2. Rational orthogonal Cartesian rotations; all six Mandel components; positive/negative stress spectra, sign reversal and sign/order conversion. Check covariance, trace, eigen residual, projector symmetry/idempotence/rank and sum reconstruction.
3. Cartesian perturbation identities and all38 columns for simple extrema and isolated projectors, including complementary repeats, mixed shear and general symmetric directions. Full projector derivatives must include rotation, not merely diagonal eigenvalue sensitivity.
4. Positive power-of-two scaling across normal/subnormal/large ranges; a separate near-gap sequence with fixed reference identity and diagnostics. Report encoding perturbations from Cartesian-to-Mandel conversion rather than pretending rounded inputs have exact unrounded spectra.
5. Guard qualifier sinks and derived aliases, value-only arithmetic in conditions, nested lazy branches and both selected/unselected invalid projectors. Check complete initial/domain/observable/scale/reset/generator consumers.
6. Nonfinite primals and each derivative column, intermediate overflow, convergence failure, unresolved gaps, failed-output preservation, sticky expression failure and solver rollback/recovery with valid calls afterward.
7. The pinned MC analytical face/edge/apex/boundary certificates, rotated full tensor tangents in open regions, repeated trial pairs, hydrostatic apex and zero holds. Boundary derivatives are checked only against the declared selected/generalized branch policy. Numerical parity is separate from independent accuracy and scientific admission.

Completion of this design packet cannot be reported as completing all numerical fixtures or floating-policy decisions. New execution task(s) must retain the independent contract audit and any rejected design witnesses.
