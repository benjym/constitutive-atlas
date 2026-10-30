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

Run `python3 -m unittest discover -s tests -p test_screening.py` to check schema conformance, DOI uniqueness, exact raw-source hash/pointer linkage, preservation of all captured result occurrences and the reported count reconciliation. These are static Python checks; they compile or execute no constitutive or third-party code. They establish ledger integrity, not independent scientific screening correctness.
