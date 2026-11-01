# Independent generic bridge static review

Task `REVIEW-controlled-path-browser-bridge-v1`; reviewer
`/root/norsand_path_review`, 2026-11-01. This is a new identity, with all earlier
review bytes preserved. The reviewer did not author the bridge or its checker.
No build or compiled call was performed by this reviewer.

All 18 files in `bridge-freeze-v1.json` match. The frozen module/Wasm, generated
metadata/equations/C ABI and six header closure retain the accepted compiled
capability identities. Reuse does not imply a new shared-target build or browser
execution. The bridge's numeric work is control interpolation and marshaling;
constitutive equations remain in the frozen generic compiled evaluator.

The bridge validates complete named state/parameters/controls, finite coordinates
and progress, output count and execution settings. It preserves full caller
context through cloning, creates all trial points locally and returns only after
the entire requested history succeeds. Each C ABI invocation checks input
preservation, failure sentinels, finite output and coordinate advancement.
Allocation cleanup is in `finally`, including allocation/update failures. Shape
compatibility is checked against metadata; exact model/artifact identity is
established by the outer file freeze, not by shape equality alone.

No blocking static implementation defect was identified. One prospective
transaction-evidence gap was reported before observations: the failure request
inherits `samples:1`, so it cannot demonstrate failure after accepted positive
output intervals in the JS history. Add a separately frozen 40-interval failure
request ending at inadmissible pressure, assert that the failing request itself
is unchanged, then demonstrate recovery. The current check only asserts the
separate original good request is unchanged. Existing compiled single-advance
rollback evidence does not replace this bridge history transaction check.

The source-reference comparisons in the prospective checker assess endpoints
of single- and 40-interval histories. The volume and shear-offset invariants are
checked at each retained point. These checks do not compare every intermediate
stress/strain point against independently tabulated source trajectories and must
not be described that way. Exact replay is an interface property, not an
independent source reference.

**Decision: static design accepted; numerical/history-transaction qualification
pending prospective test completion and actual saved results.** No main-atlas,
actual browser, E5 model approval or live delivery is granted by this record.
