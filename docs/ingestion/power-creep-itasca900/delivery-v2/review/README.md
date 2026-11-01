# Independent E6/E7 integration review

Task REVIEW-power-creep-delivery-v2. Reviewer `/root/review_power_creep`, separate
from implementation author `/root`, on 2026-11-01. This review changes no shared
source, registry, model or solver. Exact checked bytes and external dependencies
are in checked-hashes.json.

## Findings and disposition

**Accepted for the inspected E6/E7 source changes and bounded pure-interface
checks, with one low nonblocking UI concern.** Actual browser/compiled-package
qualification and E8 live delivery remain the parent's responsibility. This is
not an assertion that those remaining delivery gates have passed.

**P3 — stale failed import can overwrite newer status.** In
web/power-creep.html lines104–108, the successful `file.text()` continuation checks
its generation token; the catch/finally do not. A file-read rejection after a
new controls/reset action can display the older import error. The actual inline
handler was reproduced with a DOM stub and a rejected file-read promise in
check_latest_import.mjs; latest-import.json retains the result. No engine was
loaded. This changes status text only: controls, current result/export clearing
and constitutive state remain protected. Smallest correction: apply the same
generation guard to import catch/finally, preserving original evidence and
refreezing changed interface bytes before affected UI qualification. This low
finding does not block the exact constitutive approval or SQLite integration.

No other actionable blocking defect was found in the assigned changes.

## E6 export assessment

approved_definitions validates approved definition paths inside models/, exact
hashes and IDs; duplicate approval IDs and conflicting definitions reject.
export_database merges approved nested records with ordinary definitions,
preserves embedded historical status and exact definition JSON, and records
approvals separately without promoting ordinary runtime membership. Nested
definitions absent from the discovery manifest get explicit model rows; sources
come from the definition. Agent-review rows bind accepted model IDs/hashes and
review bytes, while existing publication/lineage/screening rows are retained.
Foreign-key order and repeated export are exercised by the test. The exporter
treats the approval registry as its trusted admission input; it is not a new
independent scientific checklist validator.

The two export tests pass: ordinary database retains exact nested definition,
sources and accepted review, ordinary executable count stays unchanged, repeat
export succeeds; stale definition hash, unknown model ID and path escape reject.
The test's second name mentions conflicting approval but its fixtures cover
these three rejection conditions; the additional conflict branch was inspected
in source rather than claimed as independently exercised by that test.

## E7 contract and UI assessment

The contract fixes the exposed ABI to atlas_run_schedule, exact model/module/
Wasm/catalogue identity, zero initial strain/rate/time, two constant hold modes
and qualified solver settings. It rebuilds requests from bounded UI controls;
imported results are not trusted for plotting. Wire components are compared with
a small finite serialization tolerance; import is a canonical control replay,
not acceptance of arbitrary mixed-control or six-component initial stress.
Duplicate keys and nonfinite/unsafe numeric JSON are rejected by the existing
strict recorded parser. Parameter and signed axisymmetric q conversion matches
the source-reviewed interface. The three pure Node contract tests pass for both
modes, changed parameters, strict rejection, shape checks and identity failures.

The UI clears displayed results and export eligibility on edits, invalid input,
new run and import. Generation tokens cancel queued obsolete solves and successful
obsolete file reads. Reset restores declared defaults and reruns; import restores
validated controls and reruns. Engine work is synchronous after its queued timer;
there is no worker-result race during that call. Full final six-component stress
and strain are displayed with Mandel basis/units; the explanation accurately
declines unmatched measurement overlays. The low failed-read status race above
is narrower than the protected result path. Real browser interactions are not
substituted by these source/DOM-stub checks.

The package builder checks the exact explicit-user approval and historical
supporting files, candidate catalogue freshness and accepted nine-item review,
and emits a manifest covering page/contract/import dependencies, approval/review
and engine assets. The analytical package assessor checks asset hashes, replay
request identity, all replay points, and unchanged default endpoint budgets.
Its compiled execution was inspected but not run by this reviewer. No full
machine-range success, browser deployment or experimental validation is inferred.

## Archival and dependencies

All eight interface-freeze file hashes matched at review. All52 prior exact-byte
snapshots recorded in archive-result.json matched their content-addressed copies,
including prior research.py and old page/package source. Source-archive sidecars
preserve access to older pinned context instead of silently repinning historical
documents. Original failed archive/fixture attempts remain in retained-attempts.json.

The accepted model checklist validates with the current sidecar-aware
atlas/agent_review.py at SHA-256
f699f30bdedaaac8a888e09da3af10472fbc5627cea37fc2f3a269c83e6859af.
That modified shared checker belongs to another conversation; it is an exact
recorded external dependency, not implemented or separately approved here.
Its archive resolution was exercised by validation. Parent must include its
properly qualified dependency when preparing the actual release. The exact
model remains unchanged at67f3fabd6aecfda19b977bf3baeae2dce45f9081fa81a4436a750a41825a4bef.

## Reproducible checks and retained reviewer attempt

From repository root:

```sh
python3 -B -m unittest discover -s tests -p test_approved_export.py -v
node --test tests/test_power_creep_contract.mjs
node docs/ingestion/power-creep-itasca900/delivery-v2/review/check_latest_import.mjs
```

python-tests.log records2/2 passes; node-tests.log records3/3 passes. The DOM-stub
script reproduces the low finding, rather than being a passing lifecycle gate.
An initial parallel log invocation failed to open node-tests.log because mkdir
in the independent Python invocation had not completed. Rerunning after directory
creation succeeded; no product code changed. No builds or compiled executions
were performed. Parent's actual browser/default/package/live evidence must be
bound separately before declaring the complete delivery finished.
