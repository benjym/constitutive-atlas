# Linear isotropic elasticity: transcription dossier

Formulation ID: `linear-elastic`. Status: **transcribed; independent review pending**. This dossier records the implemented scope and an analytical verification procedure. It does not certify a soil calibration or scientific admission.

## Sources and variant

The original atlas link led to a moved OpenGeoSys documentation page. Its [current replacement](https://www.opengeosys.org/stable/docs/userguide/blocks/misc/constitutive_relations/) has an empty isotropic-elasticity section and cannot substantiate equation extraction. The replacement references are actual primary implementation sources, pinned to OpenGeoSys commit `b5d0f115c75ee74a7cdbfad533625a550a416fda`:

- [LinearElasticIsotropic.h](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticIsotropic.h): `MaterialProperties::lambda`, `mu`, `bulk_modulus`, and `elasticTangentStiffness`.
- [LinearElasticIsotropic.cpp](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticIsotropic.cpp): `integrateStress` and `getElasticTensor`.

These files identify standard constant-coefficient isotropic elasticity, rather than a soil-specific nonlinear law. Source files are linked, not vendored. OpenGeoSys labels them BSD-3-Clause; the atlas checker is an original analytical calculation and does not execute or copy an OpenGeoSys kernel. This is not a cross-code numerical comparison.

## Conventions and complete equations

Both stress and infinitesimal strain are compression positive in this atlas. Reversing both from tension-positive conventions preserves the linear constitutive relation. The six symmetric components are ordered `xx, yy, zz, xy, yz, xz`, with each shear component multiplied by `sqrt(2)` (Mandel notation). Engineering shear is twice the Cartesian tensor shear; these are distinct conventions.

The constant elastic coefficients are

\[
G=\frac{E}{2(1+\nu)},\qquad
K=\frac{E}{3(1-2\nu)},\qquad
\lambda=\frac{E\nu}{(1+\nu)(1-2\nu)}.
\]

For an increment \(\Delta\varepsilon\), the implemented stress residual is

\[
R_\sigma=\sigma_{n+1}-\sigma_n
-K\,\mathrm{tr}(\Delta\varepsilon)I
-2G\,\mathrm{dev}(\Delta\varepsilon)=0.
\]

This equals the pinned source's incremental stiffness relation. In Cartesian components its independent analytical form is

\[
\Delta\sigma_{ii}=\lambda\sum_j\Delta\varepsilon_{jj}+2G\Delta\varepsilon_{ii},
\qquad \Delta\tau_{ij}=G\Delta\gamma_{ij}\quad(i\ne j).
\]

The additional scalar is atlas void-ratio bookkeeping:

\[
e_{n+1}=(1+e_n)\exp[-\mathrm{tr}(\Delta\varepsilon)]-1.
\]

This is a project choice for logarithmic volumetric bookkeeping and a constant solid volume assumption; it is **not** part of the linked OpenGeoSys elasticity state. Its first-order expansion is consistent with compression reducing void ratio. Its exponential form does not extend the stress law to finite strain. Void ratio has no influence on elastic stiffness. The schema residual for this equation and the `e > 0` domain restriction are project choices, not equations attributed to OpenGeoSys.

## State, parameters and initialization

| Quantity | Unit | Role and restrictions |
| --- | --- | --- |
| `sigma` | Pa | Six Mandel stress components; default isotropic compression of 100 kPa, zero shear. Initial stress can be supplied explicitly. |
| `e` | 1 | Bookkeeping scalar; default 0.7, strictly positive. |
| `E` | Pa | Constant Young modulus; default 30 MPa, declared numeric bounds 1 Pa–1 TPa. |
| `nu` | 1 | Constant Poisson ratio; default 0.25, declared bounds −0.99–0.499. These bounds keep the model within the positive-definite elastic range and away from singular endpoints. |
| `p_ref` | Pa | Solver scaling only; default 100 kPa, declared bounds 1 Pa–10 GPa. It does not enter the elastic law. |

Defaults are illustrative, not values calibrated to a Wichtmann material. No plastic strain, yield surface, hardening, pore-fluid state or consolidation history is present. Initial stress offsets do not imply a modeled preparation process. No tensile cutoff is imposed; the elastic stress law can carry tension. A step violating the void-ratio domain must fail through the generic integration/domain checks.

## Numerics and applicability

The common residual integrator solves both state equations. Constant-coefficient stress response is exactly linear in the total prescribed strain; subdivision should not change it beyond solver roundoff. The engine still uses its generic Newton tolerances, scaling and transactional state update. There is no separate handwritten elasticity kernel.

The scope is local 3D infinitesimal strain in a fixed frame, with zero spin. Fixed-frame covariance tests do not establish finite-rotation objectivity. The model contains no physical time scale, creep, plastic dissipation, pore-pressure evolution law or inertial dynamics. The browser's undrained pore-pressure quantity is a driver reconstruction from its imposed boundary assumptions, not an additional constitutive prediction.

## Analytical evidence and reproduction

Run from a repository checkout:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
python3 tools/verify_elasticity.py --output artifacts/elasticity-evidence.json
```

The checker uses the Cartesian Lamé equations and converts engineering shear to Mandel components. It does not use the model DSL, generated equations or their Python interpreter to calculate expected values. There are 24 prescribed tensor cases: eight paths (hydrostatic, deviatoric, each of three shear planes, mixed, unloading and zero increment) at three parameter regimes (`nu = 0.25, -0.2, 0.49`), including nonzero initial shear stresses. Five additional cases check drained triaxial, undrained triaxial, oedometer and isotropic strain controls, plus an undrained reversal cycle.

For axial strain `x`, the boundary-condition solutions are: drained radial strain `−nu*x` and axial stress increment `E*x`; undrained radial strain `−x/2`; oedometer radial strain zero; and isotropic strain `x` in each normal component. The checker compares the resulting full stress and void-ratio states. It does not use solver-reported strain to construct the expected solution for the mixed-control cases.

Acceptance thresholds are fixed in the checker before execution: absolute stress error `1e-4 Pa`, absolute void-ratio error `1e-10`, plus relative tolerance `1e-10` times the expected component magnitude. Full inputs, expected/actual states, per-case outcomes, maximum tolerance ratios, executable hash, Python/platform information and embedded catalogue hash are retained. Failures remain in the report and produce a nonzero exit code.

See [evidence records](../EVIDENCE_RECORDS.md) for the integrity envelope, current-definition checks and review workflow. An oracle using a different mathematical expression is useful numerical evidence; it is not independent human authorship. The pending [review record](../../catalogue/reviews/linear-elastic-source-v1.json) identifies the remaining independent source/equation/numerical review. Model status is unchanged.
