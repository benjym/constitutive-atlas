# OCC log-recovery endpoint contract, proposal v1

DESIGN-occ-control-selection-v1, 1 November 2026. This is a proposed complete fixed-frame invariant continuation and numerical selection for the full Original Cam Clay law, not an admitted model or an original author algorithm. It includes interior recovery, both signed axial branches, arbitrary fixed-frame deviator directions, the hydrostatic corner, critical state, dilation/softening, unload/reload and reversal. Numerical existence and smoothness of a strain endpoint map do not imply unique equilibrium under stress/mixed controls.

## Source identity and scope decision

Use the exact disclosed Schofield/Wroth electronic transcription retained privately at `.local/private-sources/original-cam-clay/schofield-wroth-electronic-transcription.pdf`, SHA256 `638e0ee7dc238ae8922b79983433be7d12ad30450098efe395968f7eeed13cb2`. Its work is attributed to the 1968 book; the artifact is a 2005 electronic transcription, with first-edition fidelity unverified. Source selection does not claim authenticated 1968 scan bytes. Preserve old receipts and reports.

Chapter6 pp94–99 supplies recovery, zero recoverable distortion, packing and the yield surface. Section6.11 p114 explicitly connects OCC Eq6.17's invariant generalization to AppendixC's Mises construction. AppendixC pp216–218 supplies invariant geometry; its Granta-gravel pressure-history rule is not imported. This proposal combines that geometry with Chapter6's OCC packing and recovery. It is identified as a **source-derived invariant continuation**, not a literal complete 3D author implementation. p114 was visually rechecked for this design; previous reviews inspected governing Chapter6/AppendixC pages.

Use infinitesimal strain, fixed Cartesian frame/zero spin, compression-positive effective Cauchy stress and SI units. Symmetric tensors use Mandel order `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`. No finite-rotation transport, pore-pressure evolution, creep, finite shear modulus, MCC ellipse, tension cut-off or smoothing is supplied.

## Continuous relation and corner interpretation

Let `p=tr(sigma)/3>0`, `s=dev(sigma)`, `q=sqrt(3*s:s/2)>=0`, `v=1+e>0`, `x=ln(p/p_ref)` and `d=lambda-kappa>0`. The packing coordinate is

```
w=v+kappa*x
c=ln(pc/p_ref)=1+(Gamma-w)/d
F=q+M*p*(x-c)<=0
```

`Gamma` is the critical-specific-volume intercept at the explicit reference pressure. M>0, p_ref>0, 0<kappa<lambda. Under a change of reference pressure r1 to r2, Gamma2=Gamma1-lambda*ln(r2/r1); this changes no physical prediction. Persistent stress and v determine packing/pc. No redundant independently initialized pc is silently repaired.

Recoverable distortion is zero. Bulk recovery is `dv_el=-kappa*d ln(p)`. For a smooth plastic direction, with dimensionless multiplier L>=0,

```
dEv = kappa/v * d ln(p) + L*A
A = M*(1+x-c)
dD = L*3*s/(2*q)
dw = -v*L*A
L*F=0
```

D is deviatoric strain, Ev its volumetric companion. At q=0, p=pc, p101's normal cone is used: `A=M`, `sqrt(2/3*dD:dD)<=L`, `dEv_p=M*L`. The scalar L is summed mechanism magnitude; corner power is `M*p*L` and can exceed `M*p*sqrt(2/3*dD:dD)`. Smooth absolute-distortion dissipation is not imposed as an equality for interior cone directions. This preserves source p101 isotropic compaction. AppendixC10 is treated as the limiting smooth normal, not as a deletion of the corner cone. Continuous bulk/packing and both signed axial smooth branches remain unchanged.

## Project finite-step equations

For incoming `(sigma_n,v_n)` and prescribed symmetric strain increment de, let `E=trace(de)`, `D=dev(de)`, `r=sqrt(2/3*D:D)`, `x_n=ln(p_n/p_ref)`. Choose backward Euler volume and endpoint plastic packing with **exact log-pressure recovery**:

```
v = v_n/(1+E)                         [requires 1+E>0]
E = (kappa/v)*(x-x_n) + L*A
w-w_n = -v*L*A
```

The last equation is algebraically implied by the first two and w's definition, because `v-v_n=-v*E`. This is a first-order mixed finite discretization; it is not exact exponential volume bookkeeping, original author software, or a published return map. Under internal refinement it targets the continuous source volume law. The source's exact elastic v-ln(p) recovery is preserved at every discrete elastic step. The common adaptive residual integrator may subdivide and uses its normal transaction/error semantics; an unsplit endpoint is not generally equal to a subdivided endpoint.

Define the hydrostatic yield-intercept log-pressure at the new v:

```
x_c=(Gamma+lambda-kappa-v)/lambda
alpha=kappa/v
beta=M*r/(lambda-kappa)
x_s=(E+alpha*x_n+beta*(Gamma-v))/(alpha+beta*lambda)
x=min(x_s,x_c)
p=p_ref*exp(x)
Q=M*p*lambda/(lambda-kappa)*(x_c-x) >= 0
```

