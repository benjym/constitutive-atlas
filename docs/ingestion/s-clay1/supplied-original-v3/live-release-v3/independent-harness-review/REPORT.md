# Independent publication harness review

Accepted the exact proposed hashes in `review.json`, against HEAD `5d5f62dc4020238896dd6905627b1eae708bfabd`. No blocking findings.

All existing physical tolerances are unchanged (legacy 1e-7; current browser 1e-10; ensemble analytical stress .05 + 1e-7*|stress| and volume 1e-9 + 1e-7*|volume|).

Only pre-existing exact-definition-bound S-CLAY1 support exclusions alter success qualification. Every model/protocol still executes native and Wasm, compares full committed state/strain prefixes, and participates in unchanged cardinality. Browser checks retain full recursive physical result comparison and same-instance import replay even for out-of-scope prefixes.

Exact retained legacy rejection and OCC cyclic-failure checks run before public-support classification; their messages, points, initial state and parameters remain strict. All earlier supported model success checks remain strict.

Unsupported legacy parity additionally compares native/Wasm success and message, native status-to-result consistency, no error/signal/stderr; it does not assert source or numerical qualification of those controls.

Ensemble roundtrip cardinality now equals the actual exported study size instead of stale 15; queued/null assertions, linear-elastic completion and independent analytical checks remain unchanged. Historical three-model 15-job tests remain. Current full-catalogue 14 configurations/26 jobs includes explicit S-CLAY1 baseline assertion and full exact import equality.

Fetch-depth changes only fast checkout history depth to 2. ci_changes is unchanged: failed git diff returns None and main treats missing history as numerical=true; unknown/manual/new-branch events also require numerical checks. Numerical job and aggregate guards are unchanged.

Source support declarations, S-CLAY1 definition and accepted agent review, approval registry and profile-allocation logic are byte-identical to HEAD. New scope validator checks exact support-row definition SHA and existing schema/reasons against the loaded catalogue.

Pure verification: 18 Node scope/ensemble tests and 3 Python change-selection tests passed; logs retained beside this report. This review did not execute compiled artifacts, perform scientific re-review, or establish remote CI/live-delivery success.
