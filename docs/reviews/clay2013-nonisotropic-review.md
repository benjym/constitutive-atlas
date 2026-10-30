> Archived AI technical review. Original temporary paths and code pins identify the reviewed snapshots; later fix sections supersede earlier findings. Current repository evidence is pinned in the corresponding investigation manifest. This is not human scientific admission.

# Clay2013 nonisotropic finite-path evidence review

31 October 2026. Read-only review of installed `tools/clay2013_nonisotropic_study.py`, `tools/clay2013_path_reference.py`, their tests, the independent Cartesian source-rate oracle and actual serial native evidence supplied by the parent. All computations here use Python; no builds, native/Wasm execution, repository edits or admission. This review relies on the already pinned author-manuscript/source dossier: SHA256 `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`, appendix Eqs43-58 for stress rate and p3 Eq7 for density. It does not reconcile that manuscript with the publisher version or add experimental evidence.

## Result

The actual four-case, three-tolerance native matrix provides useful zero-spin finite-path numerical evidence. Its raw36 calls and recomputed12 summaries match the retained report exactly. Model/catalogue/reference hashes match current inputs. Correct path chaining, source signs, Mandel conversion and independent RK4 refinement were found. The originally inspected comparator trusted supplied reference statistics/provenance. That evidence-validation blocker is now resolved by the installed strict replay gate, independently rechecked in the post-fix assessment below. No issue found requires changing the constitutive law.

## Reference and actual path semantics

`clay2013_path_reference.py:23-45` uses two physical paths (noncoaxial and shear reversal) plus their oblique rotations, one nonisotropic initial stress and one five-parameter set. Each of three full6 increments is held constant over caller coordinate0..1 and integrated by classical RK4 at8,16,32 equal steps. Every stage calls the independent Cartesian oracle with actual stress/e and actual Cartesian strain direction; each segment endpoint gets an additional domain/rate check. It imports neither the Atlas DSL nor common material integrator. The rate law remains shared source science, so agreement cannot detect a common transcription mistake in both independently coded forms. The direct determinant/source-invariant oracle also has its already documented near-isotropic limitations.

`clay2013_nonisotropic_study.py:44-69` correctly requests the next native segment from the preceding returned native state, while comparing each endpoint with the reference trajectory chained from the original exact initial state. This measures accumulated/global trajectory error rather than masking it with a fresh reference restart from each approximate native state. Requests, echoed settings/parameters/initial/strain, catalogue identity, finite7state, counters and increment coverage are checked. Source density evolution becomes `e_dot=-(1+e)trace(de)` under compression-positive signs. The independent volume relation is checked at every endpoint. Trace-free shear paths preserve e in these fixtures.

Rotating stress AND all strain increments is correct for material covariance at zero spin. A fixed spatial rotation is not finite physical spin. RK4 rotation checks and native rotated/reference comparisons are meaningful; they do not prove objectivity under a changing frame.

## RK4 refinement and reference uncertainty

Original16→32 stress differences range1.55e-6..4.10e-6Pa;8→16 to16→32 ratios are15.985..16.039. I independently extended every case to64 steps/segment.32→64 differences are9.66e-8..2.56e-7Pa, with ratios16.003..16.031. This supports the expected fourth-order asymptotic trend for these smooth regular paths. The64 Richardson estimates (difference/15) range6.44e-9..1.71e-8Pa. Scalar e differences are already roundoff-sized; its ratios should not be interpreted as observed temporal order.

The comparator's1e-5Pa working reference uncertainty allowance is conservative relative to these observed discretization changes, but is **not a rigorous upper error bound**, a general stress-domain guarantee or a bound on source-model/transcription error. `clay2013_path_reference.py:63` properly states that convergence estimates are not rigorous bounds. The comparator's opening phrase “converged Cartesian path reference” should be read or softened to “refinement-tested reference”: three/four grids give strong local numerical evidence, not a theorem of convergence across arbitrary paths. Zero spin and regular-state restrictions remain essential.

