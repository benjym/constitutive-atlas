# NorSand 1993 supplied original: source and control contract

Task `SRC-norsand-original-v2`, child `MODEL-norsand-1993`; lead `/root`, 2026-11-01. This is the source/contract continuation of the historical access-gap packet, not another model family. [Source receipt](source-receipt.json) retains the user's exact 1,100,155-byte, 13-page original privately, SHA-256 `fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9`. All printed pages 91–103 were visually inspected, including every governing equation, Table 1, Figures 1–12 and notation. [DOI](https://doi.org/10.1680/geot.1993.43.1.91). No redistribution permission is inferred from upload; originals, text and renders remain ignored/private.

## Exact identity and scope

Jefferies (1993), *Nor-Sand: a simple critical state model for sand*, Géotechnique 43(1), 91–103. This paper develops the rigid-plastic, associated, isotropic model for drained axial-symmetric loading; effective stresses and negligible elastic strains are explicit assumptions on p92. Stress and strain increments are coaxial. No elasticity, fabric evolution, cyclic inner cap or general three-dimensional Lode rule is part of the implemented-source target. Page101 explicitly identifies elasticity as a future addition for more detailed representation. Those ingredients cannot be imported from modern NorSand under this identity.

Full original acquisition resolves `NS-SOURCE-01`. It does not resolve the finite numerical/host contract or establish model approval. The earlier [access packet](../delivery-v1/) and [source-gate review](../delivery-v1/independent-review/README.md) retain their historical identities and failed routes.

## Source equation inventory

Notation uses `p=(sigma1+2 sigma3)/3`, `q=sigma1-sigma3`, `eta=q/p`, `eps_v=eps1+2 eps3`, `eps_q=(2/3)(eps1-eps3)` (p102). Compression is positive, consistent with positive contraction in the plotted volumetric strains. Stress/strain power is `sigma1 deps1+2 sigma3 deps3 = p deps_v+q deps_q`. Dots denote incremental changes, not a physical-time constitutive dependence (p102); p92 explicitly states rate independence. `pi` below means image pressure, not the mathematical constant.

The printed equations, with typographic normalization only, are:

| Locator | Law or definition | Interpretation |
| --- | --- | --- |
| Eqs1–2,p92 | Critical state permits continued shear at constant stress and volume; current `psi` tends to zero with continued monotonic shear. | Axioms; not an additional update equation. |
| Eq3,p93 | `psi_i=e-e_c(pi)` | Current image-state parameter; different from `psi=e-e_c(p)`. |
| Eq4,p93 | `dpsi_i/deps_q=f(psi_i)`, with `f(0)=0`, positive for negative argument, negative for positive argument. | General framework motivation. The specific NorSand law below is Eq12, not an independently prescribed second hardening equation. |
| Eqs5a/b,p94 | `q_c=M p_c`; `e_c=Gamma-lambda_c log p`. | Read `log` as natural logarithm in view of Eq9 and explicit `e-ln p` notation on p102. The printed `log`/`ln` difference is retained here. |
| Eq6,p95 | `D=deps_v/deps_q=(M-eta)/(1-N)` | Associated dilatancy; positive contraction, negative dilation. |
| Eq7a,p96 | `eta=(M/N)[1+(N-1)(p/pi)^(N/(1-N))]`, `N!=0` | Full printed power branch. |
| Eq7b,p96 | `eta=M[1+ln(pi/p)]`, `N=0` | Separate exact logarithmic branch; do not evaluate Eq7a at zero. |
| Eq8,p96 | `D_max=3.5 psi_i` | Empirical average limiting relation. The coefficient 3.5 is fixed in this original isotropic model, not an extra fitted material parameter (p97). |
| Eq9,p96 | `psi_i=psi+lambda_c ln(pi/p)` | Uses the current image pressure. |
| Eq10a,p96 | `pi/p=[(1-N eta/M)/(1-N)]^((N-1)/N)`, `N!=0` | Inversion of Eq7a. Note the negative exponent for `0<N<1`. |
| Eq10b,p96 | `pi/p=exp(eta/M-1)`, `N=0` | Inversion of Eq7b. |
| Eq11a,p97 | `r_L=(pi/p)_max=(1+3.5 psi_i N/M)^((N-1)/N)`, `N!=0` | Limit evaluated from the current image state; requires positive power base. |
| Eq11b,p97 | `r_L=exp(-3.5 psi_i/M)`, `N=0` | Exact zero-coupling limit. |
| Eq12,p97 | `dpi/deps_q=h(pi_max-pi)`, `pi_max=p*r_L` | Stress-dimensional right side per dimensionless shear strain. No normalization by pressure is missing. |
| Numerical paragraph,p98 | Forward differences with consistency at each step. | Does not fix step size, rounding, lagging, correction algorithm or failure policy. These remain Atlas numerical choices. |

