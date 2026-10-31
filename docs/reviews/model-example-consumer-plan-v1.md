# Complete model examples in the laboratory — implementation plan v1

Motivation: the clay2013 [actual-driver study](../../catalogue/investigations/clay2013-preview-v1/RESULTS.md) fails its universal100kPa drained default. The source-linked candidate's declared example is10kPa. The present consumer resets other model fields while retaining a separate universal stress value. A source-valid explicit-state contract does not guarantee mixed-control solvability.

## Required behavior

Selecting a model or pressing a clearly labelled **Load model example** action loads its declared default parameters and complete declared initial state together. Stress comes from the selected definition, including axial/radial ratio; every persistent scalar/tensor field is copied. Temporary slots keep their declared zero-start semantics. Never substitute a different stress, change a parameter to fit the path, project a state or repair a rejected example silently.

Use visible wording: **Illustrative model example. These values do not establish specimen preparation or experimental calibration.** Existing model description and source links remain available. Manual parameter/state edits remain possible; loading an example explicitly replaces those edits. Run import must restore its own complete specification after any form population. Loading an example leaves protocol, loading history, increment count and numerical settings as selected; it does not imply every selected protocol succeeds.

The current laboratory supports positive axisymmetric effective stress in a first Mandel stress slot. Validate a model example against this consumer representation before populating it: complete finite shape, first-slot stress binding, equal radial components and zero shear, positive supported confinement, representable axial/radial ratio and control bounds. If an example is unsupported, give a clear error rather than approximate it. This is a consumer capability check, not material-domain or physical-preparation validation. A future general tensor-state laboratory can widen support under its own contract.

Keep the helper generic and independent of model IDs. Existing seven root definitions all declare100kPa spherical stress, so their initial selection/reset examples should remain numerically unchanged. A synthetic source-independent10kPa example tests that the consumer no longer inserts100kPa. Test a tensor history slot and temporary plastic slots, parameter copies, no input mutation, invalid/asymmetric/nonfinite examples and import/manual-state preservation where relevant.

## Verification before candidate installation

1. Review the source/default-control packet and record its numerical/physical limits.
2. Implement/test the generic consumer and visible action; confirm source links and editable controls in a real browser.
3. Freeze a distinctly identified clay2013 settings-aware driver/browser study using the actual new consumer example, including all five protocols, default1%/100step path, zero/reject/recovery checks, independent controls/void closure and native/Wasm parity. Declare every budget before observation.
4. Keep the original100kPa default failure and its unchanged acceptance in preview-v1. A new consumer example does not make that gate pass.
5. Install an explicitly limited local draft only if the separately frozen intended-use gates pass. Scientific admission and experimental preparation remain independent.

This document specifies work still to implement; it does not change the website, model count, source equations, initialization validation, numerical tolerances or deployment.
