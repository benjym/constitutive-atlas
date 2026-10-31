# Schema-focused Methods overview

The Methods page now leads with “A common language for constitutive models.”
It explains the structured model record, explicit physical conventions, generated
execution, verification and supported scope. An isotropic elasticity example
connects parameters, state, inputs and conventions to an analytical consequence.
TMD2 reproduction and base-VW96 initialization studies are distinct linked
examples at the end. Their pages and recorded outcomes are unchanged.

The content follows `docs/FORMULATION_CONTRACT.md`, schema v0.3 and
`docs/ARCHITECTURE.md`. It distinguishes new explicit contracts from legacy
records awaiting migration, and automatic validation from scientific review.
No model, schema, compiler or numerical implementation changed.

## Verification

51 existing Python tests pass across these focused suites:

```sh
python3 -B -m unittest tests.test_browser_numerics tests.test_web_catalogue tests.test_web_development tests.test_web_propagation
python3 -B -m unittest tests.test_build_evidence tests.test_evidence_archives tests.test_web_recorded tests.test_web_publications
python3 -B tools/build_web.py --wasm-dir /private/tmp/atlas-dp-web-v1/release --output /private/tmp/atlas-schema-methods-v1
```

Packaging completes with 628 public experiments. Packaged HTML/CSS match the
working source exactly; atlas.js/atlas.wasm match the existing engine bytes.
Methods local file targets exist. Actual browser review confirms the new page,
its desktop layout, the elasticity catalogue dialog and development evidence
navigation. The development page retains original FAIL and separately scoped
PASS outcomes. Browser error log is empty. Responsive single-column styles
are supplied; a mobile browser viewport was not separately inspected.

Preview: http://127.0.0.1:8957/#methods
Screenshot: `/private/tmp/atlas-schema-methods-v1-preview.jpg`.
The loopback preview is temporary; nothing was deployed.

## Historical evidence preservation

Original web/index.html, web/style.css and IMPLEMENTATION_PLAN.md bytes were
saved under their SHA-256 directories in catalogue/source-snapshots before edits.
The first historical manifest verification exposed a missing index.html archive
binding. The development-summary archive map now selects the original bytes;
its original map was itself archived before extending the propagation map.
The original propagation map was archived and a current-TMD7 sidecar added.
All three original website manifests verify without changing their pins.

Two ad hoc verification-script mistakes were corrected: a link parser included
an unrelated dynamic anchor without href, and the experiment count initially
looked for manifest.json instead of index.json. Neither was a website failure.
The initially sandbox-denied loopback server started after authorized escalation.
No compiled build, fit, numerical study, admission change, commit or deployment.
