# Independent barodesy2017 body-law review

31October2026. Read-only cross-review of `/private/tmp/atlas-clay-barodesy-source-20261031-v1`; no repository changes, native builds, author-code execution or scientific admission. Primary: Medicus–Fellin, *An improved version of barodesy for clay*, DOI10.1007/s11440-016-0458-4. Independently hashed private publisher PDF: SHA256 `bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15`. Visually checked printed366–367 and374–375 (PDF2–3,10–11), including complete Eqs1–10/Table1 and Appendix3 Eq41. Source PDF/renders/text remain in the other packet's private directory and are not part of this report.

## Decision

**An explicitly named body-Eqs1–10, zero-spin research variant is defensible.** The source discrepancy must stay in its identity/provenance and limitations. It cannot be called equivalent to all printed formulas, the author UMAT, a finite-spin implementation or a scientifically admitted model.

Body p367 Eq8 uses `2p/sigma_star`. With the explicit p366 definition `p=-tr(T)/3`, Appendix3 p375 Eq41 uses `-2tr(T)/sigma_star=6p/sigma_star`. No redefined pressure or N accompanies the appendix summary. Independently, Appendix2 p374 Eq32 uses `2p/sigma_star` and its p375 Eq33 gives the factor `2^(c5 lambda)`. Thus the body selection has a second source-internal derivation supporting it. This is evidence for a documented research selection, **not an externally confirmed erratum**.

For source isotropic compression T=-pI,D=-vI/3, with v>0 the compressive volumetric rate, source R0=T0=-I/sqrt(3). Therefore

`d(log p)/dv = c3/sqrt(3) [A-1-sqrt(3)*beta]`,

where on the source NCL `A=2^(c5 lambda)` for the body and `A=6^(c5 lambda)` for Appendix41. Body beta cancels this exactly to1/lambda; the appendix reading does not. `independent_algebra.py` independently implements these scalar reductions without importing the other packet's helper. Nine assertions pass across all three complete Table2 calibrations, including a separate K0 check. Retained values are in `independent-algebra.json`; these are algebra tests, not integrated paths.

## Exact compression-positive map

Let source T=-sigma and source D=-E, where sigma/E are Atlas compression-positive stress/stretching. Define `r=norm(E)>0`, `U=E/r`, `delta=-trace(U)`, and calculate a,K,m,Lambda,beta,f,g from the **body** formulas using that delta and p=trace(sigma)/3. Define

`P=exp(-a*U)/norm(exp(-a*U))`.

Then source R0=-P and source T0=-sigma/norm(sigma), giving

`sigma_dot = c3*norm(sigma)*(f*P + g*sigma/norm(sigma))*r`,

`e_dot = -(1+e)*trace(E)`.

There is no additional minus sign multiplying c3, and a must not be evaluated with delta=+trace(U). c3 is negative in the three published complete calibrations; requiring c3>0 or source scalar h>0 would reject them. Algebraically combine the stress-normalization term as `c3*(f*norm(sigma)*P+g*sigma)*r` to avoid a removable division, but that alone does not resolve the p=0 critical-density domain.

The e closure is explicitly source footnote13 p374 for incompressible grains. sigma_star is fixed1kPa=1000Pa; put pressure ratios inside dimensionless powers/logarithms. phi is an angle requiring a declared degree/radian input convention. The rest of the four parameters are dimensionless. This map uses stretching, not a claim that arbitrary additive finite strain has the same kinematics. Source p366 footnote3 limits exact logarithmic-strain-rate equivalence to rectilinear stretching.

Source p366's printed spin conversion contains identical `WT` products that cancel. W=0 avoids that discrepancy; do not implement a corrected commutator and silently call it the same source. Fixed orthogonal-basis covariance checks with W=0 remain valid and useful despite this finite-spin limitation.

## Closure and memory

Seven scalar state components (sigmaSym6,e1), four independent material parameters(phi_c,N,lambda_star,kappa_star), fixed sigma_star and the declared incompressible-grain/zero-spin kinematics close the **regular-domain instantaneous body law**. Table1 defines all c1–c6. R,K,m,a,beta,Lambda,f,g,ec and the scalar h are derived quantities; no reversal history, lag cache, preparation mode or auxiliary plastic multiplier is implied. Sigma/e initialization is supplied explicitly. NCL initialization is a reference case, not a universal required initial state; overconsolidated states must not be silently reset to it.

The1/1000 extension-pressure ratio is embedded in the source c3 calibration (Table1 plus Sec4.3), not a fifth freely chosen soil input. Existing32-slot capacity is sufficient; a matrix function is a separate expression/runtime capability. Do not reuse a sand or small-strain extension to fill this model's remaining numerical gaps.

A restrictive research domain may require positive-definite compressive stress and e>=0, but label such a restriction as the selected supported domain, not the paper's complete admissibility theorem. At minimum keep finite parameter/intermediate checks, p>0,1+e>0, nonzero parameter denominators and c1>0. The simple phi/lambda/kappa inequalities alone do not prove that every calibration denominator has the expected sign or stays away from zero.

