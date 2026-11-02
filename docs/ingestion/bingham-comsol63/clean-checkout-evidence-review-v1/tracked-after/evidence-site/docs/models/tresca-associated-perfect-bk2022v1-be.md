# Associated Tresca perfect plasticity — BK2022v1, project BE

This dossier covers the proposed draft `tresca-associated-perfect-bk2022v1-be`, not the generic Tresca yield criterion. Independent scientific review is pending and unassigned. The proposal is not installed in the public catalogue by this review.

Primary source: Tahar Z. Boulmezaoud and Boualem Khouider, *Unification of the mathematical model of elastic perfectly plastic solids: a convex analysis approach*, [arXiv:2207.12719v1](https://arxiv.org/abs/2207.12719v1), 26 July 2022; [versioned PDF](https://arxiv.org/pdf/2207.12719v1). The private source receipt records SHA-256 `db7fb284eb9bb622883d5daff6361db37cab912b890b8a24ed99a2428abc7805`. This review reuses the [assembled source reading](../ingestion/tresca/README.md) and [coordinator crosswalk](../ingestion/tresca/COORDINATOR_REVIEW.md); it does not claim fresh PDF inspection or an independent signature.

Qualified private definition: `7f98e11faad012d3a1cff5fff1dc7cae91e80390e48ef01af396b04018018871`. Proposed public definition: `19acebed37d59120e49c5dff698e2b7d2a2693bbce9ec35c8bcbc65954819e18`. Only id, name and description change. The [proposal and pending review](../reviews/tresca-v5-source-integration-v1/README.md) bind these exact bytes.

## Source and algorithm

| Source locators | Contract |
| --- | --- |
| pp. 2–3, Eqs. 1–8; p. 6, Eqs. 27–31 | Additive infinitesimal elastic/plastic strain, isotropic Hooke law and associated normal-cone flow. |
| p. 7, Eqs. 32–45 | Pressure invariance, constant positive Lamé moduli and elastic compliance. |
| pp. 15–16, Eqs. 77–81 | Constant Tresca set with positive maximum shear strength k. |
| pp. 18–21, Eqs. 89–108 | Repeated-eigenspace continuum normal projection. This is distinct from the project finite backward-Euler update. |

Write C:A=2mu A+lambda tr(A)I and K={A: eigmax(A)-eigmin(A)<=2k}. The continuum closure is sigma_dot=C:(epsilon_dot-ep_dot), sigma in K and ep_dot in N_K(sigma). The project adopts compression-positive sigma=-tau, epsilon=-epsilon_source and ep=-ep_source simultaneously. Central symmetry of K and isotropy of C preserve the equations and plastic work. All symmetric tensors use orthonormal Mandel order xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz. Stress is **total Cauchy stress**, in a fixed frame at infinitesimal strain; no pore law or finite-spin transport is supplied.

The separately derived project backward-Euler update projects trial T=sigma_n+C:de onto K in the compliance metric. Returned stress R preserves trial pressure. The stress residual is r_sigma=sigma-R. The original plastic-strain residual is r_ep=ep-ep_n-C^-1:(T-sigma). The implemented row is r_ep'=r_ep-C^-1:r_sigma=ep-ep_n-C^-1:(T-R). Thus the block row transformation [[I,0],[-C^-1,I]] is invertible and preserves roots, while changing off-root derivatives. Pressure preservation permits C^-1:(T-R)=(dev(T)-dev(R))/(2mu). See the [pressure-split derivation](../reviews/tresca-pressure-split-v1/README.md).

Strict corner decisions use certified comparisons of the actual binary64 trial. Yield equality selects elastic; face/corner equality selects face. Derivatives are selected branch extensions, not unique classical tangents at nonsmooth boundaries. Projectors require isolation of the selected eigenvalue; [the certified predicate proof](../reviews/certified-centered-middle-v1/PROOF.md) does not remove spectral or expression-range limits.

## Preparation and temporal contract

Persistent state is full sigma6 and ep6, both explicitly supplied and finite. Initial sigma must lie in K; it is not silently projected. Initial total strain is implied by ep+C^-1:sigma. Laboratory plotted strain is change from this preparation, not a declaration of zero absolute initial strain. Plastic strain history is not reset on reversal. There is no physical clock, creep, density, hardening or event reset. An admissible zero increment holds the state; failed attempts retain the full incoming parent. Changing-direction partitioned paths need not equal one unsplit return.

The selected source assumes lambda>0, mu>0, k>0; this corresponds to 0<nu<0.5. A wider stable elasticity range is not silently included. The positive p_ref is a numerical scale. Example parameters and initial states are software examples, not source-matched soil calibration.

## Evidence and remaining decisions

The [private v5 qualification](../../catalogue/investigations/tresca-certified-corners-v5/README.md) passes its original native/Wasm gates: 219 corpus requests, all 38 derivative columns, 12 own-state history steps and 29 laboratory requests, including the formerly failing reversal. Historical failed studies remain failures. These bounded comparisons establish numerical evidence, not independent source admission, experimental validation, a universal finite-parameter domain or bitwise backend identity.

Raw residual evaluation and physical solution admissibility have separate contracts. Representability, intermediate overflow and selected spectral isolation still limit execution. The first mixed public catalogue with solution constraints needs a prospective compatibility study for the existing nine models. Actual browser packaging, full-state preparation/import/export and total-stress routing remain separate checks. Pore pressure must be unavailable/null; effective-stress-only experimental overlays must reject this model. No Wichtmann calibration or applicable comparison is established here.
