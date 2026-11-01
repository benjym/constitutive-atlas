# Linear isotropic elasticity: admission decision sheet

Current definition: `33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041`; schema `0.1`; status `transcribed`.

Pending canonical review: [linear-elastic-source-v2.json](../../../catalogue/reviews/linear-elastic-source-v2.json). Its exact definition binding was checked, not accepted.

Proposed release: the fixed-frame, small-strain material-point scope in [README.md](README.md). Explicit input state is required by the reviewed consumer contract; legacy low-level default behavior is not claimed to have changed. All decisions below are unsigned proposals.

## EL-01: Accept the constant-E/nu source specialization and paired stress/strain sign plus Mandel mapping?

Accept the constant isotropic infinitesimal law only; source fields varying with position/state are excluded.

Read: [README.md](../../../docs/ingestion/linear-elastic/README.md), [source-receipts.json](../../../docs/ingestion/linear-elastic/source-receipts.json).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## EL-02: Accept effective-stress interpretation and exponential void bookkeeping as explicit Atlas host/numerical choices?

Do not attribute the void update to the OGS elasticity source or infer poromechanics/finite strain.

Read: [linear-elastic.md](../../../docs/models/linear-elastic.md), [formulation-crosswalk.json](../../../docs/ingestion/linear-elastic/formulation-crosswalk.json).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## EL-03: Do the analytical tensor/control cases and independent rational checks support the named numerical claim?

Assess 29 native cases separately from 30 rational stiffness columns and saved endpoint residuals; no all-parameter conditioning theorem.

Read: [linear-elastic-analytical-v1.json](../../../catalogue/evidence/linear-elastic-analytical-v1.json), [crosswalk-checks.json](../../../docs/ingestion/linear-elastic/crosswalk-checks.json).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## EL-04: Is explicit stress/e state with examples-only defaults sufficient for this material-point scope?

Accept explicit mechanical inputs; exclude soil calibration and source-matched physical specimen preparation.

Read: [formulation-crosswalk.json](../../../docs/ingestion/linear-elastic/formulation-crosswalk.json).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## EL-05: Which parameter/control region and release checks must the pinned reviewed release retain?

Retain named analytical/control/rollback regressions; separately qualify nearly incompressible behavior and any FE-host tangent claim.

Read: [linear-elastic-analytical-v1.json](../../../catalogue/evidence/reports/linear-elastic-analytical-v1.json), [FORMULATION_CONTRACT.md](../../../docs/FORMULATION_CONTRACT.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## Reproduction and final release

Run the parent packet preflight. Existing source/algebra checks and saved reports are verification inputs, not fresh compiled execution. After independent acceptance, prospectively pin a new release build/check matrix and retain every outcome. A reviewer may request a narrower scope or a specific new study; model status remains unchanged until that process is completed.
