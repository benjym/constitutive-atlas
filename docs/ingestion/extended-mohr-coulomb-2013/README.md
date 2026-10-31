# Extended Mohr–Coulomb 2013 — ingestion packet

Task ID: ING-extended-mohr-coulomb-2013. Owner: review_sanisand. Date: 2026-10-31.

This packet pins the original Doherty–Muir Wood paper and inventories its complete available constitutive sections, including the original Cam Clay flow and asymptotic hardening. It is not a criterion-only executable model. Six source/algorithm reconciliation gates remain open; no corrected variant or scientific admission is selected.

## Identity and sources

J. P. Doherty and D. Muir Wood, *An extended Mohr–Coulomb (EMC) model for predicting the settlement of shallow foundations on sand*, **Géotechnique 63(8), 661–673 (2013)**, [DOI 10.1680/geot.12.P.008](https://doi.org/10.1680/geot.12.P.008). The [UWA record](https://research-repository.uwa.edu.au/en/publications/an-extended-mohr-coulomb-emc-model-for-predicting-the-settlement-/) identifies the 2013 issue. The [Dundee record](https://discovery.dundee.ac.uk/en/publications/an-extended-mohr-coulomb-emc-model-for-predicting-the-settlement-/) records early online publication on 12 December 2012. The PDF's first page confirms the latter date; these are two dates for the same DOI, not different model revisions.

The [publisher PDF](https://www.emerald.com/jgeot/article-pdf/63/8/661/2789443/geot_12_p_008.pdf) was retrieved through the Crossref-listed [ICE PDF route](https://www.icevirtuallibrary.com/doi/pdf/10.1680/geot.12.P.008). The web tool returned 403, while ordinary direct retrieval followed the publisher redirect and returned a valid 13-page PDF, HTTP 200. A route-specific failure is not an absence claim. Exact private download: **1,248,623 bytes**, SHA-256 **`f801f2f9be72b4cdbc1333889d6bceac0771ec1fa386f636c72e63d633cb096e`**. This copy carries an institutional download stamp; the receipt pins its actual bytes, not a presumed universal publisher hash.

`source-receipts.json` retains URL/status/hash receipts, date, private paths, identity evidence and visual coverage. Twenty top-level Downloads PDFs were screened by filename and first-two-page text for the author/title/DOI, with no match. This is not an exhaustive recursive full-text absence statement. The acquired publisher PDF makes source acquisition successful. No supplement, author constitutive code or executable algorithm was acquired. Copyrighted PDFs, HTML, extracted text and renders remain private and are excluded from the whitelist; redistribution permission is not established.

## Existing work and gaps

This extends [candidate triage B3](../../reviews/parallel-candidate-triage.md) and the discovery entry in [the catalogue](../../../catalogue/manifest.json). The [SoilModels page](https://soilmodels.com/emc/) distinguishes a modified and extended OptumG2 version. Neither that version, a later cemented/damage model, nor generic perfectly plastic Mohr–Coulomb is substituted for the selected paper.

The source is now available, but the printed appendices do not support unqualified transcription. Apparent invariant/gradient errors, flow-scalar compatibility and the rounded-normal integration recipe require explicit independent decisions. The ledger records source facts separately from mathematical diagnostics and proposed support restrictions.

## Equations and schema crosswalk

`equation-ledger.json` locates Eqs1–55, including spatial stiffness assignment Eq16 and the triaxial calibration identity Eq17. Mathematical formulas in this audit are not a loadable Atlas definition. Core pages 662–665 and 671–672 were visually inspected using the PDF skill; extracted text locates supplementary application material.

| Source | Typed representation and units | Status |
| --- | --- | --- |
| Eqs1–3, p662 | constant `G` Pa, `mu` dimensionless; isotropic linear elasticity | Available. Engineering shear, not Mandel shear. |
| Eqs4–5, p663 | effective stress `sym3`, attraction `a` Pa, mobilized `phi_y` radians; exact MC yield `F` Pa | Available value formula, subject to invariant closure. |
| Eqs7–11, pp663–664 | volumetric plastic strain, distortional scalar and original Cam Clay potential `Q` Pa | Source distinguishes this from constant-angle/associated MC flow. Scalar versus full tensor norm needs reconciliation. |
| Eqs12–15, p664 | scalar isotropic hardening `phi_y`; `beta` strain scale; `phi_y0` preparation history | Rational asymptote. Analytic inverse and derivative independently checked. |
| Eqs18–26, pp671–672 | mean stress, `J` Pa, determinant `J3` Pa³, Lode angle, invariant-gradient basis | Printed dimensional/derivative conflicts retained. |
| Eqs27–43, p672 | exact and rounded gradient recipes; numerical threshold `theta_t=25°` | Exact yield value is retained while normals are rounded beyond the threshold. |
| Eqs44–55, p672 | elastic/plastic split, plastic multiplier, consistency hardening modulus, angle increment | Incremental rate algebra, not a complete return-map/controller listing. |

### Parameters, state and preparation

Table1, p664 lists six material parameters: `G`, `mu`, `phi_p`, `phi_cv`, `a`, `beta`. Source pressures/moduli are commonly kPa and angles degrees; a proposed Atlas representation uses Pa and radians. `phi_cv` may exceed `phi_p`: the paper illustrates 20°, 30°, and 40° with peak 30°. It is the angle associated with zero plastic volume rate, not necessarily an ultimate critical-state angle. Attraction is constant; `c=a tan(phi_y)` therefore does not represent constant cohesion during hardening.

The regular rate closure suggests six effective-stress components and one current hardening angle. `phi_y0` is fixed initial maximum-mobilized-friction provenance, not a seventh fitted material constant or a kinematic backstress. Eq13's scalar `alpha` is a derivable preparation quantity, unrelated to SANISAND alpha tensors. Accumulated scalar plastic strain and the plastic strain tensor may be retained as outputs but must not be independently evolved under contradictory definitions. No density, void-ratio, kinematic-hardening, physical-time or postpeak-softening law is supplied by this model.

Initial stress and maximum previously mobilized angle are explicit inputs (p664). The initial yield locus may exceed the currently mobilized friction to represent prior history; it must not be inferred solely from current stress. Unloading remains elastic inside the current expanded locus; no reverse softening or history-reset law is given. Preparation is not a hidden consolidation/projection path.

The p664 demonstration uses `G=4 MPa`, `mu=.25`, `phi_p=30°`, `a=0`, `beta=.005`, `phi_y0=1°`; these are example settings, not defaults. Page666 also describes a separate perfectly plastic endpoint with `phi_y=phi_p=phi_cv`. That endpoint cannot be reached by evaluating singular Eq12 at equality; it needs an explicit supported branch.

### Signs, dimensions and regular domain

Source stress and normal strain are compression-negative. Atlas compression-positive transport would negate the full named stress and strain tensors; pressure changes sign, `J` is unchanged and the consistent Lode convention changes sign. Do not negate only mean pressure. Eq1 lists engineering slots `(xx,yy,zz,xy,xz,zy)` while Appendix26 lists `(xx,yy,zz,xy,yz,zx)`. Named Cartesian transport must resolve that permutation before engineering-to-Mandel conversion. Engineering shear strain is `2 epsilon_ij`; Mandel stress is `sqrt(2) sigma_ij` and Mandel strain is `gamma_ij/sqrt(2)`, preserving work.

The state/integration ledger separates printed facts from proposed mathematical checks. A regular supported branch needs finite values, `G>0`, `-1<mu<.5`, positive `beta`, `phi_p>0`, `phi_y0<phi_p`, and active denominators/log/square-root/arcsine domains addressed. These inequalities are mathematical support proposals, not universal source calibration ranges. In particular, no `phi_cv<=phi_p` restriction is justified. A constant hydrostatic compressive state can be elastic without evaluating Lode angle; an active apex cannot be treated that way.

## Source reconciliation gates

1. **EMC-01, Eq20/21 p671:** the printed Lode formula has denominator `2J`, while `J3` is the cubic stress determinant. Its argument has pressure-squared units and scales by 100 when all stresses scale by 10. The dimensionally homogeneous denominator `2J³` is retained only as a derived diagnostic alternative. No correction is silently adopted.
2. **EMC-02, Eqs22–26 pp671–672:** the chain-rule basis has units incompatible with ordinary determinant derivatives. Printed Eq26c is a cofactor vector divided by `2J²`, plus an identity-vector third. Its normal-component sum is 1/2, whereas `det(dev(sigma))` is invariant under hydrostatic shifts. Fixing Eq20 alone does not close this basis problem.
3. **EMC-03, Eq41 p672 versus Eq11 p664:** the potential's angular derivative prints `phi_y`; the potential and nearby instructions use `phi_cv`. A derivative check distinguishes them when the angles differ.
4. **EMC-04, Eqs8–9 versus51/55:** a work-conjugate shear scalar and a positive Euclidean distortional norm are not generally interchangeable. Even a dimensionally consistent Cartesian differentiation of the Lode-dependent potential gives a nonradial deviatoric flow. A retained witness has `Lambda Q_J=1` but a strictly larger Eq9 norm. This is a diagnostic against an unqualified general-stress identity, not a selected alternative hardening model.
5. **EMC-05:** the source vector slot ordering changes between Eq1 and Appendix26. A shear permutation is not an innocuous implementation detail when strains, stresses and gradients are paired.
6. **EMC-06, Appendix2 p672:** the source evaluates the exact yield criterion for all Lode angles but uses rounded `Ka` derivatives and rescaled `C1` outside ±25°. The latter differs from the actual hydrostatic derivative of the exact value. Its algorithm must be represented explicitly; automatic differentiation of exact `F` does not reproduce the printed normal recipe.

The body calls the strain asymptote exponential, whereas Eq12 is rational. This packet follows the printed equation for its independent scalar check and does not infer a different exponential law. No publisher erratum or author confirmation was acquired in this bounded investigation.

## Temporal integration and nonsmooth behavior

The p664 implementation uses forward Euler with adaptive substepping and error control, citing Sloan1987 and Abbo1997. Appendix3 provides the incremental elasto-plastic equations, including the consistency denominator and `H`, but does not specify a complete tolerance/controller, elastic-to-plastic intersection, unloading, apex or failure/recovery algorithm. Those external methods are acquisition/review inputs before a faithful algorithm reproduction, not equations to guess.

The law is time-independent; p671 explicitly identifies creep as outside its scope. A hold at fixed strain does not justify invented hardening. The model lacks postpeak softening and, except for the equal-angle case, can continue indefinite compression or expansion rather than reaching a true critical state (p665).

The exact MC value has face, repeated-principal edge and apex issues. Rounded normals at the Lode extremes do not constitute an exact multisurface edge/apex solver. The apex is `p=a,J=0` in the source convention (compression-positive `P=-a`); no tensile cutoff or apex continuation is specified. `1/J`, the determinant basis and Lode angle must not be eagerly evaluated at zero deviatoric stress. An exact active-set version would be a separately named numerical variant, not silently the paper's integration.

Proposed Atlas transaction phases are parent, elastic trial/intersection, active branch, material substep, error-control acceptance, and whole-caller commit. Every failed candidate must retain its immutable parent; a late full-caller failure must roll back stress, angle, optional strain outputs and preparation together. Accepted external caller prefixes remain available. These are requirements for implementation, not claims demonstrated by the source UMAT. No author code was run.

The machine ledger includes a predeclared face/edge/apex, unloading/reloading and subdivision/rollback acceptance plan. Independent references must start from the original supplied state, cover every caller point, and distinguish exact criterion residuals from the selected algorithmic normals. Freeze all tolerances, scales and failure policies before compiled observations. Tangents must correspond to the chosen variant and state which branch boundaries are unsupported.

## Independent checks

Run `python3 docs/ingestion/extended-mohr-coulomb-2013/check_packet.py` after installation, or the staged script by absolute path. Normal execution requires exact equality with `check-results.json` and does not mutate evidence. Nine groups pass: elasticity/work transport; hardening inverse/derivative/initial threshold; asymptotic peak; dimensional Lode witness; hydrostatic gradient defect; potential-angle conflict; independent principal face/edge value identity using the explicitly derived invariant alternative; rounding threshold and normal distinction; nonradial shear-scalar distinction.

The checks are independent scalar/Cartesian algebra, not production DSL agreement, native/Wasm validation or experimental evidence. One development failure is retained in the result metadata: directly applying `asin` to a rounded repeated-principal endpoint lost sufficient angle accuracy to fail a `2e-15` identity gate. Exact known endpoint angles are now supplied only for those analytically repeated-principal fixtures. No tolerance was changed and no material continuation was introduced.

## Handoff

The local-relative manifest covers README, source receipts, equation ledger, state/integration ledger, independent check script and retained results. Private sources/renders, acquisition helpers and caches are excluded.

Source access: **successful**. Source closure: **partial, EMC-01–06 unresolved**. Executable model: **not added**. Verification: **nine bounded algebra/diagnostic groups**. Scientific admission: **not requested or changed**.

The smallest safe next executable packet is the scalar Eq12–15 hardening fragment plus independently transported linear elasticity. It should declare radians, explicit `phi_y0`, finite positive regular parameters, analytic inverse and derivative, initial threshold and asymptotic endpoint exclusions. It must not claim a full EMC constitutive model. In parallel, independently review the printed invariant basis, full flow scalar and rounded-normal algorithm against the cited primary derivations. Only after those decisions should a named full stress-update variant and its face/edge/apex integration be proposed. Required generic capabilities may include named engineering/Mandel transport, independently declared criterion/algorithmic normal, explicit active nonsmooth branches and transactional substeps; no shared schema change is made here.
