# Exact Maxwell CI assets — v1

The standard builder requires the independently qualified timed Maxwell engine.
The new provisioner restores only three regular allowlisted engine/catalogue files
from the exact retained compiled closure, plus exact qualification/review receipts.
It never extracts archive paths, runs a compiler or creates a review decision.

Archive, selected member, qualification and actual reviewer hashes are fixed.
The existing bundle guard then verifies current runtime source, generated catalogue,
registered approval, reviewed interface and all five qualification gates before a
new destination is installed. Existing output directories are refused.

Run `python3 -B tools/provision_maxwell_assets.py` before the standard web builder.
Default output: `build-maxwell-wasm`. Source drift intentionally fails, requiring
a new actual qualification rather than silently reusing an old engine.

Five focused tests cover selection without extraction, archive/member corruption,
duplicate/link rejection preservation of existing destinations and cleanup after a rejected bundle guard.
[Actual checks](checks.json) include a real restoration and existing bundle guard.
No compiled program was executed. Two CI pre-builder test/restore hooks are implemented in the exact [workflow projection](workflow.patch), with prior bytes and receipt bindings retained. Separate review pending;
this is not evidence that CI or deployment passes.

[Five-test followup](checks-v2.json) adds actual guard-failure cleanup coverage requested by the reviewer. Original four-test checks and bindings remain immutable; the former test source resolves through the source archive map. No failed gate was weakened.
