# Perzyna COMSOL 6.3 — exact source and formulation contract

Owner: /root coordinator, 2 November 2026. Full assignment MODEL-perzyna-comsol63; this packet supplies E1–E3 inputs, not completed numerical or website delivery. No prior Perzyna model/owner was found on the live board or in models/ingestion. The original S-CLAY1 source acquisition remains separately blocked and unclaimed.

## Identity and source selection

Target `perzyna-comsol63-mises-perfect-zero-spin-ode`: the printed **Perzyna Model** in COMSOL Multiphysics 6.3 Structural Mechanics Module documentation, with isotropic linear elasticity, associative von Mises flow, constant positive yield stress, no hardening or thermal effects, infinitesimal strain and fixed spatial axes/zero spin. This is an elastoviscoplastic solid. It is a named vendor mathematical realization, without a claim of exact equivalence to every historical Perzyna formulation or to a vendor binary. Publisher/author is COMSOL; the inspected pages do not state a publication year or personal authors. Version is explicitly 6.3.

Primary pages:

- [Creep and Viscoplasticity](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.039.html): Perzyna images073–075; common flow057/059/060, Mises016/022, yield070.
- [Viscoplasticity settings](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_solid.07.024.html): associative von Mises, Perfectly plastic, No kinematic hardening, thermal None.
- [Linear Viscoelasticity introduction](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.029.html): elastic strain subtraction and isotropic elastic stress images008–010; stress-sign images002–004. Only the elastic relations are used; no viscoelastic branch is added.

`source-receipts.json` binds 20 private primary HTML/PNG originals. Three current HTML responses and Perzyna073–075 were acquired directly; 14 common/elastic PNGs were reused only after exact original-receipt hash verification from the existing private source inventory. All 17 equation images were visually read from a private white-background inspection sheet; original transparent PNGs are unchanged. Neighboring images081/082 were collected only as context and are not attributed to the selected law. No source PDF was used. Downloads filename search found no Perzyna/COMSOL source. Copyrighted originals/inspection sheets remain private; URLs and hashes are public receipts. No vendor code/binary was run.

**SC-PERZ-01, documented source discrepancy:** theory image073 explicitly gives λ=A(σe/σys−1)^n, conditioned by image074 F=σe−σys≥0. The settings paragraph instead lists A and a reference stress σref, and omits n. This packet selects the printed mathematical law and its yield-stress denominator; σref is not a parameter of this realization. The exponent n comes from the printed equation. The UI-control inconsistency is retained, not silently corrected or interpreted as an independent reference-stress law. The source mapping requires separate review before compiled qualification and final E5 acceptance.

## Complete equation and v0.3 crosswalk

Let ε be total infinitesimal strain, vp its permanent deviatoric part and α accumulated equivalent permanent strain. With elastic strain e=ε−vp, define s=2G dev(e), σ=K tr(e)I+s and q=√(3s:s/2). For positive K,G,Y,A and n≥1, set λ=A[max(q/Y−1,0)]^n. Then ε̇=D, vṗ=(3/2)λs/q when q>Y and zero otherwise; α̇=λ.

| Source locator | Quantity | Exact declarative mapping / units |
| --- | --- | --- |
| theory029 introduction/008–010 | Elastic strain and isotropic stress | `eps-eps_vp`; observable dry total Cauchy stress, Pa |
| theory039 image016 | von Mises equivalent stress | `sqrt(1.5)*norm(2*G*dev(eps-eps_vp))`, Pa |
| theory039 images070/073/074 | Yield and rate | `A * max(q / sigma_y - 1, 0) ** n`; 1/s |
| theory039 images022/057/075 | Associated deviatoric flow | `1.5 * lambda_vp / max(q,sigma_y) * sdev`, 1/s |
| theory039 images059/060/073 | Accumulated equivalent rate | `alpha_dot=lambda_vp`; dimensionless α |
| settings Plasticity Model | Perfect associative Mises | Constant Y, no evolving strength/back stress |
| theory029 images002–004 | Source tension-positive signs | Simultaneously negate stress, strain and vp to compression-positive Atlas convention; q/α unchanged |

The denominator `max(q,Y)` does not regularize active flow: when q>Y it equals q, while λ=0 otherwise. It defines the source-consistent zero-flow product at q=0 without evaluating 0/0. Equality q=Y has λ=0. No clipping, shifted yield, stress offset, plastic projection or hardening is introduced.

Five parameters in order K,G,Y,A,n: moduli/yield in Pa, A in s⁻¹, n dimensionless. Project illustrative values are 20 MPa,10 MPa,0.1 MPa,0.002 s⁻¹,2. These are not material calibration or vendor defaults. The declared exponent interval [1,8] is an explicit regular-exponent project restriction, excluding 0<n<1; it is not attributed to the source. Other finite parameter bounds are executable guards, not a qualified Cartesian accuracy envelope. A and Y have distinct roles: the normalization couples Y to both onset and rate, unlike an independently normalized Chaboche law. At n=1, equivalence to Bingham requires η=Y/A; holding A constant while changing Y does not hold that viscosity constant.