## Actual native results and tolerances

The supplied `native-study.json` contains12 trajectories/36 sequential updates. At initial mean pressure10666.6667Pa, endpoint stress acceptance limits are about213.33334,21.33334,2.13334Pa for requested rate tolerances1e-4,1e-6,1e-8. These are project global regression thresholds of2%,0.2%,0.02% of initial pressure, plus the reference allowance. They are much looser than the observed errors and are not equal to the local tolerance or a per-component relative accuracy guarantee. Absolute e limits are1e-6,1e-7,1e-8.

Observed maximum stress errors across the four cases range0.35197..0.70353Pa at loose tolerance,0.02378..0.03556Pa at medium tolerance and0.0009988..0.0014122Pa at tight tolerance. All cases improve strongly under refinement and remain well above reference discretization differences, so that conclusion is resolved for this matrix. Maximum noncoaxial e errors are4.63e-9,1.40e-10,7.60e-12; shear fixtures have zero measured e error. The working limits should be reported alongside actual errors; broad pass/fail limits alone are weak evidence against small systematic mistakes.

Native rotated-vs-rotated-base discrepancies reflect the component-max adaptive error controller, which is not rotationally invariant at finite tolerance. For noncoaxial paths the maximum discrepancy shrinks0.29306→0.0032375→0.0001730Pa. For shear reversal it is approximately1.82e-12→0.0022569→0.0000709Pa, so a blanket monotonic covariance-error statement would be false. Each native rotated trajectory does independently approach its rotated Cartesian reference. The Cartesian RK4 rotation residual stays at floating-point scale. Do not demand bitwise native covariance at every adaptive tolerance or infer a constitutive anisotropy from that controller artifact.

## Blocker: reference receipt/statistics are not validated

The inspected `clay2013_nonisotropic_study.py:17-29` checks case inputs, their hashes, grid labels and finite row shapes, then trusts the supplied refinement ratio and fine-difference summaries. It does not verify source/dependency receipts, grid0 initial state, basis, spin, rotation, resolutions or recomputed convergence/covariance. `audit.py` proves all five corrupted references still pass the full actual-native assessment:

1. Wrong source SHA256.
2. Wrong dependency receipts.
3. Altered coarse-grid initial row (stress1234567Pa).
4. NaN fine-difference summary (comparison with NaN does not reject it).
5. Finest endpoint altered by1e-4Pa while old convergence summaries remain, exceeding the declared1e-5 reference uncertainty allowance.

This is an evidence-verifier gap, not a failure of the genuine reference or native results. The actual genuine reference reproduces exactly here. Before committing the numerical milestone, close the gap with the staged `suggested_checked_cases.py` and five passing regression-test groups in `test_suggested_checked_cases.py`.

The suggested replacement checks literal pinned source and both reviewed implementation hashes against actual current files, then canonical finite JSON identity against a fresh `study()`. This recomputes every grid and initial row, all coarse/fine/ratio/Richardson statistics and covariance, and binds all metadata, exact inputs, basis, spin, rotation and resolution. Canonical serialization distinguishes bool/int/float identities where ordinary Python equality would not, and rejects nonfinite data. No native execution or new dependency is involved. Any approved implementation change requires updating the pins and regenerating/reviewing evidence.

Exact replay is explicitly a **local provenance mode**. Different Python/libm/platform rounding may change last bits; an old reference should then fail for regeneration/review rather than silently gain a comparison tolerance. If cross-platform archived-reference portability is later required, add a separately named numerical replay mode with independently justified component tolerances and complete provenance checks; do not blur it into exact identity. Fresh replay costs well under1second here. No cache is proposed, avoiding mutation of a shared reference object.

## Rollback, coverage and remaining gates

