# Wu–Bauer 1994: original-paper extraction

**Draft; source inconsistencies and independent scientific review remain open.** Wei Wu and Erich Bauer, *A simple hypoplastic constitutive model for sand*, International Journal for Numerical and Analytical Methods in Geomechanics 18, 833–862 (1994), [DOI](https://doi.org/10.1002/nag.1610181203). The user-supplied original is pinned by the [receipt](../../catalogue/source-audits/original-papers-2026-10-31.json). PDF page 1 corresponds to printed p.833. PDF pages 2, 3, 8–11 and 14 were visually inspected for this extraction. Full derivation, Appendix I, remaining simulations and external correction searches are not certified complete.

The [typed source fragment](../../catalogue/source-audits/wu-bauer-1994-original.json) and [research helper](../../tools/inspect_wu_bauer_original.py) represent instantaneous algebra in source variables. They are not an admitted public model, calibrated Atlas material, or finite-step update. The publication remains unbound to a public executable formulation. It must remain distinct from VW96, IGS97 and later density-dependent Wu/Bauer variants.

## Stress law, state and units

With `T=tr(sigma)`, `s=dev(sigma)` and `D` the source stretching tensor, Eq.(21), p.840/PDF8, is

```
objective_rate = c1*T*D + c2*(sigma:D)*sigma/T
               + (c3*(sigma @ sigma) + c4*(s @ s))*norm(D)/T
s = sigma - T*I/3                                      [Eq.(22)]
```

The squares are Cartesian matrix products, not componentwise squares. The fragment uses orthonormal Mandel coordinates, preserving the Frobenius contraction and norm. All four coefficients are dimensionless; stress in Pa and stretching in inverse seconds produce Pa/s. Neither void ratio nor an independent history tensor appears in this stress law: six stress components are its minimal state. Keeping a volume/density observable would require a separately specified kinematic closure. Density-dependent coefficient sets do not make density an evolving state variable.

The law is degree one in stress and positively homogeneous of degree one in stretching. Nonzero stress trace is required by the printed denominator; neither a pressure floor nor stress-free initialization is supplied here. Algebra can be evaluated at some physically questionable states, so algebraic finiteness is not an admissibility test. At nonzero trace, zero stretching gives zero rate, while the norm generally prevents a unique derivative at that direction.

Eq.(3), p.835/PDF3, defines the Jaumann rate as `objective=ordinary+sigma*W-W*sigma`. Using this fragment directly as an ordinary stress rate requires zero spin. The paper's simple-shear examples cannot be claimed reproduced by that restriction.

## Printed conflicts requiring resolution

1. **Sign convention:** p.835/PDF3 assigns negative signs to tensile stress and elongative strain/rates. Yet Eq.(1), p.834/PDF2, defines stretching by the positive symmetric velocity gradient, and the triaxial compression recipe in Section 3.3.1, p.846/PDF14, prescribes axial stretching `-1` with confining stress `+100 kPa`. The fragment retains abstract source signs. Choosing positive compressive stress with `D_source=-D_Atlas` may follow that operational example, but would be an inference that conflicts with the prose. No canonical sign map is selected.
2. **Calibration coefficient:** p.842/PDF10, Eq.(25) row 2 requires `c3=c2` when initial Poisson ratio is zero; Eq.(31) agrees. At the same limit, the printed numerators in Eqs.(27) and (28) have opposite signs with the same denominator. For `Rf=3`, `vf=.5`, the denominator is nonzero and the two ratios are nonzero opposites. This cannot satisfy row 2. The helper exposes that counterexample; it does not implement a corrected parameter converter. The prose definitions of the Poisson ratios also lack the minus sign suggested by the operational loading convention.
3. **Friction-angle formula:** Eq.(33), p.843/PDF11, prints `arcsin((Rf+1)/(Rf-1))`. For `Rf>1` its argument exceeds one (`2` at `Rf=3`), leaving no real result. The reciprocal is not silently substituted. An authoritative resolution remains necessary.

These observations were checked on rendered original pages, rather than inferred from OCR. A limited web search did not identify a correction to adopt; it does not establish that no erratum exists. Resolving one conflict does not resolve the others or establish a reproducible source implementation.

## Calibration identity

Table II, p.843/PDF11, gives **Karlsruhe medium sand**:

| Specimen | Relative density | c1 | c2 | c3 | c4 |
| --- | --- | --- | --- | --- | --- |
| Loose | .10 | -69.4 | -673.1 | -655.9 | 699.6 |
| Dense | .95 | -101.2 | -962.1 | -877.3 | 1229.2 |

These sets are not Wichtmann Karlsruhe fine-sand calibrations, VW96 defaults, or interpolation endpoints for an inferred density law. Table II has unequal `c2` and `c3`, so the zero-initial-Poisson-ratio specialization must not be imposed on them automatically.

## Integration and verification requirements

Section 3.3.1, p.846/PDF14, uses forward Euler, solves Eq.(24) for radial stretching at each constant-confinement step, and inserts it into Eq.(23) for axial stress rate. Rate independence does not remove integration error. Atlas's adaptive midpoint, tolerances, transaction semantics and control solver would be project choices, requiring declared step refinement and source-path comparisons. There is no incremental plastic yield activation or return map to supply from this stress-only equation.

The [Python tests](../../tests/test_wu_bauer_original.py) compare the typed law with independent Cartesian matrix products, rotation, positive scaling and separately written axisymmetric Eqs.(23)–(24), p.841/PDF9. They also expose zero-direction nonsmoothness, reject undefined inputs and retain numerical counterexamples to the printed calibration formulas. These tests verify the transcription's algebra, not source sign resolution, admissibility, figure trajectories or experimental agreement.

Before public admission: resolve the sign/calibration conflicts, reconcile Appendix I, define physical domain and initialization, declare integration/spin scope, reproduce source-specific paths, obtain independent references and scientific review. No public model count or validation status changes in this extraction.
