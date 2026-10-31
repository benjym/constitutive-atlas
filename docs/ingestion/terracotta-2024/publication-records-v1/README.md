# Terra Cotta canonical publication records

SRC-terracotta-publication-records-v1; 1 November 2026. **Bibliographic integration complete; journal equation-image reconciliation remains open.** This additive packet leaves the prior source reviews, constitutive record and numerical studies unchanged.

The [journal DOI](https://doi.org/10.1016/j.jmps.2024.105789) and [SSRN DOI](https://doi.org/10.2139/ssrn.4699137) now have distinct canonical publication records. Unmodified Crossref responses supply exact titles, authors, types and date parts: November 2024 for the journal issue, and year-only 2024 for the preprint. No more precise preprint date is invented from that response. Only the journal is bound to the `terracotta-2024` candidate; neither record adds executable support.

The [publisher API](https://api.elsevier.com/content/article/PII:S0022509624002552?httpAccept=text/xml) supplies core metadata, including the matching DOI, open-access status and CC BY 4.0 declaration. Its licence URL agrees with Crossref's version-of-record declaration. This establishes the recorded journal licence declaration, not permission for external measurements or the separate preprint. Both Crossref relation objects are empty: no formal preprint edge or equation equivalence is inferred.

## Evidence and access boundary

[receipt.json](receipt.json) records the independent publisher/Crossref metadata agreement and access outcomes. The author-linked PDF and publisher PDF routes returned 403 HTML. The default XML endpoint returned metadata, not full equations; the full-content view required an API key. No authentication workaround was attempted. No PDF or page-image hash is claimed. Figure 1/body/Appendix B, typography-sensitive inequality and calibration reconciliation remain the existing source-review tasks.

The exact responses are `journal-crossref.json`, `preprint-crossref.json` and `publisher-metadata.xml`. Canonical evidence locators select `/message` inside the two JSON responses, with byte checksums. These are publication records under the existing publication schema, not new model definitions or a migration of the historical model. New constitutive records and crosswalks continue to target v0.3.

## Integration and verification

The graph now has eleven nodes and the original seven relations. The SQLite export has 45 distinct publication identities including the screening ledger, one Terra Cotta journal binding, no SSRN binding and no foreign-key violations. Exporting twice preserves exact records and bindings. Publication identity/source-pointer, graph corruption, database and deterministic static-browser packaging tests pass. Tests explicitly retain the candidate's journal binding and exclude its unreviewed preprint binding.

Actual browser inspection under `/constitutive-atlas/` shows two Wiebicke author-search results with journal/preprint labels and pending-review notices. Selecting the Terra Cotta formulation yields only the journal record. One Playwright label selector matched no control; fresh accessibility inspection and the supported native control action succeeded. The local standalone publication preview does not include the laboratory solver.

[prior-source.json](prior-source.json) identifies exact archived bytes of the prior graph, publication guide and test. Original graph nodes/edges remain unaltered; only scope/date and two nodes were added. No constitutive-model/compiler/schema changes, native/Wasm builds, material calls, scientific signature, push or deployment. The next Terra Cotta equation-review trigger remains a readable journal PDF/page packet or a new concrete primary-source lead, not another repetition of these blocked routes.
