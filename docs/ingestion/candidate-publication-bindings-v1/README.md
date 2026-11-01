# Nine-family publication coverage

LIT-candidate-publication-bindings-v1, 1 November 2026. This is a bounded database and source-link addition under LIT-02, without equation transcription, model execution or scientific promotion.

The canonical publication graph grows from seventeen to twenty-six publications and from seven to sixteen direct formulation bindings. All seventeen previous nodes and eight relations are preserved exactly. No new ancestry, correction or equivalence relation is inferred from shared authors or chronology.

| Source identity | Direct formulation binding | Scope retained |
| --- | --- | --- |
| Dafalias & Manzari2004, [Simple Plasticity Sand Model Accounting for Fabric Change Effects](https://doi.org/10.1061/(ASCE)0733-9399(2004)130:6(622)) | `sanisand-2004` | Reversal/loading-process source and reviewed scope remain unresolved; failed fixed-memory qualification retained |
| Manzari & Dafalias1997, [A critical state two-surface plasticity model for sands](https://doi.org/10.1680/geot.1997.47.2.255) | `manzari-dafalias-1997` | Missing full text; no substitution of2004 equations |
| Jefferies1993, [Nor-Sand](https://doi.org/10.1680/geot.1993.43.1.91) | `norsand-1993` | Original equation images/closure still missing |
| Wheeler et al2003, [An anisotropic elastoplastic model for soft clays](https://doi.org/10.1139/t02-119) | `s-clay1` | Corrected publication identity; full text missing; later S-CLAY1S separate |
| Niemunis, Wichtmann & Triantafyllidis2005, [A high-cycle accumulation model for sand](https://doi.org/10.1016/j.compgeo.2005.03.002) | `hca-sand-2005` | Recorder, cycle-count phases and amplitude/operator scope remain open |
| Niemunis & Herle1997, [Hypoplastic model for cohesionless soils with elastic strain range](https://doi.org/10.1002/(SICI)1099-1484(199710)2:4%3C279::AID-CFM29%3E3.0.CO;2-8) | `hypoplastic-sand-igs97` | Original overlay source; separate VW96 base law and project integration choices remain |
| Kolymbas2015, [Introduction to barodesy](https://doi.org/10.1680/geot.14.P.151) | `barodesy-sand` | Selected law differs from2019 illustrative parameter fixture |
| Medicus & Fellin2017, [An improved version of barodesy for clay](https://doi.org/10.1007/s11440-016-0458-4) | `barodesy-clay-2017` | Selected body2p/zero-spin draft; Appendix6p and preparation claims separate |
| Mugele, Stutz & Mašín2024, [Generalized intergranular strain concept and its application to hypoplastic models](https://doi.org/10.1016/j.compgeo.2024.106480) | `research-hp-extracted-asbs-gis-2024-v03` | Exact selected extracted-ASBS/f=0/zero-spin draft; ordinary default failure retained |

Unmodified publisher-deposited Crossref responses and their exact URLs/hashes are retained in [source-receipts.json](source-receipts.json). They establish bibliographic identity only. Print dates are selected consistently: barodesy clay appeared online in2016 and in its2017 issue. The NorSand deposited title misspells “simple” as “simle”; the deposited title is preserved rather than silently corrected. Author capitalization is also preserved. No missing equation, source license or dimensional closure is inferred from metadata.

Bindings reuse existing catalogue discovery identities or exact DOI citations in top-level model sources. The additional [binding-scope ledger](binding-scope.json) records the distinct unresolved contract for each. A direct binding means that the publication is a source for the selected formulation or family; it does not claim that every equation, preparation or algorithm in the paper is implemented. Non-executable candidates stay non-executable. All eleven current model definitions remain byte-identical.

## Verification

`python3 -B docs/ingestion/candidate-publication-bindings-v1/verify.py` checks the pinned addition, original graph prefix/relations, raw metadata, full canonical records/bindings in SQLite, foreign keys and exact static publication packaging. Existing tests run with:

```sh
python3 -B -m unittest tests.test_publications tests.test_web_publications tests.test_classic_publications
```

All seven pass. `baseline-tests.txt` retains a pre-existing failure: the classic-publication test required exactly fourteen live records after the earlier graph had already grown to seventeen. Its corrected assertion permits later additions while retaining exact original node/relation prefix and the three specific classic identities/bindings. No scientific or numerical gate changed.

Eight exact prior shared-document/map snapshots and four reverse receipt edges are preserved through additive document-bound archive maps. No historical evidence document or model definition is rewritten. The standalone preview contains all twenty-six canonical records beneath the project path; no actual-browser, full laboratory package or hosted deployment claim is made. No builds, material calls, source-PDF retries or messages to third parties ran.

This completes only the bounded publication-data addition. LIT-01/LIT-02, full-source ingestion, independent reviews and the twenty-formulation release remain open. The next priority is source closure and agreed scientific review; these metadata records do not unlock blocked equations or justify another numerical campaign.
