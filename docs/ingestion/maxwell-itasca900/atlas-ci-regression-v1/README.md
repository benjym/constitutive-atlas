# Required Maxwell CI regressions — v1

The new coordinator harness runs the existing public contract/lifecycle tests,
24 frozen source-reference cases twice, and all four actual public presets with
recomputed full-result replay against the exact independently qualified Wasm.

[Prospective review](independent-review/prospective-review.json) accepted corrected
sources before execution. Original findings/plan/source identities are retained.
[Actual process](execution.json) exited0 in6.804seconds:21Node tests,48frozen material
calls and8public preset/replay calls pass. No compilation, native binary call,
remote CI invocation or new scientific approval occurred.

[Raw observations](observations/) and [output hashes](output-manifest.json) retain
the exact commands, inputs, responses, actual full package identity and assessments.
Direct max error0.023885Pa remains under original0.05Pa; four preset max1.375203Pa
under original15Pa. Coarse138.380770Pa remains under its original1000Pa diagnostic
gate; fine1.360719Pa improves it. No tolerance/reference was changed.

[Workflow projection](workflow.patch) adds exactly one required harness invocation
to each existing packaging job after reviewed asset provisioning, before builder.
All other workflow bytes and prior receipt bindings are retained. The separately
recorded [own binding repair](own-binding-repair.json) fixes a missing sidecar docpin
for our earlier unchanged v2 receipt without replacing any expected hash.

Actual-results/workflow independent review is pending. Remote Linux/macOS CI,
newly rebuilt-engine qualification, remaining global ordinary regressions and
E8 release/live delivery remain unverified. The collector's original pair-write
boundary is retained; the new public driver saves each returned raw response
before parsing/validation.
