# Hill / Abaqus 2025 — bounded source packet

Task: ING-hill-abaqus2025-v1. Owner: separate source specialist `/root/hill_source`, 2026-11-02. Owned output: this directory and ignored `.local/private-sources/hill-abaqus2025/`. This closes source transcription only; the parent owns the open [delivery ledger](../DELIVERY.md).

## Identity and sources

Selected law: the quadratic Hill potential with associative perfect plasticity and isotropic linear elasticity documented by Dassault Systèmes SIMULIA for **Abaqus 2025**, restricted here to infinitesimal strain, fixed Cartesian axes aligned with the material axes, constant parameters, and dry total Cauchy stress. This is a complete elastoplastic closure, not admission of a failure criterion alone. It is not an original-paper transcription, a reproduction of Abaqus numerical integration, a finite-rotation implementation, a hardening model, or the documented creep option.

Primary readable documentation and equation locators:

| Document | Exact locator | Contribution |
| --- | --- | --- |
| [Hill Anisotropic Yield/Creep](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMATRefMap/simamat-c-anisoyield.htm) | “Anisotropic Yield”, displayed potential, six coefficient equations, and flow equation; “Yield and Creep Stress Ratios”; “Output” | Quadratic form, coefficients, associated flow, local material orientation, work-based PEEQ |
| [Classical Metal Plasticity](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMATRefMap/simamat-c-metalplastic.htm) | “Perfect Plasticity”, “Flow Rule”, opening elasticity requirement | Constant reference yield stress, associated incompressible flow, elastic closure |
| [Linear Elastic Behavior](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMATRefMap/simamat-c-linearelastic.htm) | “Defining Linear Elastic Material Behavior”, “Defining Isotropic Elasticity”, “Stability” | Total Cauchy stress, isotropic compliance, modulus constraints |
| [Inelastic Behavior](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMATRefMap/simamat-c-plastic.htm) | “Plasticity Theories”, “Elastic Response”, “Stress and Strain Measures” | Additive elastic/plastic rates, Cauchy stress; finite-strain alternatives excluded here |
| [Conventions](https://docs.software.vt.edu/abaqusv2025/English/SIMACAEMODRefMap/simamod-c-conventions.htm) | “Convention Used for Stress and Strain Components”, “Stress and Strain Measures” | Material-property engineering shear convention and Cauchy stress |

The 2025 edition identifies the documentation version; it does not establish the date of every web revision. Exact HTML hashes and access times are in [source-receipts.json](source-receipts.json). These are public vendor documentation pages hosted by Virginia Tech. No right to redistribute their raw content was established; unchanged HTML stays private and only receipts, original derivation and hyperlinks are public. No supplied binary or vendor implementation was executed. Parent reported prior Downloads/private inventory search found no Hill source; repository search found no earlier Hill dossier or packet.

## Equations and schema crosswalk

Let `s` denote the full six-component Cauchy stress, **not its deviator**, in Atlas Mandel order `[xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz]`. Define the symmetric matrix

```text
A = [[Gh+Hh, -Hh,   -Gh,    0,0,0],
     [-Hh,   F+Hh,  -F,     0,0,0],
     [-Gh,   -F,    F+Gh,   0,0,0],
     [0,0,0, N,0,0], [0,0,0,0,L,0], [0,0,0,0,0,M]]
Q = s^T A s;  q = sqrt(Q);  Y = sigma_y > 0.
```

Thus `Q=F(syy-szz)^2+Gh(szz-sxx)^2+Hh(sxx-syy)^2+N*sxyM^2+L*syzM^2+M*sxzM^2`. `Gh` and `Hh` rename the source's Hill G and H to avoid confusion with elastic shear modulus `Gmod` or hardening. The source shear terms use physical stress; Mandel scaling removes the factor two. The gradient in Mandel components is `A s/q` when `q>0`. In particular the xy entry is `N*sxyM/q`, **not** `2N*sxyM/q`. The source's six-vector flow has engineering shear entries; using it unchanged with Mandel strain would double shear flow.

The constant elastic tensor is `C:e = K trace(e) I + 2 Gmod dev(e)`. Choose `K>0, Gmod>0`; equivalently `E=9 K Gmod/(3K+Gmod)>0`, `nu=(3K-2Gmod)/(2(3K+Gmod))` with `-1<nu<1/2`. All stresses/moduli/reference scale use Pa; strains and Hill coefficients are dimensionless. Constants are temperature-independent here. `p_ref>0` is a numerical scale only.

Continuous closure: `ds=C:(de-dep)`, `dep=dλ A s/q` on active yield, `q<=Y`, `dλ>=0`, `dλ(q-Y)=0`. Constant Y and A supply the complete perfect-plastic evolution: no hardening state is needed to determine future stress. Hydrostatic plastic flow is zero and the hydrostatic stress is unrestricted by this pressure-independent yield surface. `F,Gh,Hh,L,M,N>0` is a deliberately conservative convex subset; source-supported negative normal coefficients are not admitted. Strict positivity is sufficient, not necessary. Since `Q` is a sum of positive squared differences and shear squares, its only nullspace is hydrostatic stress; the admissible set is a convex cylinder. At active yield `q=Y>0`, the normal exists.

For comparison to laboratory ratios, the three normal yields are `Y/sqrt(Gh+Hh)`, `Y/sqrt(F+Hh)`, `Y/sqrt(F+Gh)`; physical xy/yz/xz shear yields are respectively `Y/sqrt(2N)`, `Y/sqrt(2L)`, `Y/sqrt(2M)`. The shear ratio denominator in the source is `τ0=Y/sqrt(3)`, whereas normal ratios use Y. Thus `R12=sqrt(3/(2N))`, etc. The source introductory shorthand about ratios must be read together with its explicit coefficient equations. Positive ratios alone do not guarantee the selected positive F/Gh/Hh subset.

Sign conversion takes both vendor tension-positive stress and strain to their negatives. Q is unchanged and its gradient reverses; the flow and elastic law retain precisely the above form. Plastic work is unchanged. This packet uses compression-positive stress/strain as required by Atlas; positive material axes are explicitly aligned with fixed spatial axes. A rotated loading tensor in the same fixed material frame is supported; rotating the frame without transforming A, evolving material orientation, spin, and finite-rotation transport are excluded.

Proposed explicit v0.3 profile: `strain_path / incremental_residual`, `small_strain_3d`, `fixed_spatial`, objective rate `none`, Mandel, both signs `compression_positive`; input exactly `de` with current infinitesimal strain increment, dimensionless symmetric finite components; empty advance inputs. Bind state `sigma` as total Cauchy stress. No pore pressure or effective-stress conversion exists.

Proposed minimum state is seven components: persistent `sigma` (six Pa, symmetric spatial tensor semantics), and zero-initialized scalar `gamma` with `plastic_multiplier` role, dimensionless, scalar invariant. Gamma is an **increment-local solve unknown**, not accumulated strain. Initialization is explicit named sigma only, examples-only, domain-and-initial-checks, finite admissible `Q<=Y²` at initialization. A numerical initial-check tolerance must be disclosed by the coordinator. No initial projection is authorized. Zero stress is an admissible illustrative example. Optional accumulated plastic strain or work is not necessary for this stress-only perfect-plastic specialization; the minimal model must not advertise PEEQ history output.

## Temporal integration and transactions

Atlas chooses backward Euler; the source pages do not specify an exact matching vendor finite-step algorithm. Freeze this distinct numerical choice. Use the **equivalent smooth squared potential**

```text
φ(s) = (Q(s)-Y²)/(2Y),       nφ(s) = A s/Y,
rσ = s - s_n - K trace(de) I - 2 Gmod dev(de) + 2 Gmod γ A s/Y,
f = φ/p_ref,
rγ = sqrt(γ²+f²) - γ + f.
```

`rγ=0` is the complementarity condition `γ>=0, f<=0, γ f=0`. For Y>0, φ and q−Y have exactly the same sign and zero set. At active yield `nφ=As/Y=As/q`; on the elastic branch γ=0. Thus this residual has exactly the physical solution set of the q-based backward-Euler KKT equations, including the same active plastic multiplier. It introduces **no** smoothed yield surface or hydrostatic regularization. Unlike evaluating `As/q`, it remains finite at q=0 with no branch. The complementarity norm remains nonsmooth at its origin; use existing solver semantics and test yield switching rather than claim a unique tangent there.

No physical time or rate enters. A zero strain increment at an admissible state leaves stress unchanged, with local gamma zero; a hold has no creep or relaxation. Reversals/unloading are handled by the elastic predictor then KKT correction, not by a hardening/reversal memory. Abrupt strain changes must be expressed as separate increments. Step subdivision changes the selected numerical path and need not equal a single endpoint return for general nonproportional loading.

Every trial starts from the same committed sigma. The generic engine resets gamma for each residual solve. Success commits sigma; failure/rollback must return the full incoming layout without partial state/reset effects. Repeated trials must be reproducible. These are Atlas transaction requirements, not vendor behavior asserted from this source. Elastic/plastic switch and nonlinear mixed-control convergence require numerical qualification. Parameter changes, restarts, histories and initial states must retain exact model/parameter identity; there are no annealing, deletion, damage or thermal reset events in scope.

On a smooth plastic branch, a consistent tangent follows by differentiating the endpoint residual and yield constraint; the full algorithmic tangent is not merely elastic C or the continuous elastoplastic tangent. At elastic interiors it is C. Outer constrained-control problems and singular perfect-plastic stress-controlled directions may fail and must roll back. No FE stability, acoustic, localization or general host qualification follows.

## Independent checks

[check_algebra.py](check_algebra.py) uses original Cartesian/Mandel arithmetic, no Atlas parser/compiler, and no compiled artifacts. It checks six directional yields, Euler work identity `s:n=q`, pressure invariance, plastic incompressibility, all-six-shear-sensitive centered differences, isotropic recovery F=Gh=Hh=1/2,L=M=N=3/2, sign covariance, positive convexity witness, and squared-potential active equivalence. Reproduce with `python3 -B docs/ingestion/hill-abaqus2025/source-v1/check_algebra.py`. Results are retained separately. These are algebraic checks, not numerical admission, compiled verification, calibration or experimental validation.

Independent numerical-reference construction for the coordinator: for elastic trial `t=s_n+C:de`, if `q(t)<=Y` return t and gamma0. Otherwise solve `[I+(2Gmod γ/Y)A]s=t` and monotonically bracket/bisect the scalar condition `s^T A s=Y²` with γ>=0. A annihilates the volumetric mode and has positive deviatoric eigenvalues, so this scalar decreases strictly to zero for a nonhydrostatic trial. Decimal Gaussian elimination of the 3×3 normal block plus direct shear solves is independent of the DSL residual/Newton engine. Freeze corpus and error policy before observing compiled output. The isotropic limit provides an additional closed radial-return witness; unequal Hill coefficients require the genuine anisotropic reference, not a radial-return approximation.

The first script reports 48 passing observations. Additional [check_return.py](check_return.py), reproduced with `python3 -B docs/ingestion/hill-abaqus2025/source-v1/check_return.py`, reports 26 passing observations covering five plastic returns (general mixed loading, sign reversal and all three pure shears), active consistency, endpoint residual, dissipation and the exact quadratic Jensen convexity gap. [return-results.json](return-results.json) retains this separate study; first-run algebra evidence is preserved unchanged. Source-side exact-candidate assessment and prefreeze metadata findings are in [CANDIDATE_ASSESSMENT.md](CANDIDATE_ASSESSMENT.md).

## Handoff

Owned files: this README, source-receipts.json, check_algebra.py, algebra-results.json, check_return.py, return-results.json, CANDIDATE_ASSESSMENT.md and acquisition-notes.txt. Raw HTML remains in the assigned ignored private directory. Source acquisition initially failed twice due to full disk, then Python network access failed under sandbox DNS; the coordinator freed only a reproducible duplicate archive and escalation allowed public-source download. These retained operational failures do not weaken scientific gates.

Source completeness: complete selected stress law with explicit scope and numerical-choice distinction. Executable status: proposed existing incremental profile; parent must validate its exact model. Numerical verification: independent algebra only at this handoff. Scientific admission: **not reviewed or approved by this source specialist**. No experiment/calibration/reference vendor run is available. No schema/compiler extension is required for this matrix-component residual. Next owner `/root`: freeze model and numerical policy, integrate through common generated engine, run bounded native/Wasm/transaction/browser study, obtain a separate exact-byte scientific review, and continue E0–E8. Board remains coordinator-owned.
