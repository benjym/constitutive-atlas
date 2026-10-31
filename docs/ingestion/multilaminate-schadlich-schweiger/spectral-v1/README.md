# Multilaminate spectral stiffness and degradation v1

Task SRC-multilaminate-spectral-v1; coordinating parent, 1 November 2026. This is a bounded equation inventory for the [selected 2012 thesis target](../variant-identity-v1/README.md), not a complete v0.3 model, executable kernel or scientific admission.

Bert Schädlich, *A Multilaminate Constitutive Model for Stiff Soils*, TU Graz dissertation, April 2012. [Persistent source](https://doi.org/10.3217/wmxdh-rg587). PDF SHA-256 `43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9`. Seventeen complete pages were visually inspected: PDF53–55,69–72,75–76,78–81,178–179,208–209 (printed pp.35–37,51–54,57–58,60–63,160–161,190–191). Raw PDF, extracted text and renders remain private. [source-ledger.json](source-ledger.json) supplies page/render hashes and explicit open gates.

## Global compliance and spectral modes

The vertical axis is y and the horizontal bedding plane is x-z. Eq66 uses engineering shear strains with raw shear stresses. Eq67 requires `nu_hv/Eh = nu_vh/Ev`, and Eq68 gives `Ghh = Eh/[2*(1+nu_hh)]`. Positive elasticity requires positive moduli, `-1 < nu_hh < 1` and the absolute-value bound in Eq71. In terms of the independently chosen `nu_hv`, the latter is `2*nu_hv^2 < (1-nu_hh)*Eh/Ev`. Every interpolated/stress-scaled state needs admissibility, not just its endpoints.

The Kelvin compliance Eq94, with order `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`, is

```
C = [ 1/Eh       -nu_hv/Eh  -nu_hh/Eh       0          0          0
     -nu_hv/Eh    1/Ev      -nu_hv/Eh       0          0          0
     -nu_hh/Eh   -nu_hv/Eh   1/Eh          0          0          0
      0           0          0             1/(2Gvh)  0          0
      0           0          0             0          1/(2Gvh)  0
      0           0          0             0          0          (1+nu_hh)/Eh ]
```

The four spectral families have multiplicities 2,1,1,2. Defining `a=(1-nu_hh)/Eh`, `d=1/Ev`, `b=-sqrt(2)*nu_hv/Eh`, AppendixA.1 gives

```
lambda1 = (1+nu_hh)/Eh
lambda2 = (a+d)/2 - sqrt((a-d)^2/4+b^2)
lambda3 = (a+d)/2 + sqrt((a-d)^2/4+b^2)
lambda4 = 1/(2Gvh)
```

The idempotents in A.3 are projectors onto: horizontal normal difference plus xz shear (E1); the normal vector `v2=(cos(omega)/sqrt(2),sin(omega),cos(omega)/sqrt(2),0,0,0)` (E2); its orthogonal normal partner `v3=(-sin(omega)/sqrt(2),cos(omega),-sin(omega)/sqrt(2),0,0,0)` (E3); and xy/yz shear (E4). E2 and E3 are outer products. Coincident eigenvalues reduce the number of distinct eigenspaces; a numerical implementation must not assume four distinct eigenvalues or divide by their separations.

Eqs95–102 specify `sigma_m=Em*sigma`, `sigma_i,m=Ti^T*sigma_m`, `epsilon_i,m=lambda_m*sigma_i,m`, summation over modes and `Ci=Ti^T*C*(Ti^T)^(-1)`. This is a similarity transformation, not an orthogonal rotation or a compliance congruence. A nonsymmetric local matrix alone does not disprove the stated relation; global elasticity/energy cannot be assessed by assuming Euclidean local work conjugacy.

**Retained eigenangle failure:** A.2 prints `tan(2*omega)=(-2*sqrt(2)*nu_hv/Ev)/[(1-nu_hh)/Eh+1/Ev]`. Direct diagonalization of Eq94 instead yields the ratio `2*b/(a-d)` with eigenpair branch selection. AppendixD p191 uses Eh in the numerator and a difference in the denominator, plus explicit branches. The independent checker reconstructs Eq94 using its own reduced 2x2 diagonalization and separately checks the D angle. The literal A.2 fails for all three selected nonzero-coupling witnesses even after both eigenpair assignments. This does not authorize silently replacing A.2 in an executable record.

**Retained coordinate ambiguity:** Eqs92/93 repeat yy as the third normal component. Eq93 also labels the shear entries `sqrt(2)*gamma`, whereas Eq66 uses gamma for engineering shear; an orthonormal Kelvin strain vector would use engineering gamma divided by sqrt(2). The compliance and tensor basis must therefore be declared explicitly. The source's sentence about preserving a sum of components is not adopted as a definition of Kelvin invariance; the relevant orthonormal identity is tensor inner-product preservation.

## Plane projection and inversion

Eq103 orders six local components as `[sigma_nv,sigma_nd,tau_s1,tau_s2,tau_t1,tau_t2]`, with matching strain labels. Tangential contributions from global normal and shear stresses are stored separately. To transcribe Eq104 compactly, its columns for unit orthogonal directions n,s,t are:

```
c1 = (1/3,1/3,1/3,0,0,0)
c2 = (n1^2-1/3,n2^2-1/3,n3^2-1/3,2*n1*n2,2*n2*n3,n1*n3)
c3 = (n1*s1,n2*s2,n3*s3,0,0,0)
c4 = (0,0,0,n1*s2+n2*s1,n2*s3+n3*s2,n3*s1+n1*s3)
c5 = (n1*t1,n2*t2,n3*t3,0,0,0)
c6 = (0,0,0,n1*t2+n2*t1,n2*t3+n3*t2,n3*t1+n1*t3)
Ti = [c1 c2 c3 c4 c5 c6]
```

The last entry of c2 is printed without the factor 2 that appears for xy/yz. AppendixD p190 explicitly includes it. For `n=(-2/3,2/3,1/3)` and unit raw xz shear, tensor traction gives `sigma_nd=-4/9`; the literal Eq104 gives `-2/9`. Both are retained in the report. The witness's coordinate-consistent Kelvin candidate uses the tensor-derived factor 2 and divides the raw projection's global shear columns by sqrt(2). That candidate verifies Eq102 and the isotropic local limit, but is not a declaration that the printed implementation's complete assembly is reconciled.

The source requires inverse `Ti^T` and warns about axis-aligned planes, proposing a different integration rule or slight rotation (pp53–54). Exact rational checks additionally find singularity for the non-axis plane `n=(3/5,4/5,0)`. Therefore avoiding only the three axes is insufficient. The actual prepared quadrature/directions and conditioning must be checked; do not introduce a pseudoinverse, arbitrary perturbation or new quadrature here. In the isotropic limit Eqs105/106 give local diagonal entries `[(1-2*nu)/E,(1+nu)/E,...,(1+nu)/E]` in the specified split.

## Pressure scaling, degradation and history

Eqs108–110 define three separate pressure-dependency choices. For each small-strain modulus M in `{Eh0,Ev0,Gvh0}`, approach1 multiplies its reference value by `(p'/p_ref)^m`; approach2 uses `(sigma_n'/p_ref)^m` on each plane. Approach3 also applies preparation factors `(sigma_h0'/p0')^m`, `(sigma_v0'/p0')^m`, and `(sqrt(sigma_v0'*sigma_h0')/p0')^m` respectively, then evolves with `(p'/p_ref)^m`. The root in the last expression was verified visually; text extraction alone loses it. Poisson ratios do not depend on stress level within each pressure choice. Approach3 remembers the initial stress ratio, not the current ratio at every step.

The equations use pressure ratios as written; the tension-negative host listing clips mean/normal stress and takes absolute values before powers (D pp190–191). The [host packet](../host-contract-v1/README.md) retains parameter conversion and preparation questions. These are alternative source definitions, not permission for an implicit abs/default in the schema. Noninteger powers need a real, nonzero admitted domain. No full pressure branch is selected by this packet.

Section4.4.2/Fig29 specifies constant-small-strain, linear-in-log transition, constant-large-strain tangent moduli. AppendixD p190 makes the interpolation explicit. Let `r=epsilon_deg`, `0<r1<r2` and

```
z = 0                                  when r <= r1
z = [ln(r)-ln(r1)]/[ln(r2)-ln(r1)]       when r1 < r < r2
z = 1                                  when r >= r2
Eh  = (1-z)*Eh0  + z*Eur_ref
Ev  = (1-z)*Ev0  + z*Eur_ref
Gvh = (1-z)*Gvh0 + z*Eur_ref/[2*(1+nu_ur)]
nu_hv = (1-z)*nu_hv0 + z*nu_ur
nu_hh = (1-z)*nu_hh0 + z*nu_ur
```

This is interpolation of moduli/ratios, not interpolation of compliance. Pressure scaling follows local matrix construction in D p191. Eq111 defines `r` as Euclidean distance from the active sphere centre in `{epsilon_nd,gamma_s,gamma_t}`. A zero distance uses the constant branch without evaluating log(0). Fig29 labels `nu_vh` as linearly interpolated, while D interpolates `nu_hv`. With reciprocity these disagree away from isotropy: a midpoint witness gives `nu_vh=9/100` from D versus `1/8` from a literal Fig29 interpolation. Preserve that ambiguity until one explicit source-backed formulation is selected.

The history description (pp61–63) starts with an origin-centred sphere, creates a nested active sphere when distance decreases, and removes inner spheres when an outer path is reached again. Four spheres are stored; this limits nested reversal depth, not total load cycles. Do not replace r with accumulated strain norm or reset the centre every increment. Exact event ties, fifth-reversal policy and trial/commit/rollback still depend on the previously reviewed host listing. The present checker verifies Eq111 geometry only, not the full event algorithm or Masing behaviour.

## v0.3 requirements and stop boundary

The [current contract](../../../FORMULATION_CONTRACT.md) requires an explicit formulation; no model JSON is emitted while these gates remain open. This packet is an equation inventory, not a partial declaration pretending to validate.

| Required declaration | Evidence / remaining work |
| --- | --- |
| Time/equation form | Time-independent host and stress/strain increments support a strain-path treatment. The full coupled return plus stiffness/history iteration must define the actual residual/update; these compliance equations alone are not state evolution. |
| Kinematics/frame/objective rate | Fixed Cartesian y-vertical small-strain relations are explicit here; no finite-rotation transport follows. Reconcile the full law before declaring small_strain_3d/fixed_spatial/none. |
| Tensor/sign/stress binding | Reconcile Eq66 engineering versus Eqs92–94 Kelvin and Eq104 raw projection; preserve effective-stress meaning and explicitly convert both tension-negative stress and strain to Atlas compression-positive Mandel/SI. Cauchy binding remains a full-law declaration, not an inferred default. |
| Inputs and preparation | Declare strain increment, pressure-dependency branch, reference moduli/pressure/exponent, reciprocal Poisson pair, degradation thresholds, fixed material basis, prepared directions/weights, initial stress ratio where required and all nonlocal host inputs. |
| State/lifecycle | Separate global stress, plane hardening, split strain, active/outer contour centres/radii and prepared metadata. Trial copies, failure rollback, nested stiffness iteration and restart cannot be reduced to the six-component projection. Source storage exceeds the current engine budget. |
| Solver/tangent | A changing tangent elastic stiffness in the outer iteration is not a proven consistent full constitutive tangent. Invertibility, domain/energy checks, event ordering and global/local plastic coupling remain mandatory. |

Seven standalone witness groups reproduce matrix reconstruction, projector identities, literal failures, exact traction and singularities, Kelvin similarity/isotropic limit, logarithmic endpoints and Poisson ambiguity, pressure-branch isotropic collapse and distance invariance. `1e-12` absolute tolerance was fixed before floating observations on O(1) compliance examples; exact projection/singularity/Poisson checks use rational arithmetic. These are algebraic findings, not convergence, material-path or experimental validation.

Reproduce with `python3 -B check.py --source /private/path/to/thesis.pdf` (omit `--source` to run mathematics alone). [checks.json](checks.json) preserves retained failures; [manifest.json](manifest.json) pins this packet and prior dependencies. No author program, compiled artifact, build, calibration or deployment was run.

Stop this slice here. Next is the selected Chapter6 Hvorslev/softening/nonlocal equation packet; then reconcile a single full source-backed definition and its convention/branch gates before implementing generic solver capabilities. Do not continue a series of projection micro-audits or add a reduced model to bypass missing histories/nonlocal support. Full ING remains open.
