# Linear elasticity — bounded source reconciliation

Task REVIEW-linear-elastic; coordinating parent, 1 November2026. The existing stress law is technically reconciled with its pinned primary implementation source. Its complete v0.3 contract and initialization are checked in memory; **scientific sign-off remains pending**. No root definition, schema/compiler, solver, model status or historical evidence is changed.

The [existing dossier](../../models/linear-elastic.md) and [pending v1 review](../../../catalogue/reviews/linear-elastic-source-v1.json) are preserved. This packet adds primary-source access receipts, an explicit source/project crosswalk, exact stiffness identities and current-Python residual checks against the saved analytical states. It is an additive reconciliation, not a new elastic formulation or independent human review.

## Identity and sources

The reference is OpenGeoSys commit `b5d0f115c75ee74a7cdbfad533625a550a416fda`, inspected as static source, not built or executed:

- [LinearElasticIsotropic.h](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticIsotropic.h): `MaterialProperties::lambda`, `mu`, `bulk_modulus`; `elasticTangentStiffness`.
- [LinearElasticIsotropic.cpp](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticIsotropic.cpp): `integrateStress`, `getElasticTensor`.
- [KelvinVector.h](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MathLib/KelvinVector.h): `kelvinVectorToSymmetricTensor` ordering documentation and `symmetricTensorToKelvinVector` shear scaling.

[Source receipts](source-receipts.json) pin exact retrieved bytes and access date. The files identify BSD-3-Clause. Sources are linked and hashed, not vendored; no author code was executed. Web-cache retrieval initially failed, and sandboxed direct fetch could not resolve the host; the subsequent permitted network fetch succeeded for all three pinned files. Source-reading claims concern that exact revision, not current OpenGeoSys documentation or all host processes.

## Equations and v0.3 crosswalk

[formulation-crosswalk.json](formulation-crosswalk.json) maps both derived coefficients, both equations and all three declared parameters. The full profile is a compression-positive Mandel incremental residual, local infinitesimal3D, fixed spatial frame, zero spin. `sigma` is a persistent symmetric Cauchy tensor and `e` a persistent invariant scalar. Explicit initialization requires both fields; examples are not substituted, and no preparation history is inferred.

| Source quantity | Atlas representation | Finding |
| --- | --- | --- |
| Young modulus, Poisson ratio | E[Pa],nu[1] | Source parameters may depend on t,x. Atlas fixes both for a run; no varying-parameter source behavior is claimed. |
| Source lambda,mu,bulk modulus | G=E/[2(1+nu)], K=E/[3(1-2nu)] | K=lambda+2G/3; lambda trace(de)I+2G de equals K trace(de)I+2G dev(de). |
| Source sigma_prev+C*(eps_m-eps_m_prev) | sigma-sigma_n-K trace(de)I-2G dev(de)=0 | Both stress/strain signs reverse together; source Kelvin order xx,yy,zz,xy,yz,xz and sqrt(2) shear scaling match Atlas Mandel storage. |
| Mechanical stress in the source material interface | Effective stress in the Atlas soil laboratory | Explicit Atlas host interpretation. These files alone do not specify a complete effective-stress/pore-pressure coupling process. |
| No source void-ratio evolution | e-(1+e_n)exp(-trace(de))+1=0 | Project bookkeeping, uncoupled from stiffness. Its exponential volume convention does not make stress finite-strain. |
| No material p_ref | Numerical stress/state scale | Project-only parameter; not a fitted elastic constant. |

The source takes mechanical strain supplied by its host. Atlas supplies its declared infinitesimal increment; it does not implement a thermal strain decomposition, arbitrary OpenGeoSys process fields or the source free-energy interface. Root parameter boxes E in[1,1e12]Pa and nu in[-.99,.499] are project exploration bounds inside E>0,-1<nu<.5, where K,G are positive. This is not a guarantee of conditioning arbitrarily near incompressibility. The e>0 domain is a project restriction: it can reject an otherwise finite elastic stress update. No tensile cutoff is imposed; elasticity can carry tension. The hypoplastic-host comparison restriction in Decision0004 does not apply to this elastic law.

## Temporal integration and transactions

There is no elapsed-time relaxation or material clock in this constant-parameter specialization. Source API t,x parameter evaluation does not imply a creep law. A zero increment leaves sigma,e unchanged. Each trial reads immutable committed sigma_n,e_n; accepted updates commit persistent fields, and generic failure handling must restore the parent. There are no yield events, plastic multipliers, history resets or source projection rules.

Analytically, constant stress increments add under subdivision and (1+e) factors multiply for additive trace increments. The common engine's numerical solves, roundoff and intermediate domain failures still affect implementation behavior. This packet checks algebra and residual evaluation, not current compiled trial/rollback/control paths. Stress tangent C is constant; bookkeeping derivative with respect to incremental volumetric strain is -(1+e_new). No generic solver extension is needed.

## Reproducible checks and limits

```sh
python3 docs/ingestion/linear-elastic/check_crosswalk.py --repo .
```

[Saved results](crosswalk-checks.json) record eight contract/initialization checks: exact root identity, complete v0.3 validation, full field mapping, unchanged explicit state, missing sigma/e rejection, e=0 rejection and intended tensile-state admission. Exact rational algebra verifies all six stiffness columns at five Poisson ratios, including both declared bounds (30 column checks), and positive K/G plus the Lamé/bulk identity in each regime.

The existing [29-case native analytical evidence](../../../catalogue/evidence/linear-elastic-analytical-v1.json) and its report hash are verified. Its **expected states**, prescribed total strains and parameters satisfy the current Python residual under the saved tolerance budgets in all29 cases. These checks are not a fresh native execution or a reproduction of mixed-control/cyclic trajectories: they test each saved net analytical endpoint against the unchanged model. Historical actual outputs, failures and binary identity retain their original meaning. No new numerical tolerances were selected from these residual observations.

The new [pending v2 source review](../../../catalogue/reviews/linear-elastic-source-v2.json) narrows remaining work to independent scientific assessment of the source mapping, project void convention/host scope and numerical evidence. This automated technical reconciliation supplies no independent authorship signature or soil calibration. Finite rotations/strain, changing source fields, nearly incompressible conditioning, poroelasticity and experimental prediction remain outside the established claim. REV-01 remains open.

## Handoff

Source access and this bounded mapping task are complete. Existing executable support is unchanged; historical native numerical evidence is retained; current Python/algebra checks are additive; scientific admission is pending. The next review action is a signed assessment of this bounded source/evidence package, not a new constitutive implementation or solver workstream. Other existing review/ingestion tasks can proceed independently. No build, push or deployment occurred.
