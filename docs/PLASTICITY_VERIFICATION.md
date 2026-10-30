# Plasticity verification: first investigation

This is the historical v1 investigation pinned in its evidence records, not independent review or experimental validation. Both formulations retain their existing catalogue status. The checker is original project code: it does not evaluate DSL expressions, call the production nonlinear solver for its reference calculations, or execute an external constitutive implementation.

The later [Drucker–Prager apex correction](models/drucker-prager-apex.md) replaces the direction regularization and passes an expanded 73-case check. The failing v1 reports below are retained; the MCC partition comparison remains unchanged.

## Conventions and reproducibility

Stress and strain are compression positive. Tensor vectors use Mandel components `xx, yy, zz, xy, yz, xz`; all shear components contain the factor `sqrt(2)`. Write `p = tr(sigma)/3`, `s = dev(sigma)` and `q = sqrt(3 s:s/2)`. The strain increment has trace `V`. Void ratio is updated by `1+e = (1+e_n) exp(-V)`. This exponential bookkeeping does not make these infinitesimal stress laws finite-strain models.

Build the native solver, then run:

```sh
python3 tools/verify_plasticity.py --model drucker-prager --output artifacts/drucker-prager-verification.json
python3 tools/verify_plasticity.py --model modified-cam-clay --output artifacts/modified-cam-clay-verification.json
```

On the historical source revision, each command returns nonzero while its report contains an unresolved comparison. Use each evidence record’s source commit to reproduce that revision. The current DP checker is expanded and passes after the apex correction. Reports retain complete case inputs, expected/actual states, tolerances, return codes, solver diagnostics, embedded catalogue identity and binary hash. The historical investigative failures are separate from the green CI acceptance suite; the corrected DP suite is now a native regression gate. Python unit tests check the reference calculations and reject selected incorrect results; they do not excuse a failing native comparison.

The additive `diagnostics` object in the increment API reports Newton iterations, accepted internal substeps and rejected attempts. These counters can include partial internal progress before a failed transaction; the returned state still rolls back completely. The multiplier `gamma` is transient and describes the last accepted internal step, not cumulative plastic deformation.

## Drucker–Prager reference

The atlas law is constant-stiffness, nonassociated perfect plasticity:

\[
f=q-Mp-c\leq0,\qquad g=q-M_d p,\quad
K=E/[3(1-2\nu)],\quad G=E/[2(1+\nu)].
\]

For the elastic trial, `p_t = p_n + K V`, `s_t = s_n + 2 G dev(de)` and `q_t = sqrt(3 s_t:s_t/2)`. On the smooth cone the independent return is

\[
\gamma=\max\{0,(q_t-Mp_t-c)/(3G+MKM_d)\},\quad
p=p_t+KM_d\gamma,\quad q=q_t-3G\gamma,\quad s=(q/q_t)s_t.
\]

For a trial beyond the apex, the ideal cone limit is `p=-c/M`, `s=0`, `gamma=(-c/M-p_t)/(K M_d)`, when `M,M_d>0`. The implemented direction uses `max(q,p_ref*1e-12)`; comparison with the ideal apex limit is therefore explicitly a limiting check, not an identity throughout that regularization zone.

Source scope: the [OpenSees documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/DruckerPrager.html) and [pinned implementation](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/DruckerPrager.cpp) describe a broader formulation. Reversing its tension-positive conventions and scaling its cone gives `M=3 sqrt(3/2) rho`, `Md=3 sqrt(3/2) rhoBar`, `c=sigmaY`. The atlas omits its hardening, tensile cutoff and optional pressure-dependent elastic update. This is a mathematical specialization, not a numerical comparison with OpenSees. Its `plastic_integrator` is the relevant source locator.

