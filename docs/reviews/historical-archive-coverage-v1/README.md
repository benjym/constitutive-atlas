# Historical archive coverage repair

1 November 2026. FIX-historical-archive-coverage-v1 closes the 15 remaining
archive-coverage failures: 13 missing live document bindings and two historical
source-tree namespace mismatches. All 14 archive tests now pass, including
three new corruption/namespace test groups. All 45 tests in the focused
archive/evidence/source-selection/export regression run pass. No constitutive
model, numerical reference, acceptance budget or scientific status changed.

## Repair and preserved identities

[Plan](plan.json) records the exact pre-change HEAD, document/map hashes and
reverse-reference closure. The initial narrower plan is retained separately.
The baseline [test log](before-tests.log) reproduces the 15 failures under
11 original test methods before any edit. [Repair](repair.json) records the
resulting map hashes and newly created archive files.

- Added missing document pins for all 13 active receipts across eight original map locations.
- Archived the exact previous bytes of every changed existing map. Existing document pins and mapping entries remain unchanged; updates only append pins/entries.
- The test file itself was pinned by four existing receipts. Its exact original bytes were archived first and all four bindings redirected to those bytes. Extending their map coverage brings the total to 12 touched map locations and 26 covered documents, including existing pins and reverse-reference documents.
- All 57 affected reverse references remain resolvable at their original hashes: six through checked_receipt and 51 descriptive map-entry references through canonical archived bytes. No formerly unresolved source was reinterpreted as resolved.
- Every original receipt document is byte-identical. Frozen source trees received no writes. Twelve exact prior map/test files were newly copied to canonical source-snapshots locations; no binaries or third-party materials were added.

The two namespace failures refer to the map and sibling JSON inside the
clay2005-homogeneous-rates-v1 frozen-sources tree. That map uses its original
docs/ingestion/... names, not the outer copied-tree prefix. Rewriting those
bytes to satisfy a newer live-root coverage rule would corrupt the frozen
packet. The coverage test now verifies the enclosing manifest's entire copied
subtree inventory and hashes, then verifies the map's declared original
source-root document pins. The historical sibling manifest remains covered by
the enclosing immutable inventory; no retroactive document pin is inserted.

Canonical content-addressed map copies are also checked against the digest in
their archive namespace. Active maps retain the original requirement that every
sibling file manifest has its explicit exact-byte document binding. Corruption
tests reject changed/missing owner-pinned files, extra snapshot files, rebased
historical document names and modified content-addressed copies. Existing
missing/corrupt archive, changed receipt, duplicate binding and path-escape
checks remain in place. No test was deleted or numerical gate weakened.

## Reproduction and scope

```sh
python3 -B docs/reviews/historical-archive-coverage-v1/verify.py
python3 -B -m unittest tests.test_evidence_archives tests.test_evidence tests.test_evidence_sources tests.test_build_evidence tests.test_tensor_source_archive tests.test_dsl_source_archives -v
```

The first command checks preserved bytes, map extension semantics and the
original affected receipt bindings without executing a material backend. The
second reproduces the 45 focused checks; original logs are retained in
regressions.log. plan.py and apply.py record the one-shot coordinator operation
with its original local paths; they are historical operation records, not
supported commands to rerun over this checkout.

This closes archive **coverage**, not every source-availability or numerical
claim. The separate seven legacy source-binding gaps, including the unavailable
compiler identity, remain tracked by EVID-legacy-source-binding-gaps-v1.
No new source bytes were invented or substituted for missing hashes. No full
project test/build or scientific-admission claim is made. No native/Wasm build,
solver call, deployment or push occurred. Unrelated paper work was untouched.