Eq11 is evaluated with the current `psi_i` before computing `pi_max`; it does not instruct a separate nonlinear solve for an unknown limiting-image state. Page94 defines the limiting function in terms of current image state, p97 repeats that dependence, and p98 summarizes maximum hardness controlled by `psi_i`. Substituting `r_L` into Eq7 gives `eta_L=M-3.5(1-N)psi_i`, whose Eq6 dilatancy is exactly Eq8. This identity is an algebraic consistency check, not an assertion that the evolving stress is always at its limiting ratio.

## Parameters, state, domains and preparation

Five material quantities are needed when the CSL is supplied absolutely: dimensionless `M`, `N`, `h`, `lambda_c` and `Gamma`. `M>0`, `h>0`, `lambda_c>0` are the physically intended positive slopes/modulus; the paper does not supply a universal admitted multidimensional box. Table1 spans different sands rather than proving validity throughout a numerical box. Real-sand discussion p96 uses approximately `0<=N<0.4`; Fig4 also compares `N=0.5` as a shape example. Algebra requires `N!=1`; negative N is outside the proposed packet's checked material region.

Pressure must be positive wherever logs/ratios occur. For `0<N<1`, require `1-N eta/M>0` in Eq10 and `1+3.5 psi_i N/M>0` in Eq11. For the displayed compression branch also require `q>=0`. Positive cell pressure on the conventional triaxial path requires `eta<3`. These are different constraints; a real-power base is not a substitute for the loading-scope conditions. No floors, clipping, absolute shear increments or extrapolated elastic branch are authorized.

Use the dimensionally explicit CSL `e_c(p)=Gamma_ref-lambda_c ln(p/p_ref)` with a stated reference pressure. The source writes dimensional numerical `p` and defines Gamma at `p=1` (p102); its plots use kPa. Converting a kPa-referenced intercept to Pa without transforming Gamma is incorrect: `Gamma_Pa=Gamma_kPa+lambda_c ln(1000)` when reference numerical pressure is 1Pa. This conversion changes the intercept representation, not the material. `p_ref` is a declared unit/reference choice, not a sixth fitted material constant. No exact public Gamma preset has yet been selected.

The active law uses `p,q,e,pi`, with Eq7 constraining stress and yield size. A natural axial representation has four scalar physical fields with one algebraic stress relation; they are not four independent initial degrees of freedom. Accumulated `eps_q,eps_v` can be observables/integrated diagnostic histories once a host contract is selected. No persistent tensor fabric is present. `R` (Fig1,p93) characterizes overconsolidation; it is not an extra constant in Eq12. Normal consolidation at `eta0=0` gives `pi0/p0=(1-N)^((1-N)/N)` or `exp(-1)` at `N=0`; for `N=0.2`, the exact ratio is `0.4096`, agreeing with the rounded p98 example. At general active initial stress Eq10 computes the yield-consistent `pi0`. An interior/overconsolidated state requires a separate inactive/loading rule, which is not supplied as an executable branch in this paper. Do not silently project it onto the surface.

Finite evolution of void ratio needs a volumetric kinematic rule. `de=-(1+e) deps_v` follows from incompressible solids and incremental volume strain measured relative to current volume; it is an explicit Atlas reconstruction, not a separately printed constitutive equation. The paper does not specify a finite engineering-strain update. This reconstruction and any finite discretization require review before candidate qualification. Complete explicit initialization must include all physical state and control context, check yield/positive pressure/power bases and state whether the state is normally consolidated. Source figures do not prove a physical specimen-preparation recipe.

Fig7 uses `M=1.25,N=.20,h=100,lambda_c=.0185` and initial `psi0=0,-.1,-.2,-.3`; Fig8 has `lambda_c=.022`. Figs11/12 use `M=1.20,N=.20,h=280,lambda_c=.0135`. D667 has `e0=.590,p0=130kPa,psi0=-.161`; D684 has `.820,200kPa,+.075`; D662 has `.677,60kPa`; D663 has `.675,300kPa`. They do not provide a consistent exact Gamma/reference/precision contract for reproducing every plot. Calibrated `h` and supplied CSL/dilatancy information cannot be counted as an independent experimental validation. Post-peak plots describe intense-shear-zone response; p98–99 warn against interpreting it as homogeneous nominal specimen strain.

## v0.3 crosswalk and actual host gap

The [current schema](../../../../schemas/model-v0.3.schema.json) and [contract](../../../FORMULATION_CONTRACT.md) were read. No executable-looking JSON is created with guessed conventions. [Crosswalk](crosswalk.json) explicitly distinguishes confirmed source declarations, Atlas representation proposals and unsupported fields.

