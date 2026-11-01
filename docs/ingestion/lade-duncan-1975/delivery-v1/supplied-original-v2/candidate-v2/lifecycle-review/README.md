# Independent lifecycle review — candidate v2

Task: `REVIEW-lade-duncan-lifecycle-v2`. Scope: retained candidate-v2 source/model, Python interpretation and native evidence review only. No compiled execution, shared edits, revised acceptance or E5 approval. Exact reviewed inputs and outputs are bound by `review-receipt.json`.

**Verdict: the original 32-check lifecycle study remains FAIL (4 failures).** Two failures are an independently reproduced covariance-oracle defect. The loose rollback and dependent recovery expectations used a finite increment that the declared interface does not classify as invalid. Separately, the retained successful loose response demonstrates that endpoint positivity does not enforce the continuous source law's positive-pressure path boundary. Full-law admission remains blocked pending prospective domain-event qualification; neither correcting the oracle nor Wasm agreement resolves that issue.

## Source and candidate contract

The supplied original 1975 paper is available and previously independently inspected on all 17 rendered pages. This review does not reopen source acquisition. The model is the explicitly declared local Eq19 endpoint backward-Euler realization, current minimum principal pressure, fixed-frame small-strain, uncoupled zero-pore mechanical total-stress embedding. Its existing lazy spectral branches implement the disclosed cluster-average generalized derivative; a missing minimum primitive is not the present issue.

Candidate `e1a21278ac9ce65debd5bf81b181462509e57d7928cc8b8366c75cd6110c4e63` stores signed carrier q, decodes H=max(ft,f+max(q,0)), and retains q exactly for zero mechanical increment. At an exact nonzero-increment solution q=max(Hprev-f,0), hence H=max(Hprev,f). This is a disclosed representation of source maximum history, including noncanonical signed aliases, rather than postcommit projection. The retained loose tiny-pressure state passes current domain/preparation and returns an exact zero-hold residual in Python. The earlier v1 history reentry failure is not reproduced here. Finite precision and bounded qualification remain distinct from that exact algebra.

## Adjudication of the four retained failures

The covariance helper in `check_native_lifecycle.py` used Mandel shear components directly in a Cartesian determinant. Correct conversion divides each shear by sqrt(2). Independent 3x3 Q*S*Q^T multiplication and determinant reconstruction give physical-H rotation differences 7.105427357601002e-15 for both Table1 sets, within the original 1e-7 bound. Stress covariance errors are at most 1.52e-16 relative to 60000 Pa and work error is zero. These diagnose two checker defects. They do not change the failed historical result; a corrected checker/study needs a distinct identity with the same bounds.

The finite request de=(-2,-2,-2,0,0,0) has no declared amplitude-invalid predicate. The dense response fails and rolls back exactly; the loose response succeeds after 64 accepted substeps and ends at positive pressure about 5.7145e-11 Pa. Accordingly, the loose response is not evidence that an update which reported failure changed its parent. Its recovery comparison starts from a successful changed state, so equality with a direct request from the original state lacks the asserted premise. A 200 percent extension also has no demonstrated infinitesimal-regime accuracy. These two expectations cannot establish rollback defects, but changing their expected outcome to success would conceal the separate source-domain problem below.

## Independent source-domain witness and severity

For either Table1 set, nu=0 and a hydrostatic unloading path remains f=27, below ft, with no plastic work. Set u=p/pa and let epsilon be the signed per-axis strain. Source Eq2 and elastic compliance give

    du/d(epsilon) = Kur*u^n
    u^(1-n) = u0^(1-n) + (1-n)*Kur*epsilon.

For p0=60000 Pa, positive pressure reaches zero at epsilon=-0.001957623166951442 (dense) and -0.0041485165880758195 (loose). The source's strictly positive-pressure path cannot extend to -2. Thus the source-domain concern already arises at much smaller strains than the extreme test, and cannot be dismissed solely by its amplitude.

Endpoint backward Euler instead solves u_new+L*Kur*u_new^n=u_old for unloading length L>0. For 0<n<1 it has a unique positive root for every finite L. Checking only endpoint positive pressure therefore cannot detect crossing the continuous path's zero-pressure boundary. The first accepted loose subincrement is already -0.015625 per axis, beyond the continuous boundary. Its exact scalar BE root is about 1272.8173 Pa. This is a discretization/path-event issue, not proof that the native algebraic solver failed its own declared residual criterion.

Pure Python log-domain replay of the retained accepted partition produces an exact scalar BE final log10 pressure in Pa near -90685, versus native -10.243. The final native modulus is about 1.2472e-5 Pa, while its absolute stress residual scale is 2.0265e-5 Pa. This diagnostic exposes extreme dynamic range and the practical limit of the absolute residual criterion. It is not a compiled replay or an acceptance oracle for each native substep, and does not retroactively add a pressure-relative tolerance.