## Singular and reference branches

| Case | Independent conclusion | Research implementation implication |
|---|---|---|
| E=0 | D0 undefined; for a finite regular unit direction the rate scales linearly with norm(E). | Explicit no-update continuation is a reasonable declared extension. It is not a printed numerical algorithm. Return zero stress/e rates without normalizing E. Do not evaluate invalid directional shared-derived expressions eagerly first. |
| Pure isotropic stretching | delta=±sqrt(3), m diverges and a has an indeterminate limiting form. Since exp of any scalar multiple of I normalizes to I/sqrt(3), P has the isotropic value. | Use an explicitly derived isotropic P branch; prove/test both compression and expansion limits. Avoid computing m or a on this branch. This is not clipping delta near its bound. |
| Nearly isotropic stretching | Cancellation in3-delta² and log(K) near K=1. | Prefer stable invariant measures and log1p-style algebra inside a reviewed matrix-direction implementation. Exact/near branch tolerances must be declared and tested; silently flattening a neighborhood changes the law. |
| K=0 at m=c2 | With c1>0, source K vanishes at delta=sqrt(6*c2²/(9+2*c2²)), a dilative source direction. ln(K) diverges. | Initially reject the singular surface explicitly; do not set K to epsilon. A proposed normalized projector limit needs separate path/multiplicity analysis, particularly at repeated extreme eigenvalues. |
| K approximately0 | K=1−1/(1+x) cancels for tiny x=c1(m−c2)². | Equivalent x/(1+x), plus stable log evaluation, avoids artificial K=0 from subtraction. Underflow/overflow still require bounds; no source regularization inferred. |
| Hydrostatic **stress** at p>0 | No deviatoric-stress normalization or Lode angle is needed by this law. | It is a regular stress state provided E direction is otherwise supported. Do not accidentally reject it because E's pure-volumetric branch is singular in the raw formula. |
| sigma=0 / p=0 | Raw T0 and logarithmic critical-density expression undefined; source discusses stress-free asymptotes, but gives no finite evaluator branch. | Initially exclude exact zero stress/pressure. Rewriting products does not authorize a new stress-free initialization law or pressure floor. |
| Oedometric compression | E=diag(r,0,0),r>0: delta=-1,m=3/2,a=lnK. Target P22/P11=K=1−sin(phi_c) from Table1. | Add this independent K0 check. It concerns the R attractor under a proportional path, not a forced ratio for every current stress or a reset of supplied K0. |
| Isotropic unloading | Beta uses Lambda=kappa; actual instantaneous modulus also depends on current density ratio. | Do not impose1/kappa as a universal unloading tangent. Use the source's specifically stated reference density or test the full density-dependent expression. |

For regular directions, K can be evaluated as x/(1+x); for |m| large, direct x can overflow. A stable rewrite must preserve the same function and report unsupported nonfinite domains rather than saturate arbitrary tensors. At exact K=0, source limiting-projector behavior is not established by the current packet.

## Matrix exponential and DSL admission requirements

The source footnote5 p366 and Eq3 require the **matrix exponential** of a symmetric tensor. For orthogonal Q, exp(QAQ^T)=Qexp(A)Q^T; entrywise scalar exp is wrong for off-diagonal tensors. `atlas/dsl.py:103–107,187–198` currently exposes scalar exp and symmetric tensor square/invariants, with exp rejecting tensor input. No generic symmetric exponential or eigensolver is present.

A generic primitive such as a dimensionless symmetric normalized exponential returning Sym is sufficient for this source, but its public name/API is a design decision. A full eigensolver is not inherently required: matrix-function algorithms are alternatives. A finite fixed Taylor polynomial is an approximation that needs an error contract; it is not an exact source algebra replacement merely because tensor_square exists. A Cayley–Hamilton degree-two representation still needs robust scalar matrix-function coefficients at repeated eigenvalues.

Because only exp(A)/norm(exp(A)) is used, scalar-identity shifts cancel exactly. Stable implementation should exploit that freedom without overflow/underflow and test it independently. Repeated eigenvalues are regular for finite A; do not differentiate eigenvectors naively or treat repeated eigenvalues as source singularities. Generated AD needs the correct Frechet derivative, including repeated-eigenvalue limits, before using this operation in the common implicit solver.

Minimum operator checks: diagonal tensors; scalar I; repeated/double eigenvalues; symmetric off-diagonal/noncoaxial tensors; rotation covariance; identity-shift invariance; extreme spectral gaps; norm1/SPD output where representable; independent dense-series or trusted matrix-function oracle; Frechet/directional finite differences away from source singularity. Check Python/generated/native/Wasm parity only after serial build authorization; none is supplied here.

Smallest defensible next implementation: a typed **instantaneous** seven-state body-law fragment with exact source selection and supported-domain declarations, a stable matrix-function primitive, both isotropic branches, zero-input policy, K=0 rejection, and independent rate checks(NCL,K0,regular noncoaxial/covariant cases). Integration and numerical/reference admission remain separate. No generic history-runtime extension or state-capacity increase is necessary for this base law.
