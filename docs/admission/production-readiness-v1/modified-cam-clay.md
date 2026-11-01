# Modified Cam Clay: admission decision sheet

Current definition: `e075117e07a71a17a35ce47dac66172a0cc402860f5c6cf106f7883db5721a14`; schema `0.1`; status `transcribed`.

Pending canonical review: [modified-cam-clay-source-v3.json](../../../catalogue/reviews/modified-cam-clay-source-v3.json). Its exact definition binding was checked, not accepted.

Proposed release: the fixed-frame, small-strain material-point scope in [README.md](README.md). Explicit input state is required by the reviewed consumer contract; legacy low-level default behavior is not claimed to have changed. All decisions below are unsigned proposals.

## MCC-01: Approve M-squared yield and selected volume balance despite the source Eq11/Eq30b and Eq7/Eqs8-9 conflicts?

Accept the explicitly derived selected branch only; record that this is not verbatim equivalence to all printed equations.

Read: [README.md](../../../docs/ingestion/modified-cam-clay/README.md), [source-receipts.json](../../../docs/ingestion/modified-cam-clay/source-receipts.json).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## MCC-02: Accept endpoint pressure/volume stiffness and gamma/pc_n flow normalization?

Treat these as named Atlas finite-step choices, distinct from source lagging and gradient-norm multiplier normalization.

Read: [modified-cam-clay.md](../../../docs/models/modified-cam-clay.md), [formulation-crosswalk.json](../../../docs/ingestion/modified-cam-clay/formulation-crosswalk.json).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## MCC-03: Accept exponential volume/log-pc updates and temporary multiplier semantics?

State persistent sigma/e/pc and final-subsolve gamma separately; no finite-deformation or elapsed-time law.

Read: [README.md](../../../docs/ingestion/modified-cam-clay/README.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## MCC-04: Does the scalar/tensor/refinement evidence support the requested bounded discrete implementation?

Review 57 passing cases separately from the failed unpartitioned v1; actual-partition agreement is not a general adaptive-error proof.

Read: [modified-cam-clay-scalar-v2.json](../../../catalogue/evidence/modified-cam-clay-scalar-v2.json), [modified-cam-clay-investigation-v1.json](../../../catalogue/evidence/modified-cam-clay-investigation-v1.json).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## MCC-05: Accept explicit admissible sigma/e/pc with illustrative OCR, without an inferred calibrated NCL state?

Require caller-supplied consolidation/preparation for experiments; do not derive a material NCL intercept from example values.

Read: [formulation-crosswalk.json](../../../docs/ingestion/modified-cam-clay/formulation-crosswalk.json), [README.md](../../../docs/ingestion/modified-cam-clay/README.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## MCC-06: Which further branch/control/parameter checks are necessary for the proposed release claim?

Exclude global branch uniqueness, near-singular parameter behavior, full FE tangent qualification and calibrated prediction unless separately evidenced.

Read: [modified-cam-clay-source-v3.json](../../../catalogue/reviews/modified-cam-clay-source-v3.json), [FORMULATION_CONTRACT.md](../../../docs/FORMULATION_CONTRACT.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## Reproduction and final release

Run the parent packet preflight. Existing source/algebra checks and saved reports are verification inputs, not fresh compiled execution. After independent acceptance, prospectively pin a new release build/check matrix and retain every outcome. A reviewer may request a narrower scope or a specific new study; model status remains unchanged until that process is completed.
