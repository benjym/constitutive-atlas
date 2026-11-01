# Power-creep delivery closure v2

Exact constitutive definition67f3fabd6aec remains unchanged. This closes the retrospective E6/E7 omissions without changing solver settings or scientific acceptance budgets. The independent nine-item review remains at review-v2; a separate delivery source review and its corrected follow-up are in review/. Live delivery is tracked separately in ../DELIVERY.md.

SQLite now keeps exact approved nested definitions, their original draft metadata, distinct approval/review JSON and sources. It does not add a timed law to the ordinary strain-path engine. Two export tests cover exact identity, repeat export and rejection of stale/path/ID mistakes.

The public timed interface has strict bounded import/re-execution, reset, complete six-component final stress/strain, current engine identities and explicit measurement unavailability. Three pure Node groups cover changed controls, rejection of altered identity/arbitrary ABI/loading/settings/duplicate or nonfinite JSON, and result shapes. The independent reviewer found a low stale failed-read status race; final generation guards resolve it, with four additional handler checks. Original review/reproducer remain unchanged. No constitutive implementation is present in the interface module.

Actual IAB browser observations on port8773: both default protocols run; changing duration/pressure/q/b1 succeeds; duration0 invalidates old plots/export, then correction recovers; reset restores defaults; altered Wasm identity import rejects; the actual downloaded changed two-second creep export imports and reruns, restoring complete state and plots. Subsequent control change clears response/export, and a new run/reset recovers. No captured console warnings/errors. Browser export replay separately compares all21 saved points exactly with the packaged common engine; independent constant-stress creep strain.001616 agrees within1e-10. Evidence screenshots/state/export/replay check are retained here. File-picker automation was very slow; timeouts and adapter reset did not supply a model pass.

Reproduction from repository root:

```sh
python3 -B -m unittest tests.test_approved_export tests.test_agent_review_archives tests.test_research_evidence tests.test_publications tests.test_agent_review_export
node --test tests/test_power_creep_contract.mjs
PYTHONPATH=. python3 -B docs/ingestion/power-creep-itasca900/delivery-v2/check.py
node tools/test_power_creep_package.mjs /path/to/built/site
node docs/ingestion/power-creep-itasca900/delivery-v2/check_browser_export.mjs /path/to/built/site
```

The standard tools/build_web.py full builder passes with matching current ordinary and dedicated power/SLS/J2 catalogues. The first attempted ordinary engine was stale and was correctly rejected (full-package.log); full-package-current.log records the matching build. No hand-edited generated catalogue or new compiled numerical campaign was used. Original execution/refinement/history failures and policies remain intact.

Exact-byte source snapshots and additive receipt maps preserve old evidence. Mutable registry references use the identical immutable agent-review receipt context; an attempted broad registry map was retained and removed from active catalogue context. See retained-attempts.json. Current summaries keep timed/restricted versus ordinary-model counts distinct. Final CI, tested upload comparison and live browser proof must pass before E8 is marked complete.
