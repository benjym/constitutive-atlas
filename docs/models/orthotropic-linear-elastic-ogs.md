# Orthotropic linear elasticity — full nine-constant OGS law

The source-complete, independently agent-approved formulation is available in the general atlas laboratory. Native/Wasm qualification and actual packaged-browser checks are complete for bounded synthetic cases; current merged-release CI and live verification are tracked separately in the delivery ledger. The presets are illustrative, with no experimental validation.

Main laboratory: https://benjym.github.io/constitutive-atlas/index.html#laboratory?model=orthotropic-linear-elastic-ogs

Public source mapping and scientific report: https://benjym.github.io/constitutive-atlas/material-point-orthotropic/review.html

Exact accepted scientific checklist: https://benjym.github.io/constitutive-atlas/material-point-orthotropic/review.json

Exact approval: https://benjym.github.io/constitutive-atlas/material-point-orthotropic/approval.json

Exact definition: https://benjym.github.io/constitutive-atlas/material-point-orthotropic/model.json

Repository delivery ledger: https://github.com/benjym/constitutive-atlas/blob/main/docs/ingestion/orthotropic-ogs/DELIVERY.md

## Exact identity and source

Model ID orthotropic-linear-elastic-ogs, schema v0.3, definition SHA256 60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14. Exact OpenGeoSys commit b5d0f115c75ee74a7cdbfad533625a550a416fda, BSD-3-Clause, fixed aligned-axis branch. Seven readable source originals and receipts are retained privately; supplied author code/binaries were not executed.

Governing compliance/stress update: https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticOrthotropic.cpp (lines60–73 compliance/inverse;21–44 incremental stress;74–91 identity-Q branch).

Engineering constants/reciprocity: https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticOrthotropic.h (lines21–87,104–116,136–146).

Kelvin ordering: https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MathLib/KelvinVector.cpp (lines67–74,119–130).

## Formulation and host contract

Parameters: E1,E2,E3,G12,G23,G13 in Pa, then dimensionless nu12,nu23,nu13. Reciprocal ratios nuji=nuij*Ej/Ei. The symmetric normal compliance has diagonal1/Ei and S12=-nu12/E1, S13=-nu13/E1, S23=-nu23/E2. Mandel shear compliances are1/(2G12),1/(2G23),1/(2G13). C=inverse(S); sigma_next=sigma_previous+C:delta_epsilon.

All moduli must be positive; all normal pair principal minors and the full normal determinant must be positive. Broad numerical conditioning across the machine parameter envelope is unqualified. Domain checks reject invalid materials without committing state.

Six persistent stresses, ordered xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz; all six strain increments are prescribed. Small strain, fixed material axes aligned with the caller Cartesian axes, zero objective rate, dry total Cauchy stress. Atlas explicitly chooses compression-positive stress/strain; the inspected source does not label its scalar sign convention. Simultaneous reversal leaves this linear stiffness unchanged.

This is a strain-path incremental-residual interface, with no physical clock, mixed stress controls or hidden history. Initial stress is the complete restart state; zero increments hold it, reversals are elastic, failure rolls back the full six-state vector, and the update derivative is the complete6x6 stiffness. Cumulative plotted strain is relative to the supplied starting state, not a reconstructed initial deformation.

## Evidence and limits

Independent source algebra uses exact rational compliance inversion:16material sets,128endpoints,768stress residuals,576inverse identities and128energy checks. Frozen native/Wasm studies exercise121requests per backend,648state values,144tangent entries,13rejection/recovery pairs, partition/restart and the public load/reverse/hold preset. A separate agent uses Decimal80 Cholesky, independently of the production cofactor expressions and parent reference implementation.

The main laboratory exposes all nine constants, all-six prestress/increments, plots and full state, strict fresh-result export/import replay, reset and failure recovery. Current-release qualification and deployment receipts remain in the repository ledger; historical source-only worker packets retain their original status statements.

No arbitrary material-axis rotation, finite strain/rotation, thermal/poro coupling, general parameter-envelope, mixed-control, calibration or experimental-validation claim is made. No compatible permitted experimental dataset is supplied; measurement overlays are unavailable for this model.