State layout ε6,vp6,α1 has 13 persistent components. Mandel ordering is [xx,yy,zz,√2xy,√2yz,√2xz]. ε/vp transform as symmetric spatial tensors and α as an invariant. Scalar products are physical tensor contractions in this encoding. Rate-independent changes of basis are supported; finite-rotation transport is excluded. `formulation` declares physical_time/ode, small_strain_3d, fixed_spatial, objective_rate:none, compression-positive stress/strain, and observable total Cauchy stress. There is no pore-pressure equation or effective-stress reconstruction.

Explicit initialization supplies all 13 state components, all five parameters, physical start time and six-component rate/loading context. Stress is calculated from elastic strain, not supplied independently. vp is traceless within the declared 1e−10 numerical tolerance; α≥0. An initial necessary history condition α+1e−10≥√(2/3)||vp|| is enforced. These checks do not prove a preparation history; arbitrary specimen preparation is not inferred. An overstressed initial state is valid and necessary for relaxation; imposing q≤Y would erase viscous behavior. The zero state is an explicit example, not an automatic default. Nonzero memory must be retained in restart; α cannot be recovered from current vp after reversals.

## Integration and transactional contract

The source law is a physical-time ODE, not a strain-path fraction law or rate-independent return map. The project targets the existing versioned physical-time-v2 **backward-Euler schedule** API. The direct midpoint time API is outside the proposed approval scope. All state components are solved together at the endpoint; no constitutive history is updated in place. Stress-hold constraints, strain holds and piecewise constant six-component strain rates are distinct mechanical experiments. No numerical equivalence to COMSOL's undisclosed implementation is promised.

Accepted increments commit ε,vp,α and time/rate/control context together. Repeated trials start from the same committed parent. Any failed entire caller advance returns the original complete parent; no accepted internal substep may leak. Restart retains full state, time, parameters and current controls. Public history replay must bind model/engine/protocol identities. Rate changes occur at explicit segment boundaries; state is continuous and left/right rate records may share a time. No instantaneous strain/stress jumps, hidden history resets or event interpolation are added.

At D=0 an above-yield deviator relaxes toward q=Y; mean stress remains unchanged. At/below yield the hold is stationary. Under fixed above-yield stress, constant λ produces steady creep. Zero/hydrostatic stress has zero flow. Reversal can cross the elastic interval before opposite flow; α remains nondecreasing. These statements are mechanical source-law consequences, not proof of arbitrary controller stability. General mixed-control paths, FE tangents, finite rotation, thermal activation, damage, hardening and pore coupling need separate qualification and are excluded from the initial website scope.

Native/Wasm reference/step/refinement budgets must be frozen before execution. Bingham's accepted maximum-step convention may be used as a prospective conservative numerical choice, but cannot transfer its accuracy evidence to nonlinear Perzyna. Source-valid parameter bounds do not promise useful accuracy for every custom history.

## Independent reference derivation

For a strain hold with q0>Y, u=q/Y−1 satisfies u̇=−cu^n, c=3GA/Y. For n=1, u=u0 exp(−ct); otherwise u=u0[1+(n−1)ct u0^(n−1)]^(−1/(n−1)). The deviator maintains direction. Recover vp by elastic compliance and α increment=(q0−q)/(3G). Mean stress and total strain are unchanged. Creep at fixed stress has constant λ and vp increment=(3/2)tλs/q. These are independently integrated scalar laws, not production BE replays.

`oracle.py` also integrates six stresses and α with a separate explicit RK4 balance, then reconstructs vp by compliance. This uses different state/equations/integration than the production 13-state BE solve. A doubled reference grid must converge before noncoaxial histories become acceptance values. Independent equation/rotation/dissipation/initialization checks and interpreter comparisons are recorded separately. Backend agreement will not substitute for these references.

## Status and next action

Candidate `candidate.json` validates and generates through the current unmodified v0.3 compiler; generated-v1 is an isolated transcription witness. No native/Wasm build or material call has occurred. Freeze the source mapping, reference evidence and full numerical policy, obtain separate review of SC-PERZ-01, then qualify exact bytes under an explicit serial execution handoff. Final scientific approval, public profile integration, package/browser and live E8 remain open.

Actual source-check outcome: check_source_v2.py passes180analyticalcases/1106checks, including original-equation derivatives, dissipation, trace, semigroup, fixed-stress creep, explicit initialization/history and passive rotation. SOURCE-CHECK-ATTEMPT1.json and the original check_source.py retain an initial harness positional-parameter mistake; v2 fixes only that call, with unchanged candidate/oracle/gates. Public profile is a packet draft; its proposed controls must be reconciled to actual E7 UI before integration.
