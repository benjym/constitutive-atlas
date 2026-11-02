# Physical-time runtime profile v2

A generic mixed-control backward-Euler schedule runtime with an admissible explicit predictor for the initial Newton guess. It contains no model-specific equations or model-ID branches. Current prescribed strain rates and previous solved stress-control strain rates form the predictor; the incoming RHS uses t0, and the complete residual/domain is validated at t1. Invalid predictors retain the previous-state guess. Residual, generated constitutive equations, domain, nonlinear acceptance, line search, adaptive estimator and transactions are unchanged.

Select this include directory before cpp/include for a target that requires this profile. Unoverridden headers resolve to the common runtime. The full schedule header is byte-identical to the independently reviewed generic predictor implementation fd05b08d422468802fb788386a2f19463dec65ca66e3cf2153f837a5db0d2702. The legacy common schedule remains exact5c90e6cede9f24f124286cf10e2254a47a991e5d62f9bc7b3899ed62e6deb7e9. Existing targets retain their previous source identities unless explicitly opted in.

CMake selects this profile for the Bingham generic-engine consumer and the generic time solver/predictor regressions. Actual include order, object dependency files and source/tool/artifact receipts must prove the chosen header before material observations. New runtime/source identity requires qualification; identical model metadata alone is insufficient.

This improves initialization at some domain/branch boundaries. It does not prove general nonsmooth convergence, repair the backward-Euler transition estimator, change the direct midpoint API, or broaden any model's qualified scope. Bingham still requires its fixed maximum-step contract and full independent native/Wasm numerical study.
