# Publication identity and lineage

The [canonical graph](../catalogue/publications.json) starts LIT-02 with nine hypoplasticity publication records and seven sourced relations. It keeps publications distinct from formulations: a preprint, journal version, correction or validation paper does not automatically add an executable model. Only the known von Wolffersdorff source is currently bound to an existing formulation. The model catalogue remains at 32 entries, five executable.

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

The [cohesive-powder publisher abstract](https://www.sciencedirect.com/science/article/abs/pii/003259109502999I) describes an intrinsic-pressure extension of a sand law. The full source and exact parent identity remain unresolved; no ancestry edge or model binding is inferred from the abstract. Original Wu–Bauer 1994 full-text access likewise remains unresolved. The earlier [screening ledger](../catalogue/screening.jsonl) preserves its first-pass decisions; these follow-up publication identities do not certify source-complete admission.

## Database and verification

The existing SQLite export now includes `publications`, `publication_relations` and `publication_models`. DOI hyperlinks and full canonical records, including source locators, remain in the database. Formulation bindings reference `models`; relation endpoints reference `publications`. Foreign keys are enabled during export. Re-export replaces the graph without accumulating duplicate edges or bindings. The graph is not yet exposed in the website.

`atlas.research.load_publications()` checks schema structure, normalized DOI identity, unique publications/relations, known formulation bindings, distinct relation endpoints and local evidence checksums. These checks protect representation and provenance; they do not independently verify scientific claims. Relations keep their evidence and pending review status in the export.

Run `python3 -m unittest discover -s tests -p test_publications.py` for offline graph, source-pointer and SQLite checks. No compilation or third-party model execution is needed. Next, extract original equations and reconcile corrections/versions before adding candidates; extend the graph across the remaining charter families and existing model sources. LIT-01 and LIT-02 remain open.
