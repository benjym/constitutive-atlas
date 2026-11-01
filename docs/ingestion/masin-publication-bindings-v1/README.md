# Mašín clay publication coverage — 1 November 2026

Task **LIT-masin-publication-bindings-v1**. Bounded canonical-data addition; source completeness, scientific admission and release work remain open.

The canonical publication graph previously contained fourteen records, including Duncan–Chang1970, its1971erratum and Lade–Duncan1975. Its overview still reported eleven. Those existing records are preserved. This task adds three missing exact publication identities from publisher-deposited Crossref metadata, two direct existing-model bindings and **no new inferred relation**.

| Publication | Print date selected | Canonical formulation binding |
| --- | --- | --- |
| Mašín, *A hypoplastic constitutive model for clays*, [DOI](https://doi.org/10.1002/nag.416) | 10 April 2005 | `hypoplastic-clay-2005` |
| Mašín, *Clay hypoplasticity with explicitly defined asymptotic states*, [DOI](https://doi.org/10.1007/s11440-012-0199-y) | October 2013 | `hypoplastic-clay-2013` |
| Mašín, *Clay hypoplasticity model including stiffness anisotropy*, [DOI](https://doi.org/10.1680/geot.13.P.065) | March 2014 | None: research variants do not imply a top-level executable |

Unmodified metadata responses and [source receipts](source-receipts.json) retain DOI/title/authors, online/print/issued dates and acquisition hashes. The 2013 online date is22December2012; choosing the 2013 print identity does not rewrite it. The 2005 deposited family name is visibly corrupted (`Ma?�n`); display uses **David Mašín**, supported by the existing [2005 author-manuscript dossier](../hypoplastic-clay-2005/README.md). The 2014 deposited capitalization is normalized for display. Raw metadata is unchanged. No equation, correction, model state or historical scientific claim is reconstructed from metadata.

Bindings were checked against the respective top-level model `sources` entries, which already cite these DOIs. They identify source correspondence, not full-text equivalence or scientific review. The [2014 consolidation](../hypoplastic-clay-2014/consolidation-v1/README.md) preserves printed-Am/AppendixB discrepancies and the distinct retained research identity. No 2014 executable binding or builds-on edge is inferred from chronological proximity.

The resulting graph has seventeen publication identities, eight unchanged relations and seven direct formulation bindings. Existing nodes/edges are preserved semantically. Graph validation, exact metadata-pointer checks, SQLite export/foreign keys and standalone project-path publication packaging are checked by the existing offline tests:

```sh
python3 -B -m unittest tests.test_publications tests.test_web_publications
python3 -B tools/build_publications.py --output /private/tmp/atlas-masin-publications-preview/constitutive-atlas
```

Saved checks and current database counts accompany this packet. Packaging copies the canonical graph into the existing publication browser without changing UI code; no actual-browser or hosted-deployment claim is made. No model migration, constitutive execution, native/Wasm build, source-PDF acquisition or scientific promotion occurred. Full LIT-02 remains open across other charter families and existing model sources.
