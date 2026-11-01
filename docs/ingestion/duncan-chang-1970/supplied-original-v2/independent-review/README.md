# Independent supplied-source gate and contract review

Task: MODEL-duncan-chang-1970, bounded E1/E2 review; 2026-11-01.
Reviewer run: `/root/duncan_supplied_review`, separate from the coordinator authoring the new receipt/crosswalk. Owned output is this directory only. This is not an E5 model approval: no exact candidate model, numerical qualification or backend delivery was reviewed.

## Source binding and method

The retained source is `.local/private-sources/duncan-chang-1970/original-1970-user.pdf`, SHA-256 `3b33f721e3d5726ac0bbb240c296a45a017676dd3d5fa3ccb525017927779667`.
This hash was independently recomputed with `shasum -a 256`.
PDF pages 1, 2, 3, 4, 6, 7, 11, 12, 13, 14, 15, 17, 18, 19 and 20 were inspected visually using the coordinator's rendered PNGs; the private compact extraction was read for surrounding text. The PDF skill, formulation contract and full-delivery/review policies were read. No compiled artifact, author code or vendor binary was executed.

PDF 1 is visibly Duncan and Chang, September 1970, Journal of the Soil Mechanics and Foundations Division, volume 96, SM5, starting at printed 1629. The user's 2021 filename does not identify a 2021 formulation.

## Decision

**Useful original equations are readable; full-source completeness remains blocked.** PDF 19 visibly repeats printed 1645 (also present at PDF 17), whereas the expected printed 1647 is absent. The repeated pages contain the same discussion and Fig.14 but are different scan/layout instances. PDF 18 ends in the middle of the FE procedure; PDF 20 resumes at printed 1648 in the middle of the boundary-condition discussion. No conclusion about missing-page content is warranted. The 1971 erratum has not been supplied or reconciled in this review.

The coordinator may transcribe and independently check the available equations now. This result does not satisfy the checklist requirement to read the full governing source and reconcile relevant versions. Do not silently replace the full requested formulation with a restricted variant or mark E1 complete.

## Verified source inventory and contract findings

| Source locator | Independently verified content | Consequence |
| --- | --- | --- |
| Printed 1630, PDF 2, Eqs.1-2 | Hyperbola and its transformed straight-line relation; major/minor principal stresses and axial strain | The scalar hyperbola is a triaxial calibration relation, not by itself a general tensor constitutive closure. |
| Printed 1631, PDF 3, Eqs.3-5 | Failure ratio, hyperbola expressed through initial tangent modulus and compressive strength, confining-pressure power law | `K`, `n`, `Rf` dimensionless; atmospheric reference pressure and all stresses/moduli must share units. The reported 0.75-1.00 range is empirical, with prose stating `Rf < 1`, rather than an unrestricted universal admissibility claim. |
| Printed 1632, PDF 4, Eq.6 | Mohr-Coulomb compressive stress difference for fixed minor principal stress | Strength formula has denominator `1-sin(phi)`; its admissible stress domain must be explicit. |
| Printed 1634-1635, PDFs 6-7, Eqs.7-12 | Tangent derivative at constant minor stress, strain elimination, stress-level definition and stress-only loading modulus | Eq.10 is `Et = Ei*(1-Rf*S)^2`, Eq.11 `S=(sigma1-sigma3)/(sigma1-sigma3)f`. Source does not authorize using the squared expression beyond failure without the described continuation policy. |
| Printed 1639, PDF 11, Eq.13; continuation 1641, PDF 13 | Unloading/reloading modulus uses `Kur`, atmospheric pressure and the same confining-pressure exponent `n` | Unloading is approximately linear at fixed confinement; it is not a separate fitted exponent law in this source. |
| Printed 1641, PDF 13, Eq.14 | Poisson-ratio evaluation from axial and volumetric strain increments, compression positive | Eq.14 is a calibration relation, not a production evolution law for variable Poisson ratio. |
| Printed 1642, PDF 14 | A single constant Poisson ratio is expressly assumed; shear-driven volume change is omitted; Table 1 parameters are given for dense and loose silica sand | Constant `nu` is an original-paper closure. Do not import later variable-nu or bulk-modulus variants into this identity. The six fitted paper parameters do not remove the additional chosen `nu` needed by Eq.15. |
| Printed 1642-1643, PDFs 14-15, Eq.15a-f | Generalized three-dimensional isotropic incremental Hooke compliance, modulus evaluated at average stress conditions, cumulative strain and stress updates | Source supports a full fixed-Cartesian tensor closure, not merely an axisymmetric scalar-only claim. Engineering shear compliance is `2*(1+nu)/Et`; mapping to tensor/Mandel shear must preserve this factor. No objective finite-rotation transport is specified. |
| Printed 1644-1645, PDFs 16-17 | `nu=0.3` for the complex-path examples; unloading/reloading modulus used when stress difference is below its previous maximum | Persistent history is maximum stress difference, not maximum stress level `S`, and the paper does not fully specify equality, event localization or noncoaxial principal-axis cases. |
| Printed 1643, PDF 15; printed 1648, PDF 20 | Curves beyond fully mobilized strength use a very small positive modulus; the sand footing example uses an expressly arbitrary 10 psf after failure | A universal 10 psf material modulus or unlabelled extension of Eq.12 would overclaim source support. A continuation value/policy must be identified as an explicit example/numerical choice or excluded with an honestly restricted identity. |
| Printed 1646, PDF 18 | FE modulus based on average stresses estimated by linear extrapolation of previous load-induced stresses plus gravity | Implicit endpoint/midpoint residuals or ODE interpretations are Atlas discretization choices, not exact reproduction of the source FE algorithm. Missing 1647 prevents completing that procedure's review. |