Confirmed: strain-path/rate-independent effective stress; scalar axial invariants and work-conjugate strains; no physical clock; fixed coaxial axes for a proposed host. Mandel embedding of axial stress would be `[p+2q/3,p-q/3,p-q/3,0,0,0]` in compression-positive Pa. This is an Atlas representation mapping, not evidence of a general3D source law or finite-spin objective update.

The current v0.3 strain-path profiles take an arbitrary symmetric prescribed `de`, bind six-component persistent `sigma`, and declare `small_strain_3d`; `axisymmetric_x` currently exists only for physical-time ODEs. The original useful public protocol instead prescribes conventional drained triaxial mixed control: fixed effective cell pressure plus increasing axial/shear strain, with radial strain determined from normality. Physical time must not be invented merely to access an axisymmetric profile. A production model must not silently ignore supplied radial/shear strain components or encode the cell pressure as a material constant.

Minimal source-derived witness: at `eta=0,M=1.25,N=.2`, Eq6 fixes the instantaneous `deps_v/deps_q=1.5625`. An arbitrary isochoric shear input has ratio zero and cannot satisfy this active initial normality direction. This demonstrates why a single arbitrary-prescribed-strain rate map cannot simply reuse the original active equations without defining extra behavior. It is not proof that a finite residual model or specialized mixed-control host is impossible.

For a constant-cell protocol `c=p-q/3>0`, use source work-conjugate shear strain `s=eps_q` as independent loading coordinate. Define `r=pi/p`, `y=(p/pi)^(N/(1-N))` (`y=1` at `N=0`) and `D=(M-eta)/(1-N)`. Differentiating the yield and cell constraints yields the local reduction

```text
p=c/(1-eta/3), q=p*eta
deta/ds = h*M*y*(3-eta)/(3-eta+M*y) * (r_L/r-1)
dpi/ds = h*(p*r_L-pi)
deps_v/ds = D
de/ds = -(1+e)*D     [explicit kinematic reconstruction]
deps1/ds = 1+D/3; deps3/ds = D/3-1/2
```

The reduced local derivative is derived from the source; it is not an implemented production kernel or a prescribed finite step. It is a minimal example for generic mixed-control/path-coordinate capability design. Reversing signed `s` is not automatically a supported unloading/cyclic law: the paper's examples and axiom concern monotonic shear, and no inactive elastic branch is given.

`CAP-norsand-mixed-control-design-v1` must resolve a generic declared path-coordinate/mixed-control evaluator, explicit controls and state initialization, positive/zero progress and hold behavior, nonsmooth events and full-parent transaction boundaries. It must also determine whether an existing generic residual/control interface can provide the required source scope without relabeling it. No shared schema/compiler/runtime mutation is included in this source task. E2 remains open until a separately owned supported contract is available and a complete numerical acceptance plan is frozen.

## Integration and prospective verification

No elapsed seconds, strain-rate effect, absolute-value shear accumulation, unloading elasticity, initial projection or Lode continuation is inferred. A proposed monotonic host can define zero progress as an exact unchanged-state identity; that is an Atlas interface convention to qualify, not a physical-time relaxation claim. A failed trial must retain complete parent state/control history; no accepted substep prefix may leak into the parent. Restart must retain every selected physical and controller field. These requirements remain prospective until an actual interface is designed.

The frozen [algebra policy](algebra-policy.json) precedes parent source-only observations. [check_algebra.py](check_algebra.py) independently checks yield inversion, source normality, limiting dilatancy, CSL image conversion, exact `N=0`/normally consolidated limits, work conjugacy, invalid algebra domains and a separately solved implicit constant-cell derivative. These checks are mathematical/source sanity checks; they do not run a candidate, interpreter, compiled solver or trajectory. Future E2–E4 gates must separately freeze complete finite paths, domain rejections, rollback/recovery/restarts, refinement/partition and derivative behavior, a useful fully initialized public preset, native/Wasm identity/parity and unaffected-model regressions before compiled observations. The paper's forward-difference sentence is insufficient to claim those gates already exist.

## Handoff

Exact outputs are this source report, receipt, crosswalk, algebra policy/script/results, integrity manifest/checker and independent review in this directory. Historical papers/audits/models are unchanged; no root model, schema/compiler, build, registry, web asset or deployment is modified here.

Source acquisition and original equation reading: complete. Source transcription/contract review: see independent decision. Executable model: absent. Numerical evidence: source algebra only. E5 approval, atlas integration, packaged browser and live delivery: unperformed. Full umbrella remains open; the lead resumes at E2 after the generic mixed-control and finite-kinematic contract is resolved.
