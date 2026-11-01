# Catalogue consumer regression follow-up

Independent reviewer `/root/review_power_creep`, 2026-11-01. **Accepted; no
blocking finding in the prospective two-assertion test correction.** Exact
final-test.py SHA-256:
`5a5e7ba42ae1120c7314031763d3e6532a8ae62d7a9504a9e42826af5b0fcff6`.

Compared final-test.py directly with the archived prior-source/tests/test_catalogue.py.
The changes are the two documented consumer corrections and their imports:

1. SQLite exported model IDs must exactly equal manifest IDs union validated
   approved-definition IDs. This is stronger than the obsolete row count: it
   detects missing, extra or substituted IDs. Existing candidate/ordinary-engine
   membership, sources/citations and repeat-export idempotence assertions remain.
2. Supporting files still face their original SHA-256 and repository-containment
   checks. Only when an agent-review supporting file's live hash differs does
   resolution use checked_receipt with that review document, original path and
   unchanged expected hash. Exact live bytes need no archive context. The resolver
   requires the immutable receipt pair and sidecar pin and rejects wrong archives;
   this does not substitute new live hashes or accept arbitrary source content.

Existing corrupted definition/supporting hash negative tests are unchanged.
The prior checker/receipt focused tests cover corrupted/missing archives,
changed documents, ambiguous/escaping maps and current-model requirements.
No test gate was relaxed to claim numerical or constitutive success.

Ran only the exact archived prospective test file via runpy/unittest, rather than
the shared working tests/test_catalogue.py containing another worker's additions:
all3 tests pass in consumer-tests.log. Inspected clean-consumer.log (3passes)
and clean-focused.log (45passes); I did not rerun the45-test suite or the broad
repository suite. The original shared-checkout failures and first rejected
context attempt remain recorded in the parent's follow-up packet. Those broad
results are not represented as clean release qualification.

consumer-results.json binds the exact six packet files inspected. No production,
model, runtime, shared test, registry or board file was changed by this reviewer.
No compiled calls or builds. Parent should stage these exact prospective bytes
without accidentally including the other worker's material-lab additions.

Reproduce from repository root:

```sh
python3 -B - <<'PY'
import runpy, unittest
v = runpy.run_path('docs/ingestion/power-creep-itasca900/delivery-v2/catalogue-consumer-followup/final-test.py')
r = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(v['CatalogueTests']))
raise SystemExit(not r.wasSuccessful())
PY
```
