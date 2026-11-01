# Independent standard-builder and timed-route review

Separate reviewer `/root/review_power_creep`, implementation author `/root`,
2026-11-01. **Accepted the exact assigned proposed source variants; no blocking
finding.** This is source and bounded unit/saved-evidence review. Parent owns
the actual full builder, compiled analytical package, browser and release gates.
No build, compiled execution, shared edit, staging or commit was performed here.

## Exact scope and inspected delta

Reviewed the six source variants under proposed/ against their prior-source/
counterparts: tools/build_web.py, tools/test_web_package.mjs, web/app.js,
catalogue/manifest.json, tests/test_web_package.mjs and tests/test_web_recorded.py.
Also reviewed web/timed-route.mjs and tests/test_timed_route.mjs. All eight files
byte-match the parent's isolated committed-source checkout at
/private/tmp/power-creep-release-51a9ef72 when checked. checked-hashes.json binds
their exact SHA-256 identities. Broader pending shared builder/app changes and
subsequently added proposed source-archive maps were not substituted for these
assigned files.

The standard builder now unconditionally calls the existing approved power-creep
bundle and then the existing strict power package assessor. Dedicated engine
directory defaults consistently to the main --wasm-dir, with explicit override.
The earlier cleanup removes stale timed assets before exact approved assets are
installed; bundle or assessor failure prevents successful packaging. The hook
restores power-creep only and does not reinstate unrelated J2/SLS pages. Existing
definition/catalogue freshness checks and analytical budgets are unchanged.

The manifest adds only public_timed_laboratory:true for the already approved
power-creep entry, preserving false ordinary-runtime membership. The route helper
requires that explicit Boolean opt-in and accepts only a lowercase project-local
basename ending in .html; protocols, slash paths, query, fragment and encoded
traversal forms reject. Retired entries without opt-in remain unadvertised.
Catalogue cards/detail now mark the approved timed entry available and its Explore
action navigates to the safe relative route. Ordinary model actions still select
the strain-path laboratory; the timed model is not silently passed to that engine.

Mandatory validatePackage now rejects a declared missing/unsafe timed page and
missing route module. tools/test_supported_package.mjs invokes this validator,
so the actual supported-package gate enforces the new presence rule rather than
only testing the fixture. Generic presence checks are supplemented by the
builder's exact power package hashes/analytical gate. Presence alone is not
claimed to prove an arbitrary timed laboratory scientifically correct.

## Reproducible checks

Ran only bounded source/unit/saved-evidence checks in the isolated checkout:

```sh
node --test tests/test_web_package.mjs tests/test_timed_route.mjs
python3 -B -m unittest discover -s tests -p test_web_recorded.py -v
```

node-tests.log records11/11 passes, including missing timed page/module and unsafe
route rejection. python-tests.log records4/4 passes, including saved recorded
parity/failure-prefix checks and the static standard-builder expectation. No
compiled package/runtime was loaded by these commands. The changed recorded
test now correctly requires the power hook while retaining explicit retirement
of unrelated standalone J2/SLS hooks; no numerical assertion was relaxed.

An initial byte-comparison inventory traversed newly added proposed receipt maps
that were absent from the isolated checkout. That reviewer inventory attempt
failed before tests/product changes; corrected bounded comparison explicitly
selects the six assigned variants and two route files, as recorded in
checked-hashes.json. Parent must separately scope/stage archive-map updates and
retain the uploaded51a9 missing-route failure. Passing local source tests does
not erase that release failure or establish a successful new upload/live route.

The remaining exit condition is the parent's exact candidate standard full
builder and browser proof, followed by all terminal CI gates, actual uploaded
asset inspection, matching live assets and both live experiments. This accepted
review supplies no constitutive/model/solver/tolerance change or broader material
approval beyond the existing exact bounded model checklist.
