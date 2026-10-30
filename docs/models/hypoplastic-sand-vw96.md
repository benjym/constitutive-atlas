# Sand hypoplasticity, von Wolffersdorff: transcription dossier

Formulation ID: `hypoplastic-sand-vw96`. Status: **transcribed; independent review pending**. The implemented scope is a local three-dimensional rate-independent stress/void-ratio law with infinitesimal kinematics and zero spin. It has no intergranular-strain state; the IGS extension has a separate draft identity.

## Sources, availability and variant

The equation transcription is from Wolfgang Fellin's **Equations of the Hypoplastic Law**, dated 1999-10-01, [University of Innsbruck, section 5](https://www.uibk.ac.at/de/geotechnik/bodenmechanik/forschung/hypoplasticity-copy-2/). Images 18–26 were visually inspected. This is an implementation-author equation summary of the von Wolffersdorff formulation, not a direct inspection of every equation in the original journal paper. The [image inventory](../../catalogue/source-audits/hypoplastic-sand-vw96-fellin-1999.json) records exact URLs, SHA-256 values and equation mappings. Images are linked, not bundled.

The original publication is [von Wolffersdorff (1996), A hypoplastic relation for granular materials with a predefined limit state surface](https://doi.org/10.1002/%28SICI%291099-1484%28199607%291%3A3%3C251%3A%3AAID-CFM13%3E3.0.CO%3B2-3), pages 251–271. On 2026-10-30, the publisher PDF route returned the abstract page; [KIT's institutional record](https://publikationen.bibliothek.kit.edu/372196) supplied metadata without a full-text link; the [SoilModels preprint page](https://soilmodels.com/download/von-wolffersdorff-p-a-1996-a-hypoplastic-relation-for-granular-materials-with-a-predefined-limit-state-surface-mechanics-of-cohesive-frictional-materials-13-251-271/) showed a login link and an unexpanded free-download placeholder. On 2026-10-31 the user supplied the complete 21-page original PDF in Downloads. Its title page is visually verified and its bytes are pinned in the [original-paper receipt](../../catalogue/source-audits/original-papers-2026-10-31.json). The access gap is resolved; equation-level reconciliation and independent review remain pending.

## Complete equations and source mapping

Both stress `sigma` and stretching `D` are compression positive. Vectors use Mandel order `xx, yy, zz, xy, yz, xz`, with tensor shears multiplied by `sqrt(2)`. Define

\[
p=\operatorname{tr}\sigma/3,\quad A=\sigma/\operatorname{tr}\sigma,\quad
B=A-I/3,\quad j=B:B,\quad u=\sqrt{3j}.
\]

Fellin image 19 defines normalized stress and its deviator; image 22 defines `u`. Image 23 gives

\[
C=\cos3\theta=-\sqrt6\,\operatorname{tr}(B^3)/j^{3/2}.
\]

The atlas assigns `C=0` when `j<=1e-24` to avoid the isotropic `0/0`. This is a numerical convention. At exact isotropy, `u=0` and the shape factor is `F=1` regardless of `C`.

Images 20 and 21 give

\[
a=\frac{\sqrt3(3-\sin\phi)}{2\sqrt2\sin\phi},\qquad
F=\sqrt{\frac{u^2}{8}+\frac{2-u^2}{2+\sqrt2uC}}-\frac{u}{2\sqrt2}.
\]

With `r=exp[-(3p/hs)^n]`, image 26 defines `ed=ed0*r`, `ec=ec0*r`, `ei=ei0*r`; image 25 defines positive compression pressure in the original tension-positive notation. Image 24 gives

\[
\begin{aligned}
f_d&=\left(\frac{e-e_d}{e_c-e_d}\right)^\alpha,&
f_e&=(e_c/e)^\beta,\\
f_b&=\frac{h_s}{n}\left(\frac{e_{i0}}{e_{c0}}\right)^\beta
\frac{1+e_i}{e_i}\left(\frac{3p}{h_s}\right)^{1-n}
\left[3+a^2-a\sqrt3\left(\frac{e_{i0}-e_{d0}}{e_{c0}-e_{d0}}\right)^\alpha\right]^{-1}.
\end{aligned}
\]

The complete stress law, from image 18 after convention conversion, is

\[
\dot\sigma=\frac{f_bf_e}{A:A}
\left[F^2D+a^2 A(A:D)-f_daF(A+B)\lVert D\rVert\right].
\]

The source uses tension-positive stress `T` and stretching. Reversing both gives the positive linear terms and negative norm term shown above: `dot(sigma)=-dot(T)`, while `norm(-D)=norm(D)`. Normalized stress and its invariants do not change. The implemented void-ratio continuity equation is

\[
\dot e=-(1+e)\operatorname{tr}D.
\]

This expresses constant solid volume in the chosen kinematics; it is not displayed in the inspected stress-law images. For prescribed constant stretching its analytical solution is `1+e=(1+e0)exp[-tr(D)*s]`, where `s` parameterizes the loading path. The native rate integrator approximates this equation numerically; it does not substitute the exact exponential update used by some residual models.

The source defines a corotational stress rate. The atlas equates it to the ordinary rate only under its declared zero-spin scope. Fixed-frame covariance checks do not establish finite-rotation objectivity.

## State, parameters, units and initialization

State consists of six effective Mandel stresses in Pa and dimensionless void ratio `e`. Defaults are `100 kPa I` and `.7`. There is no separate yield surface, accumulated plastic strain or time-dependent creep state.

| Parameter | Units | Default | Declared bounds |
| --- | --- | --- | --- |
| `p_ref` | Pa | `1e5` | `1 .. 1e10`; numerical scaling |
| `phi` | rad | `pi/6` | `.1 .. 1.2`; critical friction angle |
| `hs` | Pa | `5.8e9` | `1e6 .. 1e12`; granular hardness |
| `n` | 1 | `.28` | `.05 .. .9`; pressure exponent |
| `ed0` | 1 | `.53` | `.01 .. 2`; dense-limit void ratio |
| `ec0` | 1 | `.84` | `.02 .. 3`; critical-state void ratio |
| `ei0` | 1 | `1` | `.03 .. 4`; loose-limit void ratio |
| `alpha` | 1 | `.13` | `.01 .. 1`; density influence exponent |
| `beta` | 1 | `1.05` | `0 .. 5`; stiffness density exponent |

The eight physical defaults match the Karlsruhe row on the cited summary page, converting degrees to radians and MPa to Pa. They are not a Wichtmann-data calibration. `p_ref` is an additional project numerical scale.

The implementation requires `e>0`, `p>1e-8 p_ref`, `ed0<ec0<ei0`, `ed<e<ei`, `F>0` and `fb>0`. These checks exclude the dense boundary where a fractional-power derivative can become singular. They do not enforce positivity of every principal effective stress or guarantee physical admissibility of all allowed parameters. Specimen state and calibration must be supplied separately. Failed increments roll back to the exact original state.

## Numerical integration and evidence

The legacy rate API supplies a strain increment as the rate over a unit loading interval; it introduces no physical material clock. The common solver uses explicit midpoint with full-step/two-half-step comparison and recursive subdivision. Its error threshold is `1e-6` in model-scaled state coordinates; this is a local integration heuristic, not a validated error bound. The accepted solution is the two-half-step state. Depth and work limits remain fixed in this legacy path.

`tools/verify_hypoplasticity.py` computes references with ordinary 3-by-3 Cartesian matrices in the source's tension-positive convention. It neither evaluates the DSL nor calls the generated tensor operations. Integrated references use fixed-step classical RK4 and successive grid comparisons up to 4,096 steps under unchanged, declared convergence thresholds.

The initial 226-check attempt passed every rate comparison but failed reference convergence on reversal between 128 and 256 steps. That [failed evidence](../../catalogue/evidence/hypoplastic-sand-vw96-investigation-v1.json) is retained. Refinement to 1,024 steps resolves the reference-convergence criterion; the native path tolerance was not loosened.

The expanded suite has **229 checks**: 216 instantaneous rate comparisons across three pressures, two relative densities, four stress shapes and nine stretching directions; three oblique fixed-frame covariance comparisons; seven prescribed-strain histories including reversal; and three invalid-state rollback cases. Rate tolerances are `1e-4 Pa`, `1e-11` for void-ratio rate, and relative `1e-9`. Path tolerances are `1 Pa`, void ratio `1e-8`, and relative `2e-5`; the separate reference-grid thresholds are `.001 Pa`, void ratio `1e-11` and relative `1e-10`. Every path must satisfy the reference convergence test as well as the native comparison.

This is project-authored numerical verification, not independent authorship, an external implementation comparison or experimental validation. Full original-paper review, domain-limit studies, calibration and the separate IGS history law remain open. The formulation status is not promoted automatically.