For nonzero r:

- If x_s<x_c, smooth plastic: L=r, q=Q and `s=(2/3)*(Q/r)*D`.
- If x_s>=x_c, corner: x=x_c, q=0 and `L=(E-alpha*(x_c-x_n))/M >= r`. At equality this matches the smooth limiting normal. The strain deviator can point anywhere within the corner cone.

Proof of the scalar solve: on the smooth surface, `A=M*(lambda*x+v-Gamma)/(lambda-kappa)`, so the bulk/flow equation is linear in x with strictly positive coefficient `alpha+beta*lambda`. When its root exceeds x_c, the displayed expression for L satisfies L>=r. Thus the endpoint exists uniquely for nonzero distortion under these project equations, even on a dry-side dilative branch; no negative hardening modulus is suppressed. The actual pressure must remain representable and the supplied state/parameters admissible.

## Interior stress selection for zero distortion

At r=0 and x_s<=x_c, take L=0, x=x_s, and select the closest deviatoric stress to s_n in Frobenius norm among stresses with norm-equivalent q<=Q:

```
s = s_n * min(1,Q/q_n)  if q_n>0
s = 0                  if q_n=0
```

This unique Euclidean projection is a disclosed **strain-interface selection**, not recovered shear elasticity or a source-determined inverse relation. It retains old deviatoric stress whenever admissible; it permits a zero-strain stress probe reducing its magnitude when the old stress becomes inadmissible under a volume change. Packing remains fixed. It is not a rule to force pc=p. At r=0 and x_s>x_c, use the plastic isotropic corner, s=0 and L>=0. At exactly de=0 the required response is exact full-state identity, including restart. Floating-point recognition and very-small-increment limitations must be tested explicitly rather than inferred from these real-arithmetic equations.

For nonzero r tending to zero from an interior state, stress may jump to the active branch, depending on distortion direction. Reversal may likewise change stress direction at arbitrarily small strain. This is the selected shear-rigid interface, not a continuous strain-path-rate law. It must use `incremental_residual`, not `strain_path_rate` or a physical-time profile. Stress-controlled outer solvers cannot assume an invertible smooth inner map.

## State, controls, failures and transactions

Proposed candidate identity: `original-cam-clay-sw-electronic-log-recovery-v1`. v0.3 profile: `strain_path` / `incremental_residual`, `small_strain_3d`, `fixed_spatial`, objective rate none; first persistent symmetric state sigma in Pa/effective Cauchy; second persistent invariant scalar v, unit1. All six strain-increment components are explicit required inputs. Initial stress, v and every parameter must be supplied; illustrative values are not a preparation recipe. Domain checks require positive pressure, specific volume, finite packing/log/derived values, parameter ordering and admissible initial yield; no source projection of invalid incoming data. Specific-volume>=1 and tensile principal-stress restrictions are not added by assumption.

A declarative residual can set `sigma-sigma_target` and `v-v_target` using only committed state/de/parameters to calculate targets. No plastic solve variable or automatic zero-multiplier predictor is needed for this analytically eliminated endpoint. This is a proposed common-engine representation, subject to semantic validation, source-equation tests and backend qualification. There is no handwritten production kernel.

The first exposed guaranteed control is prescribed full symmetric strain. Axial compression/extension, undrained strain, volumetric recovery and mixed strain directions are included. Stress or mixed controls may be exposed only after actual controller qualification; critical mechanisms and stress selection can make those problems nonunique. A rejected controller request must return the complete old physical state. Trial/commit/rollback, substeps, partial-failure reporting and restart follow the existing engine contract; no partial plastic state is committed. Finite-rotation objectivity, global FE tangents, physical-time holds and experimental validation remain excluded. Fixed-branch derivatives exist away from branch switches, zero-distortion selection and projection boundaries; no unique tangent is promised at a switch or strain-triggered jump.

## Prospective checks and next gate

Before native/Wasm observations, qualify independent finite-equation residuals rather than only recomputing these eliminated formulas. Cases must include strict interior holds and volumetric recovery/projection, positive/negative signed plastic branches, all corner directions including zero distortion, overconsolidated strain-triggered jump, dry-side flow/softening, exact critical undrained mechanism, rotations, pressure-reference changes, invalid initialization, volume/domain failures, replay/restart/rollback and ordinary default/preset. An independent Decimal/bisection or constrained-system oracle should solve the original finite equations. Refine a positive-q undrained path against the unchanged source analytical trajectory, and a hydrostatic path against exact source v-ln(p). Freeze tolerances and all proposed public outcomes before compiled calls.

Open numerical questions: cancellation in very small increments and branch comparisons; norm under/overflow; exact zero recognition; pressure/packing exponential range; admissibility roundoff; source-derived invariant continuation and corner power interpretation require separate-agent review. These are qualification questions, not proof of a missing generic primitive. Do not claim a complete browser model from this design or delete any branch to make tests pass.
