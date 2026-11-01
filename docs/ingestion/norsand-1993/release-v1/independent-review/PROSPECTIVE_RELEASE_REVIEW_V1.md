# Prospective NorSand release review V1

Reviewer `/root/norsand_path_review`; task `REVIEW-norsand-release-v1`. Base revision `b529a0efc3415b2bc567178a68174575c220cadc`.

Accept the exact prospective additive workflow/deployment dependency and existing scientific identity. This is static acceptance only: no actual staging, remote CI, upload or live outcome is decided here.

All five prospective freeze bindings match. The exact definition remains `67ff78f8cd56fd8812ba42f4456105b6e7ae217090dbcf40d8f8d5f839995d2c` and canonical independent review remains `9cfe9b7d58632c5dbc3099fb6debe40a8fdcea47ae66b7077a5e60bf8bebf6b7`. Existing source/numerical/browser reviews are reused, not retranscribed or expanded.

Independent raw-source comparison against the base workflow finds native, wasm and wasm-linux jobs byte-identical. The deploy job changes only its needs list to additionally require controlled-path. The new job equals the previously statically accepted native-then-wasm job except for its dependency on the three existing jobs. It serially builds each explicit target with parallel 1, retains all outputs/binaries/generated metadata/cache, and applies the same frozen 58 requests and unchanged checker to native and Wasm. Three new shell blocks pass independent bash syntax checks. No continue-on-error or result-filtering escape was added. Actual terminal results remain mandatory before deployment acceptance.

The request, native runner, Wasm runner and result checker hashes match the earlier CI review. Current target CMake differs from that old pin: it includes the shared AtlasScalarFunctions contract, which links the portable pow/sin source library. This already belongs to the remote base, not the proposed release delta. Bind the current CMake/include explicitly and require the new CI to qualify its actual results; do not call the entire current executable identical to the earlier artifact or substitute retained public engine identity for a fresh CI pass.

The new per-item checklist preserves all 53 canonical checkbox texts exactly and explicitly leaves E8 observations pending. It distinguishes the approved active axial variant, complete original source, Atlas numerical choices, local browser evidence and publication. Two documentation corrections were sent to the coordinator: copied introductory links need rebasing from the new folder, and the current explicit user authorization can be marked fulfilled while all unobserved E8 actions remain pending. These do not weaken or block the proposed numerical/deployment gate.

The preservation receipt has 33 bindings; every referenced archived file independently matches its recorded original hash. It also retains 3953 preexisting unresolved inventory records. This review neither repairs nor waives them and does not claim a clean global inventory. Final post-edit receipt/source resolution and staged scope still require review.

No builds, material execution, source rereading campaign, browser actions, shared-checkout writes or remote actions were performed. An optional YAML parser was unavailable; raw job comparisons and bash syntax checks were used. A here-document command hit filesystem exhaustion; a direct Python invocation completed the read-only checks without deleting any artifacts.

Remaining acceptance: corrected/frozen checklist and installed workflow preservation, exact staged release scope, all required terminal remote CI results for the intended revision, actual upload identities and live project-path browser exercise. User publication authorization persists; this reviewer does not introduce another human approval requirement.
