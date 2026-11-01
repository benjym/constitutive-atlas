# Independent agent review visibility in the model catalogue

The normal evidence exporter now indexes actual `agent-model-review` records separately from legacy source reviews and numerical outcomes. The catalogue displays recorded reviewer/run/date, scope, limitations, blocking findings, all nine checklist decisions and exact record/definition hashes. A matching explicit registry entry is identified as a project approval for those bytes and that scope; acceptance alone does not manufacture a registry approval.

An archived historical model can remain visibly accepted for its retained bytes, while the changed current definition is explicitly excluded from that approval. Original review, retained reviewed definition and registry JSON are downloadable. Raw evidence artifacts, private source code/PDFs and binaries are never copied by this exporter. Records with no exact canonical model-ID binding are listed in coverage omissions; no family/variant mapping is guessed.

`atlas/review_export.py` resolves explicitly hash-bound historical artifacts and constructs an isolated exact-byte validation context. It reuses the full existing semantic review/approval validators; the current-model requirement of the actual approval API is unchanged. This is read-only integrity validation, not a scientific rerun, reviewer authentication or qualification of current binaries. Forged/duplicated registry approvals, incomplete/self reviews, changed unarchived inputs, corrupt archives and escaping paths fail before destination writes. Original failed numerical records and all legacy review revisions remain exported unchanged.

## Checks and actual browser observation

- [Python log](python-tests.log):37 focused integrity/export/approval tests pass, including20 existing exporter cases.
- [Browser contract log](browser-contract-tests.log):16 safe rendering/navigation/history cases pass, including11 existing catalogue cases.
- [Normal export](export-summary.json):22 numerical records,21 legacy source reviews and four current accepted agent records at observation. J2's distinct formulation ID has no canonical catalogue binding and is explicitly omitted. This is a bounded snapshot, not a promise that model counts cannot change.
- [Actual IAB observations](browser-observations.json):elastic and DP details show accepted status, registered scope and preserved historical pending records; DP's83-request restriction and Debug-Wasm limitation are visible. Layout was visually inspected.
- [HTTP checks](http-links.json):both original review and exact definition downloads plus exported registry are byte-exact.
- [Preview inputs](preview-inputs.json):existing frozen12-model page/engine reused with the new view/evidence files. This is a local feature check, not current full-package E7 qualification, a new backend campaign or live deployment. No builds occurred.
- [Isolated source check](isolated-head-tests.log):the same53 checks pass with committed HEAD dependencies plus only this task's owned files; concurrent uncommitted validator/research edits are not required.
- [Archive plan](archive-plan.json)/[result](archive-result.json):two original source files and seven prior map states retained; nine standard receipt edges preserved before edits. Historical expected hashes were not changed.

Reproduce focused checks from the repository root:

```sh
python3 -B -m unittest tests.test_agent_review_export tests.test_build_evidence tests.test_agent_review
node --test tests/test_agent_review_browser.mjs tests/test_catalogue_browser.mjs
python3 -B tools/build_evidence.py /private/tmp/atlas-review-export-reproduce
PYTHONPATH=. python3 -B docs/reviews/agent-review-catalogue-v1/verify.py
```

The last checker verifies exact retained feature/evidence bytes and archival bindings; it does not rerun the scientific checks or browser. Model delivery ledgers remain open for schema migration, current qualification/database identity and verified live delivery.
