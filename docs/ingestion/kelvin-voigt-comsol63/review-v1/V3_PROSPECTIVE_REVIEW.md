# Independent prospective controls/interface revision v3

Reviewer `/root/kelvin_scientific_review`,2026-11-02. This review preceded v3 compiled results. It permits qualification of a corrective proposal and does not assume success.

Independently verified all current interface-v3 and prior-file hashes. Prior/ reproduces every interface-v2 frozen file exactly. Read the production delta and new tests. The redundant strain/state comparison now admits only64EPS·max(1,|a|,|b|), approximately1.42e-14 for the qualified strains, to accommodate observed independent accumulation roundoff. It is far smaller than the physical3e-8 gate;1e-9 corruption remains rejected. Saved-versus-fresh replay remains bit-exact and its test rejects even a one-ULP saved result change. The remaining contract delta changes solver controls only.

Independently reran pure contract/lifecycle tests against the actual isolated release app hook:13/13pass, saved in interface-v3-tests.log. No compiled artifact or actual browser was executed by this reviewer. The new roundoff consistency test and startup-failure regressions are meaningful contract checks; their synthetic responses are not numerical references.

Independently ran execution-v3/check_preparation.py, saving execution-v3-preparation-check.json, and read prepare_accuracy.py's exact source/case comparisons. All43physical cases, independent Cartesian/integrating-factor references, ABI calls, model identity, reference times, negative requests and assessor source/gates are preserved. Only prospective solver controls change: fine/public relative3e-11, absolute3e-14, work budget1000000; diagnostic coarse relative1e-5, absolute1e-8. Intentional budget2 cases remain2. Physical gates remain3e-8strain/1Pa, tighter direct/algebraic gates remain unchanged and coarse diagnostic remains3e-6strain. The original v1/v2 failures are not reclassified as passing.

The larger work allowance is based on explicitly approximate projection from retained v2 step counts, documented in budget-basis.json. It does not waive a future budget failure. Recollect all v3native/Wasm requests with the new controls; do not treat old trajectories as new-control evidence. Parent separately freezes unchanged160-file source closure plus Release toolchain flags before execution.

This proposal addresses the observed accuracy and redundant-output issues without changing constitutive physics, analytical oracle or acceptance bounds. No prospective blocker found. Native/Wasm numerical qualification, backend admission, package/browser and live-delivery checks remain outstanding.
