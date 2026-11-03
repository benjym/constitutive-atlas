# Independent prospective native fixture review

Accepted the exact proposed hashes in `review.json`. No blocking findings.

Distinct v6 inherits v5 GIS depth, OCC packing/restart and Duncan scalar-history fixture settings. Existing strict/default and named v2-v5 branches retain the same settings; only v6 enables S-CLAY1 projection and covariance fixtures.

Normal-fabric FD direction is scale_j*(e_j−(1,1,1)/3), preserving zero trace. AD is projected with the matching derivative combination, dividing the existing Jet column scales correctly. Independent exact-rational unequal-scale check passes. Shear directions and every other model remain unchanged. h=1e-6 and 3e-5 scaled derivative tolerance are unchanged.

Positive projected directions span the rank-two normal trace-free subspace, with all three fabric shear directions retained. Explicit invalid 1e-6 trace perturbation must be rejected against the unchanged 1e-9 domain requirement. No ambient trace-direction derivative is claimed.

The covariance mapping equals R A R^T for the proper 90-degree xy rotation. Source-supported anisotropic initial stress and nonzero deviatoric fabric both rotate, while imposed de rotates consistently. Stress covariance remains .01 Pa; added fabric 1e-9 and persistent-scalar 2e-8 checks strengthen coverage. This is fixed-frame covariance, not finite-rotation objectivity.

Strict checker adds a closed exact-sixteen mapping consisting of prior fifteen hashes plus the accepted S-CLAY1 definition hash. Old exact fifteen/fourteen branches and historical behavior remain unchanged. Existing OCC analytical residual 2e-10 gate, exact message, knot/work/rollback wording and unknown-profile guards are unchanged. New pure tests reject changed hashes, extra/missing models and changed trial count.

Qualification workflow selects v6 for numerical/recorded tests on both native operating systems and retains strict-negative checker. Existing build, scientific and numerical thresholds are unchanged.

No model, compiler, schema or runtime diff exists relative HEAD; definition/review/approval bytes remain identical.

Pure verification: four historical/current strict fixture contract tests, source rational projection check, and independent unequal-scale AD projection and tensor rotation checks passed. No compiled artifacts were built or executed.
