# Orthotropic linear elasticity — exact OGS formulation

Task ID: ING-orthotropic-ogs-v1. Owner: orthotropic_source; 2026-11-02.
Owned scope: this new source-v1 directory and ignored `.local/private-sources/orthotropic-ogs/`. Source-only child of MODEL-orthotropic-ogs; the parent owns E0–E8 and the delivery ledger. This handoff does not close the model task.

## Identity and sources

The exact formulation is **full nine-constant, three-dimensional infinitesimal orthotropic linear elasticity**, as implemented by the OpenGeoSys Community at commit `b5d0f115c75ee74a7cdbfad533625a550a416fda`, with material axes1,2,3 aligned to caller Cartesian x,y,z. The identity is the pinned source implementation, rather than a guessed foundational publication or another OGS revision.

[LinearElasticOrthotropic.cpp](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticOrthotropic.cpp) lines60–73 construct and invert the complete Kelvin compliance. Lines21–44 give the incremental stress and consistent tangent. Lines74–91 explicitly select identity Q when no local coordinate system is supplied. The Atlas specialization uses that branch; arbitrary material-axis rotations and finite rotations are outside its executable scope.

[LinearElasticOrthotropic.h](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticOrthotropic.h) lines21–87 define engineering constants and reciprocal ratios,104–116 sample parameter vectors,136–146 give elastic energy. [KelvinVector.cpp](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MathLib/KelvinVector.cpp) lines67–74 and119–130 verify tensor conversion and order. All seven complete primary files, including factory, Kelvin header/implementation and exact license, were downloaded, read and hashed; source-receipts.json gives durable private paths, URLs, access timestamps, SHA-256 and line locators. No PDF was needed.

Existing inventories and Downloads were checked first; acquisition.json records the search and failed access attempts. The existing isotropic packet uses this same pinned commit and provides prior Kelvin provenance, but does not contain this nine-constant law. No existing model or historical receipt was changed. The exact license is BSD-3-Clause (OpenGeoSys Community2012–2026); notice, conditions and disclaimer remain in ignored LICENSE.txt. This packet links/hashes original code and contains independently written declarative transcription/algebra checks. No author binary or supplied source program was executed. Raw originals stay private; no endorsement is implied.

## Equations and schema crosswalk

Target: [v0.3 schema](../../../../schemas/model-v0.3.schema.json) and [formulation contract](../../../FORMULATION_CONTRACT.md). candidate.json is a complete structurally/semantically checked proposal; it does not modify the root catalogue/model.

Parameter order is E1,E2,E3,G12,G23,G13,nu12,nu23,nu13. Young/shear moduli are Pa and Poisson ratios dimensionless. All nine are independent subject to positive definiteness. Under uniaxial stress along i, nu_ij is minus the strain along j divided by strain along i. The source derives nu_ji=nu_ij E_j/E_i; reversing indices changes the law. Source G/nu vector order is12,23,13.

The symmetric compliance has normal block

```
S = [1/E1,      -nu12/E1, -nu13/E1;
     -nu12/E1,  1/E2,    -nu23/E2;
     -nu13/E1, -nu23/E2,  1/E3]
```

and shear diagonal `[1/(2G12),1/(2G23),1/(2G13)]`; other normal/shear entries vanish. C=S^-1. The source update is sigma_(n+1)=sigma_n+C:de. The candidate residual is sigma−sigma_n−C:de=0, using six independent normal-block coefficients and all three Mandel shear increments 2Gij de_ij.

Define r21=E2/E1, r31=E3/E1, r32=E3/E2 and Delta=1−nu12²r21−nu13²r31−nu23²r32−2nu12nu23nu13r31. Then:

- C11=E1(1−nu23²r32)/Delta; C22=E2(1−nu13²r31)/Delta; C33=E3(1−nu12²r21)/Delta.
- C12=E2(nu12+nu13nu23r32)/Delta; C13=E3(nu13+nu12nu23)/Delta; C23=E3(nu23+nu12nu13r21)/Delta.

These are algebraic inverses of the inspected compliance, not another empirical law.

| Source locator | Quantity / equation | Schema representation / status |
| --- | --- | --- |
| Header21–87; factory26–43 | Nine constants and reciprocal nu | Exactly9 parameters in source vector order, SI Pa/1; reciprocal ratios derived |
| cpp60–73 | Full3D S and C=S^-1 | Dimensionless determinant, six normal C coefficients, all3shear terms |
| cpp21–44 | sigma_prev+C*(eps_m−eps_m_prev) | strain_path/incremental_residual; finite infinitesimal de; no physical duration |
| cpp74–91 | Q=I if no local coordinates | small_strain_3d, fixed_spatial, objective_rate:none; axes aligned |
| Kelvin header170–223; cpp67–74,119–130 | Orthonormal shear map | Mandel [xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz] |
| cpp28–38 | Mechanical strain/stress | Persistent sigma[6], Pa, Cauchy stress; source does not establish pore/effective split; dry total scope is explicit Atlas specialization |
| Header136–146 | energy eps dot sigma/2 | Independent energy check for compatible zero-origin elastic strain; no fabricated energy state |

