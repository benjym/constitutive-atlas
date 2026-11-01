# Duncan–Chang (1970), constant Poisson ratio, endpoint-average realization

This exact formulation implements the original complete isotropic incremental three-dimensional closure, with the source's constant-Poisson assumption. The endpoint averaging, branch equality rule, finite history update and positive postfailure modulus are explicit Atlas numerical choices. The exact definition has accepted independent agent review and complete native/Wasm source qualification. Atlas packaging and live delivery are tracked separately in [the delivery ledger](../ingestion/duncan-chang-1970/DELIVERY.md).

J. M. Duncan and C.-Y. Chang, *Nonlinear Analysis of Stress and Strain in Soils*, Journal of the Soil Mechanics and Foundations Division 96(5), 1629–1653 (1970), [DOI](https://doi.org/10.1061/JSFEAQ.0001458). The user-supplied originals are retained privately and identified by [source receipts](../ingestion/duncan-chang-1970/supplied-original-v2/receipt.json) and [the complete-copy supplement](../ingestion/duncan-chang-1970/complete-copy-v4/receipt.json). The [1971 erratum](../ingestion/duncan-chang-1970/erratum-v3/README.md) corrects a later discussion's Eq. 26; it does not replace the original material equations.

| Source | Implemented content |
| --- | --- |
| pp. 1630–1635, Eqs. 1–8 | Hyperbolic primary triaxial relation, confinement-dependent initial modulus and strength ratio |
| Eqs. 12–13 and unloading discussion, pp. 1640–1645 | Primary tangent modulus, unloading/reloading modulus and maximum previous stress-difference memory |
| Eq. 15 and constant-Poisson discussion, pp. 1642–1648 | Complete isotropic incremental 3D stiffness/compliance closure |
| Table 1 | Dense and loose illustrative source coefficients; no independent calibration claim |

Write (D=\sigma_1-\sigma_3), where principal stresses are ordered largest to smallest. The complete persistent state consists of effective Cauchy stress, six Mandel components, and scalar history (h=\max D). Both must be supplied explicitly. All stresses and moduli use Pa, friction angle uses radians, and strain is dimensionless. Compression is positive for both stress and strain. The frame is fixed spatial with infinitesimal strain and zero spin. This formulation supplies no physical clock, pore-fluid law, density evolution, dilatancy law or finite-rotation transport.

For each finite trial, set (\bar c=(\sigma_3+\sigma_{3,n})/2), (\bar D=(D+D_n)/2), (F=2(c_{cohesion}\cos\phi+\bar c\sin\phi)/(1-\sin\phi)), and (S=\bar D/F). The source-derived moduli are (E_i=Kp_a(\bar c/p_a)^n) and (E_{ur}=K_{ur}p_a(\bar c/p_a)^n). Atlas chooses (E=E_{ur}) if (D<h_n); otherwise (E=E_i(1-R_fS)^2) if (S<1), and (E=E_{failure}>0) otherwise. Equality (D=h_n) belongs to the primary branch; equality (S=1) belongs to postfailure. These finite endpoint decisions are not an exact event-location algorithm from the source.

The declarative residual is

$$
r_\sigma=\sigma-\sigma_n-\frac{E}{1+\nu}\operatorname{dev}(\Delta\epsilon)
-\frac{E}{3(1-2\nu)}\operatorname{tr}(\Delta\epsilon)I,
\qquad r_h=h-\max(h_n,D).
$$

The ten parameters are (p_{ref},p_a,K,K_{ur},n,R_f,c_{cohesion},\phi,\nu,E_{failure}). The first is a numerical residual scale; the atmosphere and failure coefficient use explicit SI conversion. The illustrative 10 psf failure coefficient is not a universal source value. Positive confinement and strength, finite intermediate arithmetic and the declared parameter bounds are required. Initial and committed states require (h\ge D\ge0); no pressure floor, stress projection or inferred missing history is used.

Mandel order is xx, yy, zz, √2xy, √2yz, √2xz. Exact repeated extreme principal values select trace or half-pair expressions with cluster-average scalar derivative rows. These are selected branch linearizations, not unique classical derivatives or a proved generalized Jacobian of the entire nonsmooth residual. Numerically unresolved distinct spectra may be rejected. Rounded rotations are assessed as their actual stored tensors.

The common engine solves the seven-component implicit residual. Provisional Newton iterates may leave the physical solution set while remaining in the residual domain. Exact physical admissibility and the unchanged residual tolerance bind convergence and commit. The bounded generic restart and adjacent-float safeguards are independently documented in [the generic Newton review](../reviews/newton-endpoint-constraints-v1/independent-review/FINAL_REVIEW_V5.md). A failed external increment restores the entire incoming stress and history, including after successful tentative internal substeps. Zero increments hold the state; restart requires all seven components of both persistent fields. Reversals retain history. Finite paths depend on their partition and branch decisions; uniqueness or convergence on arbitrary paths is not claimed.

Independent checks use source compliance, high-precision Cartesian Jacobi eigenanalysis and direct trigonometric series, plus a positive quadratic midpoint root and the continuous source hyperbola. [The frozen full study](../ingestion/duncan-chang-1970/material-v1/execution-v1/POLICY.md) covers both source parameter examples, branch neighborhoods, full tensors, fixed-basis covariance, confinement changes, history/failure crossings, refinement, invalid inputs, transactions, derivatives and public drained presets. Qualification results and limitations must be read from the ledger; backend agreement alone is not independent equation verification. No experimental overlay, calibration, FE application or broader parameter validation is established.

Copyrighted papers remain private. Public artifacts contain bibliographic links, source hashes and independently written equations, code and results.

The [accepted nine-item agent review](../../catalogue/agent-reviews/duncan-chang-1970-endpoint-average-agent-v1.json) binds the exact definition and source/numerical evidence. Approval covers the frozen material API and two drained source-coefficient presets; it does not establish a Duncan-specific discrete-update tangent or FE-host qualification. Original four loose-history crossing failures are retained alongside the separately reviewed generic partition retry and successful complete rerun. The compiled source study compares all seven persistent components; its nonzero-path native/Wasm tolerance is 4e-8 relative to the numerical pressure scale, not bitwise agreement.
