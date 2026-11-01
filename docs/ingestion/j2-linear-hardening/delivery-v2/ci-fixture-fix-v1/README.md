# Browser VM fixture dependency repair

Release f8252c16 failed required native jobs in run41295851838: both Python wrappers extracted real browser handlers without their new specialLaboratoryActive dependency. Both browser/package jobs passed; deployment was skipped. Exact original Linux/macOS logs and two fixture files are retained. This is a release-blocking test-harness failure, not a successful E8 observation.

The two fixtures now extract the actual helper, supply null inactive profiles and exercise early return for each active J2/timed profile. Every original behavioral assertion remains. No application, model, compiler, numerical reference or acceptance budget changes. Five focused wrapper/historical evidence tests pass; independent source-only fixture review accepts without blockers. An additional attempted evidence-module name did not exist; the corrected focused command uses actual tests.test_laboratory_scope_view_evidence and passes.

Prior test bytes are retained in before/ and content-addressed snapshots. Only required exact old fixture redirects are added to laboratory-scope-view and B17 source-manifest maps; no historical document or result is repinned. The earlier Pages artifact was downloaded but is not deployed and supplies no live claim. The new exact release must pass every required job and live/upload/browser gate.

Reproduce: python3 -B -m unittest tests.test_laboratory_view tests.test_web_effective_scope tests.test_laboratory_scope_view_evidence
