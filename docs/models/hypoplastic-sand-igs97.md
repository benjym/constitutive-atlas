# Sand hypoplasticity with intergranular strain (IGS, 1997)

This is a **draft** extension of the [VW96 host law](hypoplastic-sand-vw96.md), not a reviewed scientific implementation. Model: [`hypoplastic-sand-igs97`](../../models/hypoplastic-sand-igs97.json). Roadmap: REV-05. The host dossier defines its nine parameters, density restrictions and Cartesian source conversion; those qualifications also apply here.

## Sources and formulation boundary

The original reference is [Niemunis & Herle (1997), pp. 279–299](https://doi.org/10.1002/(SICI)1099-1484(199710)2:4%3C279::AID-CFM29%3E3.0.CO;2-8). Full original-paper inspection remains outstanding. The implementation-author cross-check is numgeo's [2026-09 theory manual, “IGS Extension”](https://j-machacek.github.io/numgeo/2026-09/theory/constitutive-models/mechanical-models/hypo-igs.html#igs-extension). The previously cited August 2023 PDF returns HTTP 404 on 2026-10-30; its old equation numbers are not treated as verified locators.

The [source inventory](../../catalogue/source-audits/hypoplastic-sand-igs97-numgeo-2026.json) pins the inspected HTML hash and an author-code revision. The published `update_igs` routine updates and projects history before evaluating stress stiffness. Atlas integrates its continuous rate law with adaptive midpoint subdivision. These are different finite-increment algorithms; no direct external-code agreement is claimed. The source is inspected, not vendored or linked into Atlas.

This entry excludes ISA, generalized IGS, phantom elasticity, additional backstrain variables, stress projections, pressure cutoffs and finite-spin transport. Those choices require distinct variants and evidence.

## State, conventions and initialization

The 13 scalar state entries are effective stress `sigma[6]` (Pa), void ratio `e`, and symmetric intergranular strain `h[6]` (dimensionless). Both tensors use Mandel order `xx, yy, zz, xy, yz, xz`; physical off-diagonal components are multiplied by √2. Stress, strain increments and history are compression positive. To use a tension-positive reference, negate all three tensors, including history; the directional projection is invariant under the paired history/strain sign change. The nonlinear host vector changes sign with the stress-rate conversion.

Defaults are `sigma = 100 kPa I`, `e = 0.7`, `h = 0`. Zero history means erased directional memory and initially enhanced stiffness. It is an initialization choice, not a calibrated deposition history. A prescribed nonzero history must have the same frame, sign and Mandel convention as strain. The continuous physical history ball is `||h|| ≤ R`; the actual numerical admission band is described below.

## Additional parameters

| Parameter | Default | Meaning | Atlas bounds |
| --- | ---: | --- | --- |
| `R` | 0.0001 | Limiting history magnitude | 10⁻⁷–0.01 |
| `mR` | 5 | Reversal stiffness multiplier | 1–30 |
| `mT` | 2 | Orthogonal stiffness multiplier | 1–30 |
| `beta_r` | 0.5 | History mobilisation exponent | 0.05–5 |
| `chi` | 6 | Stiffness transition exponent | 0.1–20 |

All five parameters are dimensionless. These defaults are illustrative, not a fitted Wichtmann parameter set. The extra domain condition is `mR ≥ mT`; all host-law restrictions remain in force. Parameter bounds are Atlas input guards, not universal published validity ranges. `p_ref` scales numerical stress error and does not set material stiffness.

## Implemented continuous equations and source mapping

Let `L:D` be the linear part of the compression-positive host stress rate, and `N` its nonlinear vector, so the host rate is `L:D + N ||D||`. Atlas `linear` is `L:D`, `nonlinear` is `N`, and `linear_eta` is `L:eta`. Here `D` denotes the prescribed increment per unit normalized path coordinate; this schema-v0.1 law is rate independent and has no physical clock.

With `eta = h/||h||` when history is nonzero (zero otherwise), `r = min(||h||/R,1)`, `a = eta:D` and `w = r^chi`, Atlas uses:

```text
stress' = [w mT + (1-w) mR] L:D
          + w [(1-mT) L:eta + N] a       when a > 0
          + w (mR-mT) (L:eta) a          when a ≤ 0

h' = D - r^beta_r eta a                 when a > 0
h' = D                                 when a ≤ 0
e' = -(1+e) tr(D)
```

The two stress branches and history evolution map to the manual's IGS stiffness and evolution displays, respectively. Contracting its fourth-order operator gives the expressions above. At `a=0` both branch corrections vanish. At `h=0`, defining `eta=0` avoids division by zero and gives `stress'=mR L:D`, `h'=D`.

For saturated aligned loading the host response is recovered and `h'=0`. Saturated reversal gives `mR L:D`; saturated orthogonal loading gives `mT L:D`. Setting both multipliers to one does **not** recover the host for arbitrary unsaturated or misaligned history. At the limiting sphere, outward loading gives `h:h'=0`; reversal moves inward. Fixed-frame covariance requires rotating history along with stress and strain. These identities are checked separately from native execution.

## Numerical choices and failure behavior

The source's continuous mobilisation is `||h||/R`. Atlas caps it at one and admits `||h|| < 1.01 R` to tolerate discretization overshoot. It does not project history onto the sphere after each accepted step. The cap and 1% admission band are explicit numerical choices requiring review; the cap is tested inside that band. No claim is made that the band itself is a physical admissibility criterion.

The generic rate integrator uses midpoint step doubling with history error scaled by `R`, stress by `p_ref`, and void ratio by one. Failed integration rolls back the whole input state. No IGS-specific native kernel exists. Independent fixed-step RK4 uses the same declared continuous cap but a different integration algorithm; it does not normalize history after stages or endpoints.

## Numerical evidence and remaining review

[`tools/verify_igs.py`](../../tools/verify_igs.py) constructs the overlay in ordinary Cartesian matrices. Odd/even host-rate decomposition supplies the linear operator and nonlinear vector from the separately written VW96 Cartesian reference. It uses neither the DSL nor production tensor or integration routines. The host oracle is shared with the VW96 verification, so this does not provide independent authorship or an independent host-law derivation.

The suite covers three parameter sets (including equal stiffness multipliers), isotropic and sheared stress, zero/partial/saturated/reversed/mixed histories, both loading branches, all shear planes, oblique frame rotations, small cycles, mobilisation, reversal through zero history, orthogonal turns and invalid-state rollback. RK4 grid convergence and native agreement are separate gates; every refinement level is retained. Stress, void ratio and history have distinct declared absolute tolerances.

For collinear paths at the default `beta_r=1/2`, a separate analytical history reference resolves reversal at zero exactly. Unloading is linear until zero; subsequent aligned loading is obtained by inverting `-u-log(1-u) = -u0-log(1-u0) + length/(2R)`, where `u=sqrt(abs(h)/R)`. Bisection solves this monotone scalar equation without a time integration scheme. It is independent of stress and void ratio.

The [initial investigation](../../catalogue/evidence/hypoplastic-sand-igs97-investigation-v1.json) passes 299 of 303 cases. All 295 instantaneous rate, covariance, numerical-cap and rollback checks pass, as do four histories. Mobilisation, saturated reversal through zero, small cycles and large reversal fail the RK4 convergence gate at the maximum 4096 steps. The analytical history solution additionally confirms a native small-cycle discrepancy: the third segment differs by about 1.36×10⁻⁷ in Mandel shear history, about 103 times the declared path tolerance. The RK4 estimate differs from the analytical value by about 5.5×10⁻¹² there. Thus the native discrepancy cannot be attributed solely to the unconverged RK4 reference. It must be investigated, not accepted by changing tolerances. Square-root history mobilisation at zero history and reversal events are likely refinement difficulties. The native gate currently covers the 295 instantaneous checks only; history checks remain an explicit failing investigation.

Remaining requirements are full original-paper reconciliation, independent review of the source/sign/variant mapping, external-code execution with matched integration and projection settings, robustness near all domain boundaries, and calibrated cyclic experimental comparisons. Zero-spin covariance does not establish finite-rotation objectivity. CI results do not promote the draft status.