## Blocking and unresolved points for the lead

1. Acquire printed 1647 and the erratum. Bind new bytes in a new source receipt; preserve this defective supplied copy as evidence. Reconcile corrections before source-complete status.
2. Finish the exact variant inventory: loading modulus, unloading/reloading law, constant `nu` closure and post-strength handling. Do not equate the fitted five-parameter loading relation with the complete original procedure.
3. Declare one stress scope per executable record. Printed 1636 permits effective or total analyses only with corresponding drained or unconsolidated-undrained calibration. This is not a coupled pore-pressure law.
4. Freeze the branch/event algorithm, including equality at maximum historical stress difference, crossings during an increment, failure crossing and principal-value degeneracy. Known-stress endpoint averages and FE extrapolated stress estimates are distinct. The source does not settle whether to average endpoint eigenvalues or diagonalize an averaged tensor on general noncoaxial paths.
5. Require initial stress and any accumulated maximum-history variable explicitly. Arbitrary nonzero initial stresses do not reconstruct past loading; setting the history to current stress difference is a preparation assumption. Define trial/commit/rollback, subdivision and restart behavior as Atlas lifecycle choices and verify them.
6. Use a dimensionally and mechanically admissible constant `nu` domain for the claimed solver. Source-measured apparent ratios above 0.5 are evidence of omitted dilatancy, not authorization for unstable isotropic elastic stiffness. Positive confinement, positive strengths/moduli and the failure/asymptote bounds need explicit checks. Do not silently clamp negative confinement or invent a low-pressure floor.
7. No physical clock, creep, relaxation or objective-rate law is specified. A zero strain increment on a strain-driven contract should produce no stress/history evolution; this is a declared implementation consequence to verify, not a new physical-time law.

## Smallest useful next checks

Before compiled execution, derive the constant-confinement hyperbola inverse and derivative independently, then check their agreement with Eqs.4, 9 and 10 under a predeclared domain. Check fixed-confinement unloading slopes from Eq.13, full normal/shear compliance from Eq.15, and branch crossings using supplied history. Use a separate stress-controlled quadrature reference for changing-confinement paths and refinement, after resolving the finite-increment policy. Preserve finite-step residual differences rather than treating backend agreement as independent verification.

No executable profile or capability gap is certified here: the current DSL/operator availability was not audited. A prospective v0.3 small-strain, fixed-frame, compression-positive, effective- or total-stress incremental residual mapping is plausible, but its exact finite-step/history semantics require the lead's explicit contract and subsequent independent review.

Reproduction: recompute the private PDF hash with `shasum -a 256`; render PDF pages 17-20 with Poppler and inspect the printed page labels and text transitions. Private originals and renders must remain outside public distribution. This review changes no historical packet, shared board, candidate, schema/compiler or admission status.