The code does not explicitly label its scalar sign convention. Atlas compression-positive stress AND strain simultaneously negate tension-positive variables if applicable; the homogeneous linear law and bilinear energy are unchanged. This is explicit representation conversion, not a claimed source sign label. No pressure-dependent or tension-cutoff branch exists in the inspected law; finite initial compressive, tensile and shear stresses are allowed as reference prestress. Stress is a spatial tensor under passive basis re-expression, but this executable contract does not implement re-expression of directional constants or finite transport. Only the aligned frame can be executed.

Exactly one persistent symmetric state, sigma, has six components. Explicit initialization requires all six finite values. Zero stress is illustrative, not implicit preparation. Supplied prestress defines the reference state; no stored total strain is needed for subsequent increments. To evaluate energy relative to an unstressed reference, the host must supply compatible elastic strain S:sigma and its reference convention. No void ratio, plastic strain or other internal strain is present or fabricated.

The physical domain requires Ei>0, Gij>0 and positive-definite normal compliance. All3pair minors `1−nuij² Ej/Ei>0` and Delta>0 are declared. With positive diagonal these are necessary/sufficient; Sylvester first2minor and determinant suffice, with the other pair conditions explicit redundant guards. These mathematical stable-elasticity conditions are not checks implemented by the inspected OGS inverse. No universal isotropic nu<.5 restriction applies: checks include admissible nu12=.8. Widget bounds1Pa–1TPa and −10≤nu≤10 are project exploration bounds, not calibration/source range claims. Default E=[30,45,60]MPa,G=[12,18,15]MPa,nu=[.2,.25,.15] is illustrative. No broad floating-point conditioning envelope near singular compliance is claimed. E1 doubles as numerical stress scale without adding a tenth parameter.

## Temporal integration and transactions

This is a rate-independent incremental relation with fixed constant parameters. OGS parameters may depend on t,x; Atlas supplies constants. Source reads previous temperature but getElasticTensor ignores it. No thermal strain, time variation, pore pressure, viscosity or rate input is added. Only de is supplied, with empty advance context. Hold duration has no meaning; zero de preserves all stress components mathematically. Subdivision and linear load/unload superposition must reproduce unsplit increments numerically. There is no yield/history/reset event or constitutive discontinuity inside the domain. Changing parameters between updates is outside this record's qualified trajectory semantics.

Each residual uses committed sigma_n and trial sigma. Accepted updates commit all6state; repeated trials restart from the same parent; failures return the complete incoming state without partial commits. These are Atlas transaction guarantees, not an assertion about an undocumented OGS rollback API. Restart preserves constants, fixed-axis identity and all6stress values. No density preparation is required. The residual Jacobian with respect to trial stress is identity; constitutive d sigma/de is symmetric positive-definite C. Mixed stress/strain loading uses the existing host control solver. No custom kernel/schema/compiler function is required. Singular parameters may reject during derived evaluation before domain predicates (division by zero); rejection timing/type does not establish physical acceptance.

## Independent checks

reference-policy.json was frozen before results and any compiled execution. verify.py constructs the inspected6x6 compliance and independently inverts it by exact rational Gauss–Jordan elimination, without candidate stiffness cofactors. It checks reciprocity, Sylvester positivity, C*S=I and positive quadratic energy, then compares the separately declared DSL residual at exact endpoints. The interpreter checks the transcription; it is not itself an independent constitutive reference.

Run from repository root:

```
python3 -B docs/ingestion/orthotropic-ogs/source-v1/verify.py
```

checks.json:16parameter sets (default, auxetic, Poisson>.5, isotropic limit and12varied orthotropic cases);128endpoints with six independent strain components, mixed normal/shear and zero increment;768scalar residual checks;576exact inverse identities;128energy checks; seven invalid-domain rejections. Maximum residual5.820766091346741e-11Pa is below frozen1e-6Pa gate. references.json retains exact rational/rounded endpoints, parameters, prestress and increments. The initial dimensional-comparison validation failure is retained; correcting dimensional zero syntax changed no physical condition or gate. Acquisition records also preserve the disk-space write failure and subsequent coordinator recovery. Nothing was deleted by this worker.

Source originals can be rehashed against receipts. Proposed candidate SHA is in checks/manifest. No native/Wasm/browser build or compiled call was run. No experimental calibration/validation or scientific admission is claimed.

## Handoff

Files: README.md; candidate.json; create_candidate.py; source-receipts.json; acquisition.json; reference-policy.json; verify.py; checks.json; references.json; retained-initial-validation-failure.txt; manifest.json. Seven exact ignored originals remain in `.local/private-sources/orthotropic-ogs/`.

Source completeness: complete for this9constant aligned3D constant-parameter specialization. Executable support: candidate validates on existing DSL/schema; shared/native/Wasm integration remains parent-owned. Numerical verification: exact algebra/uncompiled residual checks pass; compiled backend/control/restart/browser checks outstanding. Scientific admission: not independently reviewed by this author; separate agent reviews exact frozen source/model/reference/backend evidence. Atlas/live delivery remain outstanding under parent MODEL-orthotropic-ogs.

No source blocker or shared capability gap found. Next action: parent integrates the candidate into its dedicated common-engine package, freezes compiled-study endpoints/gates, tests all6stiffness columns and mixed histories/restart/zero-load/failure recovery, then dispatches independent scientific review. The full umbrella stays open through E8. Compiled backend agreement alone cannot establish source-equation correctness.


Current complete delivery status and scientific/interface qualifications are recorded in [the model ledger](../ingestion/orthotropic-ogs/DELIVERY.md). Fixed material axes remain aligned with the caller frame.
