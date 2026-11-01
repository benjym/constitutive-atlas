# Qualification checker audit

Task `REVIEW-lade-domain-control-v1`, followup static audit of the five exact scripts bound in `checker-audit-receipt.json`. No script edits, compiled/material execution or qualification decision. The running campaign and its original report must remain unchanged; supplemental checks should have separate identities and bind the same retained raw responses wherever possible.

## What is correct

The domain script uses the correct hydrostatic critical strain and interior source pressure. Its proportional tensor has eigenvalues1.1,1,.9; the full3D Cartesian rotation and Mandel encoding are consistent. Its critical strain factor .9^(-n) correctly accounts for current least pressure .9*p. Independently extracted pure helpers preserve trace, f=300/11 and Mandel norm. Sixteen float source formula combinations agree with the independently generated 80-digit references within1e-13 relative error.

The triaxial script retains the original independent stress/radial-strain/work reference errors, finest-step bounds and nonincreasing plastic stress error. All required requests must succeed. The lifecycle script uses the corrected Mandel determinant, original covariance and history tolerances, exact full-state zero holds/restart, actual invalid inputs and the intentionally limited six-setting forced-failure budget. The legacy script replays all56 original v2 requests with old settings/default behavior and compares all material states and statuses exactly, including original failures. The Wasm script includes those retained cases and new native campaigns; statuses and point/state array lengths are required to match.

No erroneous source critical-strain formula or repeat of the old Mandel H oracle defect was found. That does not resolve the coverage gaps below.

## Material coverage gaps

1. **Tiny-pressure accuracy is underchecked.** Native half-critical tiny cases assert only0<p_final<p_initial. An almost unchanged endpoint can pass that predicate while grossly missing the source pressure. The explicit policy requires tiny success/reject and no successful stagnation, but does not assign a tiny source error bound. A separate frozen supplemental study should use the same half-critical source curve and a declared relative pressure accuracy bound; the already fixed .005 ordinary half-critical bound is a natural prospective choice, not a claim that it was tested here. Use all stress components, not just Sxx. No observation is claimed by this audit.

2. **Completed prefix crossing is not tested.** The external crossing loops require some call to fail before the entire prescribed sequence completes, with exact rollback of that failed call. They do not reject an earlier successful caller step whose cumulative strain is already beyond the analytic source event. A later failure cannot roll back previous separately committed calls. Independently reconstruct successful cumulative supplied strain and require no completed source path crossing. Preserve the literal original eventual-failure gate as a distinct result.

3. **Recovery coverage is incomplete.** Policy says ordinary valid recovery equals direct after crossing failures. Native domain script performs this for tiny and extreme cases, but not each ordinary hydrostatic partition crossing or rotated proportional failure. Existing exact failed-parent checks remain useful. Supplement with valid recovery requests from each retained failed parent, using strain magnitudes appropriate to that parent's pressure rather than an arbitrary fixed amplitude near zero.

4. **Source-invariant checks are uneven.** Ordinary interior hydro cases check only Sxx reference and exactly zero work; tiny cases omit work/history, and proportional cases omit work/history. For all these constant-f elastic references, compare the full expected stress tensor, source physical H and unchanged wp. q need not be called a physical measurement; decode H consistently. Gross anisotropy/shear drift in a nominal hydrostatic response could escape a first-component source check.

5. **Static-scale Wasm parity is insufficient near zero.** The Wasm comparison divides every stress defect by101325Pa. Consequently an arbitrarily poor relative pressure response at1e-24Pa can satisfy1e-8 static parity. This matches a narrow static scaled-state gate but does not verify the new relative-domain behavior in Wasm. Independently apply the same source accuracy, invariants, crossing-prefix and transaction assertions to retained Wasm responses, and/or add a declared least-pressure-relative state comparison. A shared status does not imply that both backends follow the source.

6. **Wasm state type/finite checks are missing.** JavaScript arithmetic coerces null to zero. If an expected zero slot is returned as null, the current comparison can report zero error. Require each compared state/strain slot to be a finite number before arithmetic; shape means more than array length. This is a checker robustness defect, not evidence that the compiled engine actually emitted null.

## Bounded claims and provenance

The Wasm script compares material states but not laboratory strain arrays. Radial strain is one of the independent triaxial source-reference quantities, so a broader laboratory-response parity claim needs strain comparison or direct Wasm reference checks. The policy says full-state parity, so keep the original claim that narrow until supplemented.

Legacy replay supports exact v2 disabled-controller state/status compatibility; it does not run positive disabled-controller linear-elastic or rate-model regression cases. The added rate case tests opt-in rejection only. A broader generic legacy claim should include representative normal requests for those existing profiles. The separate16-check native metric result is bounded synthetic metric evidence; it does not supply these material regressions or prove all3D event handling.

Timeouts, invalid JSON and runner exceptions currently abort scripts before their aggregate report is written. They cannot create a passing report, and raw completed requests survive, but the coordinator must retain the failed process/log and explicitly mark the campaign incomplete/failed. Do not infer pass from an absent report or reuse a stale report from a previous invocation.

Some summaries omit top-level executable/model/global-policy/native-input-report digests. Final review receipts should bind exact scripts, executable/build manifests, current model/POLICY, reference and lifecycle policies, native input reports and all raw response hashes. Wasm parity should be bound to the exact native reports/raw bytes that were compared. This can be supplied as append-only review evidence without rewriting historical results.

## Disposition

No formula defect warrants discarding the running study. Its literal gates may be evaluated once complete, with these bounded claims. Full source/relative-domain/backend qualification remains open until the material omissions are addressed with preserved raw evidence and separately frozen supplemental checks where new execution or new acceptance criteria are needed. This audit is neither a post-observation gate relaxation nor E5 approval.
