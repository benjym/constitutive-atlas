# Classic soil-model publication records

SRC-classic-publication-records-v1; 1 November 2026. Bibliographic integration only;
no additional model, equation transcription, scientific acceptance or new full text.

The canonical [publication graph](../../../catalogue/publications.json) now adds:

| Publication | Canonical model-family binding | Source role |
| --- | --- | --- |
| Duncan and Chang (1970), *Nonlinear Analysis of Stress and Strain in Soils*, [DOI](https://doi.org/10.1061/JSFEAQ.0001458) | duncan-chang-1970 | Original journal paper |
| Duncan and Chang (1971), erratum to that paper, [DOI](https://doi.org/10.1061/JSFEAQ.0001706) | duncan-chang-1970 | Separate correction record |
| Lade and Duncan (1975), *Elastoplastic Stress-Strain Theory for Cohesionless Soil*, [DOI](https://doi.org/10.1061/AJGEB6.0000204) | lade-duncan-1975 | Original journal paper |

Exact publisher-deposited Crossref records provide titles, authors, types and
publication date parts. Evidence pointers select `/message` with exact file hashes.
The two new Duncan–Chang responses are retained here; the existing
[Lade–Duncan metadata](../lade-duncan-1975/identity-v1/crossref-204.json) is reused.
No broad search or repeated inspection of already reviewed source identities ran.

The 1971 title explicitly calls itself an erratum for the 1970 paper, supporting
a `corrects` edge. Crossref's formal relation objects are empty; the edge is an
explicit bibliographic interpretation of that title, consistent with the
[existing original/erratum source packet](../duncan-chang-1970/README.md).
It does not identify corrected equations or certify that a model incorporates
the correction. The erratum is searchable separately and both records appear
under the same formulation-family filter.

The [receipt](receipt.json) identifies exact prior graph bytes preserved in the
content-addressed source archive. All eleven previous nodes and seven relations
are unchanged; the graph now contains fourteen nodes and eight relations. Both
candidate model definitions remain non-executable. The corrected Lade DOI is
retained; the unrelated Das/Seeley pile-uplift DOI is not added to this graph.

## Verification and remaining work

```sh
python3 -B -m unittest tests.test_classic_publications tests.test_publications tests.test_web_publications -v
python3 -B tools/build_publications.py --output /private/tmp/atlas-classic-publications-preview
```

All seven focused tests pass, and the standalone package contains fourteen records.
The first validation attempt rejected a missing per-relation review field; the
new edge now explicitly records independent review as pending.

Focused tests check primary metadata identities/pointers, the explicit correction
edge, exact preservation of previous nodes/relations, model-family bindings,
SQLite foreign-key consistency and static publication-browser JSON copies. These
are data/package checks, not a fresh visual-browser or hosted deployment claim.
No native/Wasm build, model execution, fit or private response access is involved.

Original Duncan–Chang and erratum full text remain missing; the exact original
Lade–Duncan publisher PDF request returned 403 HTML in its earlier identity packet.
The next source deliverable needs readable originals/correction content and
complete flow, hardening, elasticity, initialization and temporal contracts under
schema v0.3. Keep those gates open; metadata does not supply missing equations.
