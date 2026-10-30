# Literature screening — 2026-10-31

The original broad Crossref searches did not produce relevant geomechanics literature. Their 50 result occurrences resolve to 34 distinct normalized DOIs, all excluded at title/journal screening because they concern biomedical or human biomechanics research. This is a failed discovery sample, not evidence that relevant literature is absent.

The [publication ledger](../catalogue/screening.jsonl) preserves every occurrence through its raw-batch path, SHA-256 and JSON pointer. Each publication has a DOI hyperlink, decision, reason, screening basis, reviewer, date and unresolved questions. [The schema](../schemas/screening.schema.json) defines the record format. Screening was AI-assisted; independent review remains pending. No full-text or equation review is claimed.

| Scope | Result occurrences | Distinct DOI publications | Excluded | Include for full-text review | Unresolved |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original soil and rock batches | 50 | 34 | 34 | 0 | 0 |
| Targeted hypoplasticity probe | 3 | 3 | 0 | 1 | 2 |
| Combined ledger | 53 | 37 | 34 | 1 | 2 |

Publication identity is distinct from formulation identity. The 16 duplicate occurrences in the original batches were combined by normalized DOI. The two records `10.1067/mtc.2000.109245` and `10.1067/mtc.2000.109246` have identical titles but different DOIs; both are retained, with their relationship unresolved. No formulation IDs were assigned to these excluded papers.

## Search-quality follow-up

The original raw batches remain unchanged, including their retrieval-time `unscreened` status. Their relevance failure has no established cause. Do not infer a Crossref API defect, discard the responses, or silently count them as useful coverage.

A [new three-result probe](../catalogue/discovery/crossref-hypoplastic-probe-2026-10-31.json) uses an exact title plus authors/year and explicit relevance sorting. It returns the expected DOI for [Wu & Bauer (1994), *A simple hypoplastic constitutive model for sand*](https://doi.org/10.1002/nag.1610181203), also identified by the [publisher record](https://onlinelibrary.wiley.com/doi/10.1002/nag.1610181203). This paper is included for full-text review, with formulation identity and lineage still to establish. The other two results remain unresolved pending source review. None is an admitted model or an independent numerical reference.

Crossref's [API documentation](https://github.com/Crossref/rest-api-doc) supports `query.bibliographic` and `sort=score` / `order=desc`; its [query guidance](https://github.com/CrossRef/rest-api-doc/blob/master/api_tips.md) recommends specific bibliographic information for reference matching. The successful probe establishes a usable targeted query, not the cause of the earlier mismatch or comprehensive coverage of hypoplasticity.

Before scaling discovery, use known foundational references as checks, inspect query relevance, save the unmodified responses and retain exclusion reasons. Continue separate searches across all charter families, backward/forward citation tracing, and source availability/version screening. Broad queries alone cannot establish completeness. LIT-01 stays open.

## Verification

The SQLite export (`python3 -m atlas.cli database /private/tmp/constitutive-atlas.sqlite`) preserves screening alongside the publication lineage graph. The current union contains 43 distinct DOI publications: 37 screened papers and nine lineage nodes, with three shared identities. Shared DOIs use the richer graph record in `publications.record_json`; the unchanged screening record remains in `publication_screening.record_json`. Screening-only rows retain their canonical screening record in `publications.record_json`. Exclusions are retained, and an inclusion for full-text review does not become an admitted model.

`publication_screening` exposes decision, reason code, basis, full-text flag, reviewer, date and independent-review status as queryable columns. `screening_evidence` preserves all 53 raw search occurrences, including duplicate DOI hits, with their batch path, checksum, pointer and URL. Both tables have publication foreign keys. `publication_models` continues to represent only direct bindings from the lineage graph; screening model tags are preserved in screening JSON without becoming source bindings.

`atlas.research.load_screening()` validates the ledger before export opens the destination database. It checks schema, DOI identity, model tags, review/date consistency, repository-contained evidence paths, raw checksums and exact source metadata/pointers. Invalid evidence leaves an existing export unchanged. These checks establish provenance consistency; scientific judgment and independent review remain separate requirements.

For example, `SELECT decision, COUNT(*) FROM publication_screening GROUP BY decision;` reconciles the decision counts above. Join `publication_screening` to `screening_evidence` by `publication_id` to retrieve every search occurrence behind a decision.

Run `python3 -m unittest discover -s tests -p test_screening.py` to check schema conformance, DOI uniqueness, exact raw-source hash/pointer linkage, preservation of all captured result occurrences and the reported count reconciliation. These are static Python checks; they compile or execute no constitutive or third-party code. They establish ledger integrity, not independent scientific screening correctness.

Run `python3 -m unittest discover -s tests -p test_screening_export.py` for export round trips, foreign keys, duplicate-occurrence preservation, corrupt-evidence rejection and protection of an existing database on validation failure.