Severity is blocking for claiming the differential pre-failure law throughout its declared positive-pressure domain: the current evidence admits a completed path beyond a finite source-domain event. It is not a source-transcription failure, a missing spectral primitive, an established failed-update rollback bug, or evidence that all numerical realizations are impossible. The successful 24/24 triaxial requests, eight converged source references and bounded hold/restart checks remain useful evidence within their tested ranges.

## Smallest next task and prospective acceptance

Freeze an independently sourced hydrostatic unloading/domain-event study before new observations. Use both Table1 sets, nu=0, p0=60000 Pa and at least one scaled initial pressure. Include endpoints strictly inside the analytic positive branch, sequences approaching the analytic zero event, and requests crossing it by a small margin; use the closed-form pressure and exact critical strain above as independent references. Prespecify absolute/relative error floors, a refinement sequence, event-bracket tolerance, returned-state semantics and failure/rollback policy. Ordinary interior accuracy must converge under refinement; a crossing request must not silently report the full source path completed with a small positive endpoint. It must either reject with exact rollback under a documented policy, or return an explicitly partial, located boundary status with the unconsumed increment. Reentry, retry and native/Wasm agreement must be checked under those same prospective rules. Do not add a fitted pressure cutoff, clipping, or change the old gate after failure.

A general path-aware stop/reject or event-location capability is needed to support that full-law claim; the existing endpoint domain/solution constraints and parent reset alone do not provide it. The schema and formulation contract explicitly say reset does not add event location. This does not yet prove that a shared engine edit is the only implementation: a source-faithful declarative transformation or independently qualified controller could supply the requirement under a new identity. First run the bounded analytic study to specify and expose the required behavior; then assign the smallest generic capability task if the current interface cannot express it. A hydrostatic-only guard is a diagnostic witness, not general 3D qualification. A knowingly restricted public model would be a separately reviewed scope decision, not completion of the assigned full target.

Separately freeze a corrected lifecycle study: fix Mandel conversion while retaining all covariance bounds, and test rollback with genuinely declared invalid parent/parameters/nonfinite loading and an exact unchanged-state/retry premise. Preserve the original 32-check FAIL. Corrected lifecycle and Wasm parity may progress independently, but cannot substitute for the domain-event gate.

## Reviewed followup studies

The subsequently frozen `hydro-domain-policy.json` makes the source-domain witness prospective. Independent formula/hash review of its 16 retained cases confirms that both sets complete every requested external step at 1.25 times the negative critical strain for all four partitions (1,4,16,64): eight source-domain fidelity failures. Before-event pressure errors at half the critical strain decrease monotonically with refinement; the study declares no retrospective tolerance pass. This removes dependence on the extreme -2 example. The next task is now a generic source-domain stopping/rejection design and implementation, followed by a newly frozen conformance/accuracy study, rather than merely collecting the initial hydrostatic witness. Required semantics are those above: interior accuracy, no silent complete crossing, explicit boundary/unconsumed-load or exact rollback, consistent backends. General 3D event adequacy still requires qualification; the scalar witness cannot define all events.

The distinct corrected lifecycle campaign retains the original covariance bounds and passes 38 recorded checks. Its corrected Mandel determinant agrees with this review's matrix oracle. Independent retained-response checks confirm forced iteration exhaustion returns the valid parent exactly, all three actual-invalid categories reject, and ordinary retry equals the direct full raw state. This is useful bounded lifecycle evidence and does not erase the old FAIL or establish source-domain stopping.

The 56-request Wasm parity study remains FAIL: exactly one record, original lifecycle request 20 (loose -2), has native success and Wasm failure, with scaled state difference about 0.592154. All 56 retained raw response hashes and the Wasm source snapshot hashes match. This is an actual unresolved backend status/state discrepancy. The unsupported original invalid-input label does not excuse backend disagreement, and neither backend's status alone establishes source conformance. After event semantics are fixed, repeat this exact retained regression plus the new boundary cases under a separately frozen backend policy; do not remove the mismatch from evidence.

## Reproduction and status

Run from repository root:

    python3 docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/candidate-v2/lifecycle-review/check_lifecycle.py

Also run:

    python3 docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/candidate-v2/lifecycle-review/check_followup.py

This uses Python algebra/interpreter and retained JSON only. It checks exact candidate/policy binding, all 27 native source-snapshot hashes, retained 32-check/4-failure status, covariance diagnostics, continuous hydrostatic boundary, log-domain scalar BE partition, exact zero reentry/hold, 24 retained triaxial successes and eight retained reference convergence checks. Outputs: `diagnostic-results.json` and `followup-results.json`. No new compiled acceptance run is claimed. Full delivery remains open: E4 qualification is incomplete; E5 approval and subsequent browser/live stages are not granted by this review.
