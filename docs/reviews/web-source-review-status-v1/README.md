# Catalogue source-review status — local delivery v1

1 November 2026. The existing catalogue evidence panel now includes the formal
source-review records from `catalogue/reviews/`, separately from numerical
outcomes. This advances BASE-02 and WEB-01/02/04; those larger tasks remain open.
No scientific decision, reviewer assignment or model status was changed.

## Delivered behavior

The exporter validates every review with the existing review contract and emits
its exact original JSON plus a compact projection: recorded status, independence,
attribution/date when recorded, unresolved questions, dossier/evidence references,
record hash and exact model-definition binding. All retained revisions appear;
there is no automatic latest-review selection, signature authentication or
promotion from a numerical pass. A matching definition means model JSON bytes,
not current engine/dossier/source completeness. Questions describe their record's
preparation time; newer records may document progress without erasing old ones.

The browser distinguishes missing review coverage from an indexed formulation
without a review. Existing indexes without the new optional reviews collection
remain readable and explicitly say reviews were not indexed. Pending, accepted
and changes-requested are review statuses, never numerical outcomes. Historical
acceptance is not presented as acceptance of changed current bytes. Questions
and attribution render as text. Original records are linked beneath the project's
relative path, with hashes and evidence references in a disclosure.

The actual package contains **14 reviews, all pending**: 10 bind current model
bytes and four bind historical definitions. They cover the five baseline models,
not all 32 discovery entries or nine browser-executable definitions. All 19
numerical/research entries are identical to the previous export, including failed
outcomes. This delivery adds no scientific admission or model coverage.

## Verification

```sh
python3 -B -m unittest tests.test_build_evidence tests.test_web_catalogue -v
python3 -B tools/build_web.py --wasm-dir /private/tmp/atlas-dp-web-v1/release --output /private/tmp/atlas-source-review-preview
```

All 21 Python tests pass; the browser wrapper executes 11 catalogue JavaScript
contracts plus existing state contracts and app syntax verification. New cases
exercise pending reviews alongside numerical passes, unchanged original bytes,
multiple revisions/historical acceptance, unsafe paths and unsigned acceptance
rejection. These synthetic identities are test fixtures, not actual signatures.

Full packaging succeeds with the already verified Wasm release, checking catalogue
freshness and including the existing 628 public experiment assets. Both engine
files are byte-identical to that release. All 14 exported review records match
their originals exactly; raw evidence reports, private KFS arrays and PDFs are
not added to the evidence export. Existing public experiment packaging is unchanged.

The first attempt used the stale default build directory and correctly stopped
before packaging. The explicit verified directory was then used; no rebuild was
performed. Two archive-map preparation attempts encountered heterogeneous JSON
and an absent optional sidecar; those attempts were stopped and no historical
receipt was rewritten. The two affected existing DP-web source bindings now
resolve their preserved exact bytes. A whole older DP-web prospective-freeze
check still fails at an unrelated pre-existing `tools/build_web.py` source
binding; this task does not claim to repair that older full-closure record.
The DP domain manifest still verifies.

Four original exporter/UI/test files were preserved before editing in canonical
source snapshots; [previous-sources.json](previous-sources.json) records them.
Only two applicable entries were appended to the existing DP-web archive map;
its original receipt hashes remain unchanged. Other matching historical records
refer to frozen copies or source-commit snapshots, not changed live paths.

An actual in-app browser inspected VW96's two pending records and DP's three
historical plus one current-definition pending records. The identity disclosure
opens with the recorded hashes and evidence IDs. The final explanatory copy was
reloaded and visually checked. Local preview:
`http://127.0.0.1:8947/constitutive-atlas/#catalogue/drucker-prager`.
Screenshot: `/private/tmp/atlas-web-source-review-status-v1/source-reviews.png`.
No hosted verification, deployment, new fit, native material call or build.

## Remaining work

Independent scientific judgments remain open. The separate
[KFS handoff](../../benchmarks/kfs-development-review-v1/README.md) is unsigned.
The live board owns subsequent delivery selection; do not extend the completed
KFS numerical campaign automatically. SANISAND's missing exact loading-process
source and Terra Cotta's journal/source-history gaps remain separate source tasks.
This panel does not resolve those gaps, complete formulation preparation evidence
or admit additional models.
