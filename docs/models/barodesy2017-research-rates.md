# Barodesy clay 2017 research implementation

The isolated model [body-zero-spin.json](../../models/research/barodesy2017/body-zero-spin.json) represents seven physical states: six Mandel stress components and void ratio. It uses the shared schema, compiler and C++ evaluator. Its four soil parameters are explicit; the fixed 1000 Pa reference pressure is a separate singleton parameter. It is outside the public runnable catalogue.

## Source and numerical choices

The selected source is [Medicus and Fellin, An improved version of barodesy for clay](https://doi.org/10.1007/s11440-016-0458-4), body Eqs. 1–10, with incompressible-grain void closure from footnote 13. The [source review](../reviews/barodesy2017-independent-review.md) retains the body 2p versus Appendix 6p discrepancy and ambiguous printed objective-rate expression. This implementation selects the body law at zero spin; it does not assert those differences are resolved.

Exact zero loading returns zero rates. Exact hydrostatic loading uses the normalized isotropic exponential limit in compression and expansion. Regular directions use stable equivalent log1p expressions; no epsilon neighborhood is flattened. Nonzero loading/deviatoric norm underflow, K0 singularity, unsupported matrix-exponential arguments, nonfinite arithmetic and invalid states fail explicitly.

Stress support is deliberately conservative: positive diagonal components and normalized Cartesian leading minor and determinant greater than 64 binary64 epsilons. This fixes a demonstrated invariant-determinant cancellation that admitted indefinite stress. Ill-conditioned positive-definite tensors may be rejected. The margin is a declared numerical interior, not a certified exact SPD test or a source-required restriction; boundary acceptance need not be invariant under rotations. Tests assess actual rounded tensors using independent Decimal arithmetic.

## Primal evidence

Native C++ and actual persistent-module Wasm calls pass 111 independent Cartesian reference cases, three additional support witnesses across stress scales 1e-50 to 1e50, and 16 rejection/recovery cases. The corpus includes all three complete Table 2 soils, NCL loading, reversal, noncoaxial loading, rotation/reflection, positive scaling, and 72 near-hydrostatic directions. Worst normalized rate error is below 2.7e-15 against the fixed 2e-13 budget; native/Wasm difference is below 1.2e-15. Void closure agrees exactly in this corpus.

Verification regenerates all reference inputs, source metadata, 80/140-digit exponential results and rejection diagnostics, then checks 160-digit refinement. Scalar coefficient/loading arithmetic remains binary64; high precision applies to the exponential and normalization of the already rounded matrix argument. Separate exact-zero channels, a source-derived stress-component envelope and four-ULP void closure supplement the normwise rate budget. See [rate study details](../reviews/barodesy2017-rate-study.md) and [runner corrections](../../catalogue/investigations/barodesy2017-rates-v1/review/runner-fixes.md).

## Material derivatives and remaining gates

The [material AD study](../reviews/barodesy2017-material-ad-study.md) seeds all seven current states and six loading components, holding parameters fixed. It compares 21 regular-direction 7×13 Jacobians against four independently refined Cartesian finite-difference grids, with analytical identities as separate checks. Both backends pass all 21 Jacobians and 20 rejection/recovery pairs; worst final scaled finite-difference discrepancy is below 6.2e-11, within the fixed 2e-8 budget. Scaled native/Wasm Jacobian parity is below 3.8e-16. Analytical void, loading homogeneity, coordinate rotation, density-column and pressure-scaling identities also pass. The probe rejects zero and exact hydrostatic loading; neither branch has a validated material derivative policy here. This is an instantaneous derivative, not an integrated algorithmic tangent.

Retained runtime evidence is bound by the [milestone manifest](../../catalogue/investigations/barodesy2017-runtime-v1/manifest.json). Historical numerical replay accepts an explicit SHA-bound native transcript location and distinguishes current artifact verification from archived numerical evidence. Raw and partial responses survive failed acceptance checks.

Next gates are near-hydrostatic/zero derivative policy, finite loading paths with refinement and rollback, physical preparation, source-matched experimental comparisons and independent scientific review. General spin, author-code equivalence, source-variant reconciliation and public admission remain open.

The [independent isotropic reference](../reviews/barodesy2017-isotropic-reference.md) prepares nine compression paths for the next finite-update study. It distinguishes ideal NCL initialization from the actual rounded initial state and includes an arbitrary-density scalar compression correction. Its ten Python test groups pass; it is reference/design evidence, with no native finite-integration claim.
