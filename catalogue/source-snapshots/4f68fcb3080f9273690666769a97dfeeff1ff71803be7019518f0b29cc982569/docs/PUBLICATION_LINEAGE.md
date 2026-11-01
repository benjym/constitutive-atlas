# Publication identity and lineage

The [canonical graph](../catalogue/publications.json) currently contains seventeen publication records and eight sourced relations, spanning hypoplasticity, Terra Cotta and selected classic soil models. The [bounded Mašín source-identity addition](ingestion/masin-publication-bindings-v1/README.md) adds the 2005, 2013 and 2014 clay publications with two existing formulation bindings; it adds no inferred lineage edges. It keeps publications distinct from formulations: a preprint, journal version, correction or validation paper does not automatically add an executable model. The von Wolffersdorff source and Terra Cotta journal source are bound to their respective formulation entries; the latter remains a candidate in the public catalogue. Publication coverage does not change executable or reviewed model counts.

The [schema](../schemas/publications.schema.json) defines DOI identities, authors, publication date parts, version roles, formulation bindings, evidence locators and unresolved questions. All records are provisional and require independent review. The graph is a seed, not a complete bibliography or equation-level source audit.

Relations point **from the referring/newer publication to its source or related publication**:

| Relation | Meaning | Does not establish |
| --- | --- | --- |
| `is-preprint-of` | Metadata identifies a corresponding journal publication | Identical equations, dates or corrections |
| `corrects` | A correction explicitly targets another publication | A new constitutive formulation |
| `builds-on` | The source identifies an earlier formulation/framework | Unchanged state, parameters or numerical algorithm |
| `discusses` | A publication discusses another model/paper | Direct ancestry or equation identity |

## Source findings

The [2017 correction](https://link.springer.com/article/10.1007/s11440-017-0605-6) fixes the placement of sigma in the final term of Equation 6 of the [sand paper](https://link.springer.com/article/10.1007/s11440-017-0550-4). Read both before transcription. The sand paper's Section 2 discusses Wu–Bauer 1994 and von Wolffersdorff 1996; these discussion links are recorded without treating either as an interchangeable implementation.

The [clay theory paper](https://link.springer.com/article/10.1007/s11440-020-01000-z), Section 3, uses the 2017 sand core as its starting point. Its online publication is in 2020, with a 2021 issue. The [validation paper](https://link.springer.com/article/10.1007/s11440-020-01105-5), Introduction and Section 2.2, describes changes for clay calibration and strength. Retain both sources when selecting an exact variant; the title alone cannot establish a new formulation or unchanged equations.

Crossref metadata links the validation [preprint](https://doi.org/10.31224/osf.io/69pgk) and theory [preprint](https://doi.org/10.31224/osf.io/kxsnv) to their respective journal records. Preserve these distinct DOI identities. Their full texts have not been compared. Exact metadata responses are pinned in the [source audit](../catalogue/source-audits/hypoplastic-publications-2026-10-31.json) and [earlier search probe](../catalogue/discovery/crossref-hypoplastic-probe-2026-10-31.json).

The [cohesive-powder publisher abstract](https://www.sciencedirect.com/science/article/abs/pii/003259109502999I) describes an intrinsic-pressure extension of a sand law. The full source and exact parent identity remain unresolved; no ancestry edge or model binding is inferred from the abstract. The original Wu–Bauer 1994 PDF has since been received and its selected equations visually inspected; the [source dossier](models/wu-bauer-1994-original.md) records unresolved printed sign and calibration conflicts. Its typed source-algebra fragment is not a public executable model. The earlier [screening ledger](../catalogue/screening.jsonl) preserves its first-pass decisions; these follow-up publication identities do not certify source-complete admission.

## Terra Cotta source identities

The [bounded primary-metadata packet](ingestion/terracotta-2024/publication-records-v1/README.md) preserves unmodified journal/preprint Crossref responses and the publisher API metadata. The journal publication links to `terracotta-2024`; the preprint remains a distinct, unbound identity. Both Crossref relation objects are empty, so no formal preprint edge is asserted. Publisher metadata declares CC BY 4.0 for the journal article. This does not license external measurements or establish equation-image reconciliation; the full journal PDF remains unavailable.

## Database and verification

The existing SQLite export includes `publications`, `publication_relations` and `publication_models`, plus the [screening ledger and occurrence evidence](LITERATURE_SCREENING.md#verification). The DOI union is computed by the exporter from the screening ledger and canonical graph; the canonical graph currently has seventeen nodes. DOI hyperlinks and full canonical records, including source locators, remain in the database. For shared identities, `publications.record_json` retains the graph node and `publication_screening.record_json` separately retains the original decision. Formulation bindings reference `models`; relation endpoints reference `publications`. Foreign keys are enabled during export. Re-export replaces the records without accumulating duplicate edges, bindings or screening occurrences. The graph is exposed by the standalone `web/publications.html` evidence browser. The standard Pages packaging includes its validated canonical records; deployment verification is pending.

`atlas.research.load_publications()` checks schema structure, normalized DOI identity, unique publications/relations, known formulation bindings, distinct relation endpoints and local evidence checksums. These checks protect representation and provenance; they do not independently verify scientific claims. Relations keep their evidence and pending review status in the export.

Run `python3 -m unittest discover -s tests -p test_publications.py` for offline graph, source-pointer and SQLite checks. No compilation or third-party model execution is needed. Next, extract original equations and reconcile corrections/versions before adding candidates; extend the graph across the remaining charter families and existing model sources. LIT-01 and LIT-02 remain open.

## Browser review

The publication page loads no solver or Wasm. It provides title/author/DOI/year search, journal/preprint/correction filters, direct formulation bindings, correction notices, evidence disclosures and stable publication anchors. Filter state is shareable in URL parameters; relation links reveal their target outside the current filters. Formulation filtering shows direct source bindings, not every discussed paper as an assumed model source. The catalogue and laboratory source panels link only formulations bound by the canonical graph.

For static review without a solver build, run `python3 tools/build_publications.py --output /private/tmp/atlas-publication-preview`, then serve that directory with a loopback HTTP server and open `publications.html`. This copies only the page, JavaScript, stylesheet, canonical graph, model names and schema. It does not update the full laboratory distribution. `tests/test_web_publications.py` checks deterministic copying, canonical provenance and relative assets beneath a project path. Browser checks on 2026-10-31 cover author search, preprint and formulation filtering, empty results, and following a relation to the sand paper with its correction notice. The same checks also exercised shared search parameters beneath `/constitutive-atlas/`; a 390-pixel viewport had no horizontal document overflow, and the layout was visually inspected before resetting the viewport. Full laboratory integration, deployment and independent scientific review remain open.