This nonisotropic matrix contains successful calls only. It proves request chaining and successful increments' normalized coverage, not domain-failure rollback, budget-failure rollback or persistent-instance contamination. Existing `test_clay2013_engine.py` includes isotropic partial-progress domain/budget failures and zero/invalid calls; those tests were read but not executed by this reviewer. Their results must remain separately attributed. Recommended next native regression: branch from one committed noncoaxial endpoint, force both domain and budget failures after partial progress, require exact returned-state rollback, then compare a valid continuation with an unfailed control in the same persistent Wasm instance. This can be added without changing the law.

The present paths are finite but modest, at a single mean pressure and parameter set; the four cases contain only two distinct physical loadings. Pressure/aspect-ratio/density/parameter sweeps, difficult near-isotropic/near-SPD-boundary precision, caller-partition tests on these nonisotropic paths, intermediate-state/domain margin retention and independent cross-backend replay remain useful gates. Reversal is a dissipative loading history, not an elastic-return expectation.

Scientific/public admission still requires publisher/manuscript reconciliation, independent human scientific review, source-matched preparation and calibration, accessible/licensed experimental comparisons with actual residuals, and declared physical applicability. An independently refined numerical implementation is not an independently validated material model.2014 anisotropy, changing spin and other extensions remain separate variants. Keep the public clay entry non-executable until its own admission gates are met.

## Reproduction and retained files

```sh
PYTHONPATH=/Users/bmar5496/code/constitutive-atlas PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/atlas-clay-path-review-20261031-v1/audit.py
PYTHONPATH=/private/tmp/atlas-clay-path-review-20261031-v1:/Users/bmar5496/code/constitutive-atlas PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s /private/tmp/atlas-clay-path-review-20261031-v1 -p test_suggested_checked_cases.py -v
```

`observations.json` binds genuine native report/raw/model and captures original corruption acceptance,64-grid refinement and native covariance observations. The installed five path-reference test groups and seven comparator test groups pass with Python only; the comparator's subprocess calls are mocked in the test that exercises raw retention. Five additional suggested-replacement test groups pass. No native/Wasm call or build was made. Review-manifest pins the reviewed files; later edits need a fresh assessment.

## Post-fix installed gate and retained Wasm reassessment

The installed comparator now invokes `replay_checked_cases` before the prior convergence gates. I inspected the actual source/dependency file-hash guards, exact finite canonical fresh replay and its placement, then reran the original five corruption probes against the full actual-native assessment. All five now reject. Installed12 comparator tests (old7 plus strict replay5) pass in this review with Python only. The strict gate binds fresh recomputed trajectories, source and current reviewed code, metadata and derived statistics as intended. No remaining reference-trust blocker identified for this bounded numerical evidence milestone. The local exact-replay portability caveat remains.

I also independently reassessed `/private/tmp/atlas-clay-nonisotropic-20261031-v1/wasm-study.json` using the installed strict comparator and a fresh pinned Cartesian reference. All12 trajectories/36 actually chained Wasm calls pass request/response/parent chaining, complete input coverage, identity and independent numerical error/refinement checks. Native report, current model/catalogue and reference bindings match. The Wasm report has no embedded summary field; `wasm-reassessment.json` retains the independently computed full summary instead of treating native summaries as Wasm evidence.

Recomputed maximum native/Wasm state discrepancy divided by max(1,abs(native),abs(Wasm)) is4.678527846318495e-16, consistent to rounding with the report's4.678527846318497e-16. Worst Wasm stress errors at loose/medium/tight tolerances are0.7035252,0.0355603,0.0014122Pa, matching the earlier native scales. This is retained JSON reassessment, not a fresh native/Wasm run; reported loader/binary receipts were not reconstructed or executed by this reviewer. Parent-owned manifest checks must continue to bind actual artifacts and engine/source inputs.

`post-fix-observations.json` preserves strict rejection of the originally accepted corruption cases; original `observations.json` remains historical evidence of the gap. `reassess_wasm.py` is a reusable JSON-only check and `wasm-reassessment.json` retains its results. Updated current-file pins and previous inspected pins are both in `review-manifest.json`. The original report sections describing a blocker should be read as pre-fix findings superseded here. Numerical/scientific/public-admission limitations above remain unchanged.
