# Pending source-review coverage for all nine executable definitions

1 November 2026; task REVIEW-additional-executable-coverage-v1.

Four new pending records bind the existing clay2005, clay2013, barodesy sand and
barodesy clay2017 dossiers to their exact current model JSON bytes. There are now
18 retained review records, all pending, and each of the nine executable definitions
has at least one current-definition record. **Coverage of pending review work is
not completed scientific review.** No reviewer or maintainer has been assigned.

| Added record | Existing source and preview dossier |
| --- | --- |
| [Clay2005](../../../catalogue/reviews/hypoplastic-clay-2005-source-v1.json) | [Accepted-manuscript law, sign correction and current determinant/preview scope](../../models/clay2005-laboratory-preview.md) |
| [Clay2013](../../../catalogue/reviews/hypoplastic-clay-2013-source-v1.json) | [Appendix reconciliation, complete example and retained former default failure](../../models/clay2013-laboratory-preview.md) |
| [Barodesy sand](../../../catalogue/reviews/barodesy-sand-source-v1.json) | [2015 equation identity, separate 2019 fixtures and restricted continuation](../../models/barodesy2015-laboratory-preview.md) |
| [Barodesy clay2017](../../../catalogue/reviews/barodesy-clay-2017-source-v1.json) | [Body versus Appendix selection, zero-spin and preview/research distinctions](../../models/barodesy2017-laboratory-preview.md) |

This is an inventory of existing unresolved decisions, not a fresh equation audit.
The records carry `independent: false` and omit reviewer/reviewed_at. Their empty
`evidence_ids` explicitly avoid inventing a standalone numerical-evidence envelope
for the current preview hashes: the linked dossiers provide the separately scoped
studies, original failures and primary-source hyperlinks. Historical research
identity is not silently rebound to the public draft. The existing exporter indexes
these records verbatim; no source-review schema, model, solver or UI change is needed.

The [verification report](verification.json) checks all 18 records against the
existing review contract and all nine current-definition identities. It verifies
that the 14 prior records and 19 numerical/research export entries remain exactly
unchanged, and that the four new exported originals match their canonical bytes.
All 21 exporter/browser contract tests pass. The exporter checks retained evidence integrity without rerunning its scientific
checkers, binaries or simulations. These checks do not authenticate signatures or
supply scientific judgments. Broad source ranges, preparation, experimental
applicability and complete-update tangent claims remain unresolved as listed.

Reproduce the software checks without builds or material calls:

```sh
python3 -B -m unittest tests.test_build_evidence tests.test_web_catalogue -v
python3 -B tools/build_evidence.py /private/tmp/atlas-review-coverage-export
```

The catalogue source-review panel already consumes this index. Local export
verification establishes its data handoff; this task does not claim a new rendered
browser session, full website packaging, hosted verification or deployment.
[inputs.json](inputs.json) pins the reused model/dossier/prior-review evidence;
[previous-sources.json](previous-sources.json) preserves exact status/roadmap bytes
before their current counts were updated. Delivery history remains intact.
The [manifest](manifest.json) binds this packet and the four added records.
Independent scientific review is the next gate; software availability remains draft
for these four definitions.
