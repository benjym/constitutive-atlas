# VW96: original-paper reconciliation

**Draft reconciliation; independent scientific review pending.** Source: von Wolffersdorff (1996), *A hypoplastic relation for granular materials with a predefined limit state surface*, pp. 251–271, [DOI](https://doi.org/10.1002/%28SICI%291099-1484%28199607%291%3A3%3C251%3A%3AAID-CFM13%3E3.0.CO%3B2-3). The complete user-supplied PDF is pinned in the [receipt](../../catalogue/source-audits/original-papers-2026-10-31.json). PDF page 1 is printed p. 251. The review covers the rate/kinematics definitions, Section 6, the parameter/example descriptions and Appendix C. PDF pages 12–14 and 20 were rendered and visually inspected. The full derivation in Sections 3–5 and Appendices A–B has not been independently reviewed.

## Equation mapping

The [existing transcription dossier](hypoplastic-sand-vw96.md) defines the complete equations in Atlas compression-positive Mandel coordinates. Its Fellin summary mapping now has these direct original-paper locators:

| Atlas quantity | Original locator | Reconciliation |
| --- | --- | --- |
| Stress and void-ratio rates | Eqs. (1)–(2), p. 252 | Objective stress rate and `e_dot=(1+e)*tr(D)` in tension-positive source convention; reverse both stress and stretching for Atlas |
| Complete stress law | Eq. (40), p. 262 | The linear `F^2*D` and `a^2*(hat:D)*hat` terms plus the nonlinear `fd*a*F*(hat+hatdev)*norm(D)`, all scaled by `fb*fe/(hat:hat)` |
| Friction factor `a` | Eq. (41), p. 262 | `sqrt(3)*(3-sin(phi))/(2*sqrt(2)*sin(phi))` |
| Shape `F`, normalized invariants | Eq. (42), p. 263; Eq. (C10), p. 270 | Same square-root expression and negative sign in the normalized cubic invariant as the current model |
| Limiting void ratios | Eq. (43), p. 263 | Common exponential pressure reduction for `ed`, `ec`, `ei` |
| Density factors `fe`, `fd` | Eqs. (44)–(45), p. 263 | `fe=(ec/e)^beta`, `fd=((e-ed)/(ec-ed))^alpha` |
| Barotropy `fb` | Eq. (46), p. 263 | Includes `(1+ei)/ei`, `(ei0/ec0)^beta`, the pressure power and the reciprocal bracket exactly as in the current model |

The original supports the **eight-parameter** host already implemented. The apparent seven-parameter version in Niemunis–Herle (1997), Appendix A, specializes the combined density factor to `beta=1`; see the [IGS source reconciliation](hypoplastic-sand-igs97-original.md). Do not substitute that specialization for arbitrary VW96 beta values.

The source explicitly gives void-ratio continuity, so it no longer needs to be described solely as a project inference. The footnote on p. 252 defines the Jaumann stress rate `T_circle=T_dot-W*T+T*W`. Atlas's ordinary-rate interpretation remains restricted to zero spin. Rate independence does not remove the need to integrate the equations accurately along a loading path.

## Isotropy, domain and numerical choices

Appendix C, p. 270, states that `cos(3*theta)` is indeterminate at isotropy, while `tan(psi)*cos(3*theta)` tends to zero and `F` tends to one. It also requires the computed cosine to lie in `[-1,1]`. Atlas assigns zero cosine below its declared small-invariant threshold; this threshold is a project numerical convention. It is not prescribed in the paper.

The current pressure floor, strict density guards, input bounds, midpoint integration, tolerances and rollback policy remain Atlas choices. This source review does not demonstrate admissibility of every state accepted by those guards, replace domain-boundary studies, or establish finite-rotation behavior. A critical-state surface is not an incremental plastic yield surface; this law has no plastic-multiplier return map.

## Keep calibrations separate

Table I, p. 264, gives the Hochstetten example:

| phi | hs | n | ec0 | ed0 | ei0 | alpha | beta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 33 degrees | 1000 MPa | 0.25 | 0.95 | 0.55 | 1.05 | 0.25 | 1.5 |

These values differ from both the current illustrative Karlsruhe defaults and the 1997 paper's seven-parameter host. SI conversion requires degrees to radians and MPa to Pa. The paper's Fig. 10 discussion uses initial void ratio `0.67` for triaxial compression with differing lateral stresses. Its later path study reports void ratio `0.633` after isotropic preparation to `tr(T)=-300 kPa`; initial and post-consolidation densities must not be interchanged. Full figure-specific path extraction and numerical reproduction remain pending. No new Wichtmann calibration or experimental agreement is claimed.

## Review status

This closes the specific primary-source access gap and reconciles the implemented rate-law factors against the original, with no model equation or default change. Existing project-authored Cartesian/native evidence remains scoped to its recorded parameters and cases; original-paper inspection alone adds no new trajectory or independent verification. Remaining REV-04 requirements include independent equation review, source-specific benchmark preparation, boundaries/singular limits and external reference/experimental comparisons. The formulation is not promoted automatically.
