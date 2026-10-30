# Terracotta author-source audit — 30 October 2026

Status: **partial source extraction; unresolved; not independent review**. This audit records requirements for TC-01–03. It does not establish journal/code equivalence, numerical correctness or experimental validity. The initial findings used read-only inspection. The subsequent [research transcription](terracotta-2024-transcription.md) now includes hash-checked execution of the unmodified author RHS to generate frozen numerical references; no author solver source is bundled into the atlas.

## Pinned evidence

All repository evidence is at revision [`a4039d0124d8ff61e766f5201f44ddc163c4cff5`](https://github.com/MaxWiebicke/Terracotta-pq/tree/a4039d0124d8ff61e766f5201f44ddc163c4cff5). The repository [license](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/LICENSE) is MIT; publications/data have separate terms.

| Source | SHA-256 of inspected bytes |
| --- | --- |
| [Functions](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/code/Terracotta_functions.py) | `6f1d7bbc9e805cfa38230b1277a1b55a02f27ab4581e973f5a61c495262a0711` |
| [Example driver](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/code/Terracotta_main.py) | `62c45ae3ba7d556956e4e29d940371a5f1a39b8feeb0d1a0c59db80fbe44a888` |
| [Author equation summary](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/images/theModel.png) | `e019012545c5fb0bb80c8f95bad68d35f458c9094ea471d8f42616a170dcc071` |

The original journal source remains [Wiebicke & Einav (2024)](https://doi.org/10.1016/j.jmps.2024.105789). The initial extraction used the repository assets; the follow-up below records the journal passages subsequently located. Complete visual/equation cross-checking remains outstanding. The README cites an earlier SSRN version. Source locators below refer to the pinned code, not purported journal equation numbers.

## State and output requirements extracted

The author summary expresses pressure and signed deviatoric stress algebraically in elastic volumetric/shear strain, solid fraction, mesoscopic temperature and imposed strain rates. Its elastic terms are `pe = phi^6 (K ev_e^2 + 3 G es_e^2)/2` and `qe = 3 G phi^6 ev_e es_e`. The other terms are `pd = 2 alpha Tm Dv/Gamma`, `qd = 2 gamma Tm Ds/Gamma`, and an isotropic contribution `Tm^2/Gamma` to pressure. Thus total stress is an observable depending on both state **and loading rate**.

The four core evolving quantities under prescribed invariant strain rates are elastic volumetric/shear strain, `Tm` and `phi`. The summary gives `dTm/dt = alpha Dv^2 + gamma Ds^2 - eta Tm^2`, `dphi/dt = phi Dv`, and elastic rates equal imposed rates minus coupled plastic rates. It defines a symmetric transport matrix, with the pressure scale `p1 phi^Lambda` factored outside. `plastCoefficients` (lines 78–106) instead incorporates that scale into its coefficients; compare complete products before treating their definitions as a discrepancy.

The implementation evolves ten quantities: total invariant strains, elastic stresses, elastic strains, temperature, viscous stresses and solid fraction (`stateVarRatesComplexLoading`, lines 148–236). Differentiating algebraic stresses introduces strain acceleration and previous-rate/outer-step inputs. The minimal four-state, prescribed-strain-rate ODE avoids that numerical differentiation; this is an implementation inference from the author summary, not yet a reviewed journal transcription. A [generic algebraic-output/mixed-component-control contract](../TIMED_SCHEDULES.md) is now implemented and analytically tested on synthetic laws. Applying it to this original signed invariant formulation still requires its explicit kinematic scope and source-matched reference evidence.

`eps2pq` (lines 9–15) uses `ev = e1 + 2 e2` and `es = 2(e1-e2)/3`. The invariant shear strain and signed stress must retain compression/extension conventions. A generic nonnegative tensor norm cannot silently replace them.

## Units and initialization evidence

The example labels elastic moduli in kPa, `alpha`/`gamma` in K·s, `eta` in 1/(K·s), and `Gamma` in K²/kPa. `p1` must have pressure dimensions from its use in `p1 phi^Lambda`, despite an incomplete example comment. Preserve the mesoscopic temperature scale; a K label is not evidence that it is ordinary measured temperature. Confirm all units against the journal before transcribing defaults, and explicitly convert kPa-based coefficients to SI.

`initialElasticStrains` (lines 62–76) inverts elastic stresses with a square root and divides by elastic volumetric strain. This needs admissibility/root-branch checks, not a zero-state default. The example starts at isotropic elastic pressure 100 kPa, zero viscous stresses/temperature and `phi = 0.423`. A nonzero-temperature total-stress initialization additionally depends on the initial prescribed rate. The transport matrix's admissible domain must be checked from the source; `plastCoefficients` currently terminates the process on a negative determinant. The atlas must instead report a transactional numerical/domain failure.

## Findings to reconcile before admission

| ID | Observed source evidence | Consequence / required resolution |
| --- | --- | --- |
| TC-A01 | `TmRate` (139–146) uses the unhalved source/sink expression; `funcComplexLoading` (238–314) divides it by two | Mixed-control equations and state evolution disagree as written. Resolve against journal equations; record any reference-code correction explicitly rather than matching one branch silently. |
| TC-A02 | The example's initial `stress` adds `Tm^2` to both array components, while its plotting expression adds `Tm^2/Gamma` only to pressure | The supplied zero-temperature start masks this difference. Do not infer general initialization from that expression. |
| TC-A03 | Viscous stress rates use previous strain rate, outer `dt` and local time; `ratesIntegrationScipyCL` restarts each interval on `[0,dt]` | Reference trajectories may depend on this outer partition. Separate algebraic law from integration procedure; record reference step policy and run refinement before setting comparison tolerances. |
| TC-A04 | The equation summary's viscous outputs depend directly on imposed rate | A rate change can produce a jump in observed total stress while core state stays continuous. The timed schedule must distinguish state continuity from observable continuity. |
| TC-A05 | `ratesIntegrationScipyCL` (316–335) selects BDF without explicit tolerance overrides | Record solver defaults/version in any reproduction. The new explicit midpoint engine fixture is not evidence of Terracotta stiffness suitability or BDF parity. |

## Next evidence

Retrieve and inspect the complete journal equations and parameter/initialization passages, attach exact locators, and reconcile TC-A01–05. Then transcribe a source-pinned original invariant model with explicit observables. Compare prescribed-rate paths first, followed by genuinely matching mixed controls, creep and relaxation with source-matched durations and parameters. Keep author-code agreement, independent equation review and experimental validation as separate evidence gates.

## Journal follow-up

The [journal full text uploaded by Itai Einav](https://www.researchgate.net/publication/382467665_A_simple_hydrodynamic_model_for_clay) provides these additional locators:

- Section 4.5, Eq. (36), p. 10: the temperature-rate expression has no factor of one half, supporting TC-A01's identification of a discrepancy in the mixed-control routine.
- Section 6, p. 13: BDF and the outer-step acceleration approximation are stated numerical choices, supporting TC-A03/05.
- Appendix B, p. 26: Figure 1 is the simplified variant; the fuller variant retains an elastic contribution to thermodynamic pressure and changes plastic transport coefficients. Pin **Figure 1** as the immediate target; Appendix B requires a separate variant identity.
- Appendix C, p. 27: the dimension table supports the time/temperature extension.

These targeted text checks advance TC-01 but do not close equation extraction, parameter reconciliation, numerical reproduction or independent review.

## Research transcription follow-up

A [declarative Figure 1 research draft](terracotta-2024-transcription.md) now has four scalar states, algebraic outputs, explicit axisymmetric kinematics and five prescribed-rate author-RHS reference histories in native/Wasm. Its dossier records SI conversion, rounded `p1`, admissibility guards, a boundary adaptation and the precise remaining TC-A01–05 limitations. This does not close independent review, original outer-step reproduction or mixed-control/creep reference comparisons.
