# Terracotta Figure 1 — declarative research transcription

Status: **executable research draft, not independently reviewed or experimentally validated**. [Definition](../../models/research/terracotta-2024-fig1.json), [source audit](terracotta-2024-source-audit.md), [tests](../../tests/test_terracotta.py), [frozen author-RHS references](../../tests/reference/terracotta-2024-author-rhs.json). The browser catalogue retains candidate status. This restricted formulation does not count toward the twenty-model 3D release gate or close the SANISAND six-model gate.

The target is the simplified **Figure 1** formulation in [Wiebicke & Einav (2024), JMPS 192, 105789](https://doi.org/10.1016/j.jmps.2024.105789). Appendix B's extra elastic thermodynamic pressure and revised transport coefficients are a different variant. The [author equation image](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/images/theModel.png) was visually inspected; journal equations/units/parameter passages were checked in the [author-uploaded full text](https://www.researchgate.net/publication/382467665_A_simple_hydrodynamic_model_for_clay). Downloading the journal PDF was blocked by HTTP 403, so a complete visual journal check remains open. This is transcription evidence, not independent review.

## Kinematics and equation map

`formulation.kinematics: "axisymmetric_x"` declares fixed axial x and equal radial y/z strains, with zero off-diagonal components. `Dv=tr(D)` and `Ds=D:B`, with `B=diag(2/3,-1/3,-1/3)`, preserve signed compression/extension. For this scope `Ds=2(Dxx-Dyy)/3` and `stress=p I+q B`, so `stress:D=p Dv+q Ds`. Replacing signed `Ds` or `q` with a norm would change the model. Rotations, general 3D paths, finite deformation and poromechanics are unsupported.

The four persistent scalars are elastic volumetric strain `ev_e`, elastic shear strain `es_e`, mesoscopic temperature `Tm`, and solid fraction `phi`. Total stress is an algebraic observable. The common engine integrates these equations; there is no Terracotta-specific C++ mathematical kernel.

| Declaration | Expression / interpretation | Source locator |
| --- | --- | --- |
| `pe` | `phi^6 (K ev_e^2 + 3 G es_e^2)/2` | Eqs. 23–24; Fig. 1 |
| `qe` | `3 G phi^6 ev_e es_e` | Eq. 24; Fig. 1 |
| `pc` | `p1 phi^Lambda` | Eq. 43 |
| `a` | `sqrt(eta/alpha)` | Eq. 42, with `pc` factored out as in Fig. 1 |
| `b` | `-a qe/(M^2 pe)` | Eq. 48, same factorization |
| `c` | `sqrt(eta/gamma)/(M omega)+a/M^2` | Eq. 51, same factorization |
| elastic strain rates | `(Dv,Ds) - Tm/pc [[a,b],[b,c]] (pe,qe)` | Eq. 32; Fig. 1 |
| `Tm` rate | `alpha Dv^2 + gamma Ds^2 - eta Tm^2` | Eq. 36; Fig. 1 |
| `phi` rate | `phi Dv` | Mass balance; Fig. 1 |
| viscous `pv,qv` | `2 alpha Tm Dv/Gamma`, `2 gamma Tm Ds/Gamma` | Eqs. 29–31 |
| mesoscopic pressure `pt` | `Tm^2/Gamma` | Eq. 37 |
| total `p,q` | `p=pe+pv+pt`, `q=qe+qv` | Eq. 38; Fig. 1 |

Raw `a,b,c` above have units 1/(K s); the pinned author's `plastCoefficients` includes `1/pc` within each coefficient. Products agree. `observables` flatten stress first (six values), then pressure, signed q, elastic pressure/q, viscous pressure/q, and mesoscopic pressure. The new DSL constructor `sym(xx,yy,zz,xy,yz,xz)` takes six equally dimensioned scalars in Mandel order and supports Python, C++ and AD.

## SI parameters, scales and initial state

The default is the pinned author-code kaolin example, consistent with the rounded journal Table 1 values: `K=13e9 Pa`, `G=5e9 Pa`, `M=.73`, `omega=.6`, `p1=543e6 Pa`, `Lambda=10`, `alpha=gamma=6e5 K s`, `eta=150/(K s)`, and `Gamma=.001 K^2/Pa`. The latter converts the source's `1 K^2/kPa`. `Tm` uses the author's mesoscopic normalization; it is not ordinary measured temperature. Numerical parameter bounds are guardrails, not published calibration intervals.

Journal Eq. 43 and rounded Table 1 `phi1=.267` would give `p1=543109.483584174 kPa`. The author code instead rounds to `543000 kPa`; this draft uses that code value explicitly to make its reference comparisons reproducible. Do not silently mix the two presets.

The default initial state has `pe=100000 Pa`, `qe=0`, `phi=.423`, `Tm=0`; the positive elastic branch gives `ev_e=sqrt(2 pe/(K phi^6))=0.05182296052058317` and `es_e=0`. Accumulated laboratory strain is a separate zero-origin quantity. Changing parameters does not automatically reinitialize elastic strain to preserve pressure. General elastic initialization requires the positive root of `ev_e^2=phi^-6 [pe/K+sqrt((pe/K)^2-qe^2/(3GK))]`, followed by `es_e=qe/(3G phi^6 ev_e)` and admissibility checks. Nonzero-temperature initialization additionally requires a prescribed rate and its viscous/mesoscopic stress contributions.

Numerical state scales are `.05` for the elastic strains, `1` for solid fraction, and `1e-6 sqrt(Gamma p1)` for `Tm`; observable scale is `1e-4 p1`. These explicit numerical scales are not additional constitutive constants or fitted quantities. Scale/tolerance sensitivity remains required for later validation.

## Domain and controls

The declared domain requires positive elastic volumetric strain/pressure and `pc`, `0<phi<=1`, `Tm>=0`, a nonnegative plastic transport determinant, and elastic stability `K ev_e^2 >= 3 G es_e^2`. Parameter checks enforce the stress-ratio ordering in Eq. 54: `M <= sqrt(3G/K) <= M sqrt(1+sqrt(alpha/gamma) M/omega)`. Domain failures stop transactionally; no state clipping is used. The upper solid-fraction bound is an explicit atlas physical admissibility guard: the source warns that its power-law ICL can exceed unity at extreme pressure. This implementation stops rather than extending into that nonphysical range. Degenerate boundary states can still produce a singular mixed-control solve and fail.

The shared [timed driver](../TIMED_SCHEDULES.md) reduces axisymmetric control unknowns to one axial and one shared radial increment. Radial controls must match exactly; all shear components must prescribe zero strain. Initial strain/rate must obey the same symmetry. Material-stage rate symmetry is checked using 64 machine epsilons times the maximum component magnitude; this is a roundoff tolerance, not permission for a general 3D path. Python interpretation and compiled material updates both reject out-of-scope rates. The reduced driver is separately checked against analytical Maxwell stress-controlled creep.

## Reference evidence and its limits

[reference_terracotta.py](../../tools/reference_terracotta.py) imports the **unmodified, hash-checked** pinned author functions and calls `stateVarRatesComplexLoading`, the ten-state RHS, for constant prescribed-rate segments. It records five histories: low-rate undrained loading/relaxation; a tenfold rate jump/relaxation; undrained extension; isotropic compression; and oedometer loading. Mechanical parameters, initial state, stage rates/durations, source hash, Python/NumPy/SciPy versions, numerical settings and boundary policy are retained in the frozen JSON. No experimental records are bundled.

Each stage resets viscous stress algebraically to its new one-sided rate-dependent value and passes that same rate as `dStrainPrev`. The acceleration term is therefore zero within the stage. This is an **explicit adaptation of reference boundary handling**, not reproduction of `integratePath`'s first-step acceleration approximation or its default BDF tolerances. DOP853 at `rtol=1e-11` is cross-checked with BDF at `rtol=1e-10`, using recorded componentwise absolute tolerances. Maximum stress disagreement between those reference methods is below .002 Pa on these cases. This does not assess all stiffness regimes.

The atlas's backward-Euler schedule checks use `rtol=1e-6`, absolute scale fraction `1e-10`, and 100,000 allowed accepted substeps. Frozen-reference acceptance bounds are 100 Pa for pressure/q, `1e-5` for elastic strains/solid fraction, and `2e-6 K` for `Tm`. They are engine transcription checks, not experimental-error or calibration criteria. A separate case verifies improvement under tolerance refinement. Native and Wasm pass the same source-reference histories, and agree with each other within the stated script tolerance. Closed-form temperature production/decay and solid-fraction evolution, mixed radial stress control, invalid-state rejection, and out-of-scope rollback provide additional checks.

TC-A01 uses the unhalved journal Eq. 36 consistently; the author's discrepant mixed-control routine is not used for these references. TC-A02 uses pressure-only `Tm^2/Gamma`. TC-A03/04 are handled by the stated algebraic boundary adaptation. TC-A05 is recorded as a changed numerical policy. Author-code agreement remains shared-source evidence; independent equation review, original outer-step reproduction/refinement, mixed-control author reconciliation, external source-matched creep reference comparisons and experimental validation remain open. TC-01/05 are not closed by this evidence.

## Reproduce

Normal builds require only the existing C++/Python toolchain:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
python3 -m unittest discover -s tests -p test_terracotta.py -v
```

`build/atlas_research_solver` and `build-wasm/research.js` use a separate catalogue generated from `models/research`. They are not copied to the browser's executable model catalogue. The research JSON is downloadable as a draft.

To regenerate the author reference, obtain the pinned source from its recorded raw GitHub URL (the generator rejects any hash mismatch), install the recorded NumPy/SciPy versions in an isolated environment, and run:

```sh
python tools/reference_terracotta.py --author-functions /path/to/Terracotta_functions.py \
  --output tests/reference/terracotta-2024-author-rhs.json
```

The source is MIT licensed by its authors; consult its [pinned license](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/LICENSE). The generator executes only the explicitly supplied, hash-verified file. SciPy is an optional reference-generation dependency, not required for normal atlas tests or deployment. Frozen numeric outputs are committed for offline regression.

## Explicit initialization preprocessing

The [experimental recipe contract](../INITIALIZATION_RECIPES.md) now implements the positive stable inversion described above with explicit named parameters and total pressure/q, phi, Tm and rates. It checks model domain and initial-history guards, preserves provenance and exports arrays for the unchanged timed solver. Native one-sided rate-jump and closed-form temperature-decay checks supplement the existing histories; they do not close independent creep or full source-review gates.

## Separate prepared-creep reference

The [scalar creep investigation](../TERRACOTTA_CREEP_REFERENCE.md) now checks three frozen prepared states at constant total pressure/q against a separate RK4/midpoint implementation of the continuous Figure1 equations. Nine native runs refine all non-roundoff state/strain/rate/elastic-stress channels; source reconciliation, external author-matched histories, scientific review, experimental validation remain open. This is Terracotta-specific creep evidence, separate from the Maxwell engine fixture and earlier shared-author-RHS histories.

The [prepared-creep native/Wasm study](../TERRACOTTA_CREEP_REFERENCE.md#nativewasm-prepared-creep-verification) now covers all nine frozen-preparation cases through both C-ABI backends, each separately checked against the scalar reference. This does not close interactive browser creep, source reconciliation or experimental validation.