The 19 native cases cover isotropic elasticity, compression/extension, all shear planes, a mixed state, associated/nondilatant/J2 specializations, unloading/reversal, apex limits and failure rollback. **18 pass.** `near-apex-with-shear` fails: from `sigma_n=100 kPa I`, `e_n=.7`, use `de=(-.002,-.002,-.002,.00001,0,0)` and default parameters. The solver returns the exact initial state after nine internal accepted substeps and fifteen rejections. The ideal apex reference has `p=-8.333333 kPa`. Pure hydrostatic apex loading passes. The shear case remains a solver/regularization investigation; do not present general apex robustness as established.

Other restrictions: the parameter bounds do not enforce `Md<=M`. On the cone the plastic work is proportional to `c+(M-Md)p`, which can be negative for otherwise permitted inputs. Parameter admissibility and behavior at the apex need independent review. A nondilatant potential cannot correct hydrostatic tensile loading beyond the cone apex; that case checks rejection and exact rollback, not successful integration.

## Modified Cam Clay reference

The atlas uses `f=q^2+M^2 p(p-pc)`, associated flow normalized by the previous `pc_n`, endpoint stiffness `K=(1+e)p/kappa` and `G=3K(1-2nu)/(2(1+nu))`. Hardening is the project discretization

\[
\Delta\varepsilon_v^p=\gamma M^2(2p-p_c)/p_{c,n},\qquad
p_c=p_{c,n}\exp[(1+e)\Delta\varepsilon_v^p/(\lambda-\kappa)].
\]

The [Itasca formulation](https://docs.itascacg.com/itasca930/common/models/camclay/doc/modelcamclay.html), equations 15, 18–25, supplies a primary comparison for stiffness, yield and flow. Its explicit hardening/volume updates are different finite-step choices. The [Silbermann–Nagel report](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/web/content/docs/benchmarks/small-deformations/ModifiedCamClay/ModifiedCamClay_report.pdf), dated 28 June 2023, is another primary source: equation 30b uses `M^2`, whereas equation 11 prints a single `M`. The discrepancy was checked on rendered pages. Its section 3.1 direct backward-Euler hardening equation is also different from this atlas exponential update. Neither source establishes bitwise equivalence with the atlas algorithm.

Let `v=(1+e_n) exp(-V)`. For an elastic step the independent reference is `p=p_n/(1-v V/kappa)`, `pc=pc_n`, `s=s_n+2G dev(de)`. For isotropic plastic loading, `q=0` implies `p=pc`. Elimination reduces the problem to one scalar root, bracketed and solved by bisection:

\[
\log(p/p_{c,n})-
\frac{vV-\kappa(1-p_n/p)}{\lambda-\kappa}=0.
\]

Recover `Vp=V-kappa/v*(1-p_n/p)` and `gamma=Vp pc_n/(M^2 p)`. At critical state `p=pc/2`, `|q|=M pc/2`, coaxial isochoric shear preserves stress, void ratio and `pc`. For the chosen axisymmetric increment `(a,-a/2,-a/2)`, its multiplier is `|a|/M`.

The continuum isotropic references use `v=v0 exp(-V)`, with `p=p0 exp[(v0-v)/kappa]` for elastic compression and denominator `lambda` for normally consolidated plastic compression. The report checks refinement through 8, 16, 32 and 64 steps. Minimum observed order `.8` and final relative pressure error below `5e-4` were specified before the first comparison.

**19 of 20 comparisons pass**, including both refinement studies. The retained single-step comparison for an overconsolidated yield crossing differs because the production solver rejects the full step and takes two half-steps. Its pressure is `233234.691578 Pa`, compared with `235946.077388 Pa` for one full implicit step. Composing the independent scalar reference over two equal half-steps agrees within the original tolerance. This explains this discrepancy without declaring the one-step and partitioned algorithms equivalent. The report remains conservatively `failed` because its single-step comparison is retained. Future evidence should distinguish discretization applicability from a numerical disagreement and assess subdivision sensitivity through yield crossing.

Initialization requires positive `p,pc`, `lambda>kappa` and yield admissibility. Default `e,p,pc` are illustrative: the atlas has no normal-consolidation intercept parameter or automatic reconstruction of specimen history. Independent source review, broader noncoaxial plastic paths and experimental calibration remain open.
