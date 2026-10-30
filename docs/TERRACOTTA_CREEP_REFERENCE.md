# Terracotta Figure 1: prepared creep reference

The [separate scalar reference](../tools/reference_terracotta_creep.py) now checks the restricted Terracotta law under constant **total** pressure and signed q. It uses only the Python standard library and explicitly transcribed scalar equations from [Wiebicke & Einav (2024)](https://doi.org/10.1016/j.jmps.2024.105789), Figure 1/Eqs.23–24,29–32,36–38,42–43,48,51. It calls neither the Atlas expression interpreter/integrator nor the author implementation. This is a separate mathematical implementation by AI, not independent scientific authorship, an author-code creep reproduction or experimental validation.

## Problem and reference

For positive mesoscopic temperature, the total-stress equations give rates directly:

```text
Dv = Gamma (P - pe - Tm^2/Gamma) / (2 alpha Tm)
Ds = Gamma (Q - qe) / (2 gamma Tm)
```

Here P/Q are held total invariants; pe/qe are recalculated from the current elastic strains and current solid fraction at every stage. Substitution into all four original ODEs, including the **unhalved** temperature evolution, avoids differentiating the stresses or invoking the author mixed-control residual discrepancy. Accumulated volumetric/shear strains are integrated alongside the four material states. The rate inversion is singular at Tm=0; such a hold is rejected without a floor. Conditioning and stiffness near that boundary remain limitations.

Three preparations start from the same 100 kPa isotropic, phi=.423, Tm=0 state and the rounded author-code SI parameters. For 10 seconds they impose `(Dv,Ds)=(0,2e-5)`, `(0,-2e-5)`, or `(6e-5,0)` per second. Preparations use RK4 at 1000/2000/4000 steps and check the exact temperature-production and density solutions. Each hold then freezes the finest prepared state and accumulated strain, captures total P/Q using that state's preceding rates, and holds them for 20 seconds. The algebraic initial hold rates recover the prescribed preparation rates.

The hold clock restarts at zero; preparation occupied the preceding 10 seconds. Figure 1 is autonomous for this scope. This is a **frozen-preparation comparison** that isolates hold integration. The native solver does not repeat preparation here; an end-to-end preparation study remains separate.

All three holds produce nontrivial creep. The [frozen reference](../tests/reference/terracotta-2024-scalar-creep.json) retains eleven observations per case, three RK4 grids (128/256/512 steps per two-second observation interval), and first/last-pair state/strain/rate differences. Explicit midpoint at 2048 steps per observation interval supplies a second integration-method check. Agreement thresholds are stated numerical study criteria, not rigorous global error bounds or a claim of fourth-order convergence at roundoff. Full journal reconciliation remains open.

## Native comparison and bounds

The [study runner](../tools/terracotta_creep_study.py) executes three native relative tolerances, `1e-4`, `1e-6`, `1e-8`, with absolute scale fraction `1e-11`. Every run uses identical explicit frozen initial state/strain/rate and parameters for its case. All three normal stress components are held, and all shear strain components remain zero. No special Terracotta C++ kernel is used.

All nine runs complete. Every non-roundoff error channel improves on the declared observation grid: four material states, strain, sampled rate, and elastic pressure/q. At the finest settings, maximum absolute strain error is approximately `4.86e-9`, rate error `3.96e-10 /s`, elastic-stress error `.00635 Pa` and held total-stress residual `1.02e-6 Pa`. These describe this three-case study, not general model accuracy.

Acceptance bounds are componentwise: state `[2e-9,2e-10,1e-7 K,1e-8]`, strain `1e-8`, sampled rate `1e-9 /s`, elastic pressure/q `.01 Pa`, and held total pressure/q `1e-4 Pa`. Non-roundoff error channels must improve at both refinements. No extrapolation, time sorting or partial failed-run substitution is allowed.

The verifier checks the entire nine-run matrix, explicit request/response metadata, runtime catalogue identity, exact observation/boundary ordering, finite arrays, initial-state consistency, stress tensor/invariant consistency and finite accepted diagnostic norms. Native stress-controlled transition rates are deliberately exported as null by the generic driver; the verifier checks that mask and compares regular sampled rates. Retained response hashes and scalar recomputation protect against altered grids, metrics, settings, diagnostics and failures.

## Reproduce and limits

```sh
python -m tools.reference_terracotta_creep \
  --model-definition models/research/terracotta-2024-fig1.json \
  --output /tmp/terracotta-creep-reference.json
python -m tools.terracotta_creep_study \
  --reference /tmp/terracotta-creep-reference.json \
  --solver build/atlas_research_solver --output /tmp/terracotta-creep-study.json
ATLAS_RESEARCH_SOLVER=build/atlas_research_solver \
  python -m unittest tests.test_terracotta_creep -v
```

The [retained manifest](../catalogue/investigations/terracotta-creep-v1/manifest.json) pins reference/implementation inputs, all nine native responses, summary and test evidence. That native-only milestone reused the existing matching research binary; no native build, external DLL/Fortran execution or experimental-data redistribution was required. CI's existing CTest Python discovery includes these tests and supplies the research solver path.

This advances numerical creep verification and TC-05 while preserving candidate/draft status. External source-matched creep histories, independent scientific equation review, full journal/author reconciliation, broader initial/rate/domain coverage, applicable clay experimental comparisons remain open. The original axisymmetric scope and the twenty-model full-3D gate are unchanged.

## Native/Wasm prepared-creep verification

The [paired C-ABI runner](../tools/test_terracotta_creep_wasm.mjs) executes all nine frozen-preparation requests through both backends. The [reference verifier](../tools/verify_terracotta_creep_wasm.py) independently subjects each complete backend matrix to the componentwise bounds and refinement checks above. Pairwise differences must also stay below `1e-7 * max(1, abs(native))` for each sampled value; this is a parity criterion, not a physical accuracy bound. Iteration counts may differ.

[Retained evidence](../catalogue/investigations/terracotta-creep-wasm-v1/manifest.json) binds the requests, reference, model, verification tools and paired results; the paired report also records the exact native binary, Wasm loader and Wasm binary hashes. Existing matching builds were reused. These are Node-hosted Wasm C-ABI checks; an interactive-browser creep workflow remains separate. CI runs both commands after its existing research builds:

```sh
node tools/test_terracotta_creep_wasm.mjs --output /tmp/terracotta-creep-parity.json
python -m tools.verify_terracotta_creep_wasm /tmp/terracotta-creep-parity.json
python -m unittest tests.test_terracotta_creep_wasm -v
```
