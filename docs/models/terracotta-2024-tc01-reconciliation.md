# Terracotta TC-01: bounded reconciliation and precise visual-source gap

31 October 2026. No model admission, repository edits, build, native/Wasm call or author-code execution. Target: Wiebicke & Einav (2024), JMPS192,105789, [journal identity](https://doi.org/10.1016/j.jmps.2024.105789). The machine crosswalk records each expression's verification level and hashes the existing Atlas definition/dossiers. This packet advances a source gate; it does not close TC-01.

## Evidence obtained and limit

Read the PDF skill. Searched names and first-page extracted text of Downloads PDFs; no Terracotta journal PDF was identified. Existing receipts cover four other downloaded original papers, not this journal. Normal publisher PDF and author-upload PDF routes returned HTTP403. The [author-uploaded journal text](https://www.researchgate.net/publication/382467665_A_simple_hydrodynamic_model_for_clay) remains readable, but its extracted math cannot replace equation images. No journal byte hash, journal page rendering or verified journal inequality is claimed.

Independently visually inspected the locally retained pinned [author equation image](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/images/theModel.png). Its expressions match the named Figure1 research definition on inspection: elastic stresses; viscous stresses; unhalved temperature rate; solid-fraction rate; coupled plastic strain-rate action; factored a,b,c. This verifies the image-to-schema transcription, not journal equivalence. Source bytes remain private/excluded.

## Figure1 versus AppendixB: do not merge

| Item | Figure1 / current research draft | AppendixB verification required |
|---|---|---|
| Total pressure | pe+pd+pTm | p26 B.1 additionally includes elastic thermodynamic pressure pTe |
| Plastic transport | Figure1 factored a,b,c with common 1/pc outside matrix | p26 B.2–B.4 revise dimensional coefficients; inspect numerator/denominator powers, not merely add pTe to output |
| Viscous transport | Direct algebraic rate-dependent stresses | p26 text says these remain unchanged through Eq31 |
| Calibration | Rounded author-code kaolin preset | Table1 p14 and FigB.19 p26 must identify exact material/preset and full initialization |
| Temperature, density, kinematics | Four-state Figure1 signed axisymmetric ODE | Equivalence of every retained equation is pending complete visual source comparison |

The [journal text, Section4.6 p10 / AppendixB p26](https://www.researchgate.net/publication/382467665_A_simple_hydrodynamic_model_for_clay) identifies Figure1 as a simplification, requires changed plastic coefficients in the full version and illustrates only particular drained/undrained comparisons. Similar plotted responses are not identical constitutive equations. No AppendixB expressions are admitted from extracted text in this packet.

## Parameter and unit crosswalk

Here the independent dimensional derivation follows the inspected author image and current schema, rather than claiming a newly verified journal table. Strains, phi,M,omega,Lambda are dimensionless; pressure and K,G,p1 are Pa; Tm carries its mesoscopic K normalization. Because Tm_dot has K/s, alpha and gamma have K*s and eta has 1/(K*s). The pressure term Tm^2/Gamma requires Gamma in K^2/Pa. Thus source Gamma=1 K^2/kPa converts to 0.001 K^2/Pa. Intrinsic K/G and p1 expressed in kPa convert by multiplying 1000; alpha/gamma/eta do not change in that pressure conversion. AppendixC p27–28 is the required visual unit-table check.

Crucially, Atlas a,b,c have units 1/(K*s) because pc is factored outside. The author's `plastCoefficients`, lines78–106, embeds 1/pc, yielding 1/(Pa*K*s). Compare complete products before reporting a coefficient discrepancy. This is a representation difference, not a selected correction.

The current author preset is K=13e9 Pa,G=5e9 Pa,M=.73,omega=.6,p1=543e6 Pa,Lambda=10,alpha=gamma=6e5 K*s,eta=150/(K*s),Gamma=.001 K^2/Pa. The existing transcription records phi1=.267 from the rounded journal table; Eq43 implies p1=1000/phi1^Lambda Pa, which differs from rounded code p1. Keep both calibrations named; a page-image check must precede treating either as a final journal default. Numerical parameter bounds are Atlas guardrails, not source calibration intervals.

## Concrete source and numerical blockers

1. Minimum source packet: complete journal pages2 (Figure1),10 (Eqs36–38),14 (Table1),16 (Eq54/Table2),26 (B.1–B.4/FigB.19),27–28 (AppendixC). Then equations23–24,29–32,42–43,48,51 on their complete intervening pages; page numbers are exact where already established in retained dossiers, otherwise use equation locators rather than guessing pagination. Include captions/footnotes. A complete PDF is preferred to pin bytes.
2. Resolve strict versus nonstrict boundaries visually: transport determinant; elastic stability; Eq54 stress-ratio order. Current schema admits equality. Absence of an observed solver failure does not settle source admissibility.
3. Author-code temperature conflict is concrete: `TmRate` lines139–146 is unhalved; mixed-control line301 divides the whole expression by two. The image supports the former. Journal Eq36 p10 must still be visually checked. Do not overwrite the pinned source or silently regenerate mixed-control references with a patch.
4. AppendixB requires its own identifier, pTe derivation from Eq37, transport expressions, initialization inversion/domain and comparison evidence. Current Figure1 creep evidence cannot admit it.
5. Existing native/Wasm prepared-creep evidence freezes independently prepared initial states. A new end-to-end preparation/hold study should carry the computed preparation state and accumulated strain forward, capture hold P/Q at the explicit one-sided transition rate, then keep the full hold on the same trajectory. At Tm=0 stress inversion is singular: reject unsupported holds, with no hidden floor. Predeclare separate preparation and hold errors against independent full-path reference. At rate jumps retain state continuity and algebraic stress jumps; output left/right rate convention explicitly. This is a proposed next study contract, not a new scientific source claim.

TC-01 stays open. The smallest useful next action is obtaining the minimum journal page packet, then an independent visual equation audit. Existing creep, initialization and boundary tests should not be commissioned again as source reconciliation.
