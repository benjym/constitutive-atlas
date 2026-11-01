# Formulation survey search and screening

The survey must distinguish the breadth of constitutive ideas from the subset that the atlas can currently execute. The [development protocol](survey_protocol.json) sets those units and screening rules. It exercises discovery and title screening while leaving the final search depth, source review and scientific release open.

## Material scope addendum (2026-10-31)

The user-directed [scope decision](survey_scope_decisions.json) focuses the primary survey on soils, granular media, intact and jointed rock, and their interfaces. Standalone bulk concrete and geopolymer laws remain linked background. Soil/rock interfaces with a concrete counterface and cemented or bonded geomaterials remain eligible for source assessment. General theories with unspecified material scope still require primary-source review. This addendum leaves the frozen retrieval protocol, requests and occurrences unchanged; it does not replace independent scientific review.

## Current search evidence

The eight-theme Crossref pilot returned 200 occurrences forming 177 normalized DOI groups. Raw responses, HTTP headers, exact URLs, request and retrieval times, cursors, code and protocol snapshots are retained locally; [the search manifest](survey_searches.json) pins their identities. The [generated audit](../results/survey-discovery-audit/report.md) checks request parameters, hashes and ordering. DOI groups are bibliographic identifiers, not counts of unique complete formulations.

The two earlier shared Crossref batches contained predominantly biomedical titles despite geomechanics query labels. Their original bytes remain intact and [the quality audit](survey_legacy_quality.json) pins the evidence. The new requests explicitly set descending relevance order and a publication-date cutoff. They returned plausible field-specific titles and descending scores. This comparison does not isolate a single cause of the earlier search-quality problem. Crossref's [current API guidance](https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/) explains date filters, cursors and caching; actual saved responses remain the evidence for these requests.

## Identity and screening

Keep every discovery occurrence. Normalize DOI resolver forms and case without deleting suffix punctuation. Different DOIs remain separate publication records even when titles match. For records without DOIs, an exact title/author/year match produces a possible-duplicate group requiring review. Missing identity metadata does not justify merging records.

The current queue flags nine same-title groups across distinct publication identifiers for relationship review. These flags identify possible duplicates, versions or index records; they do not merge records or establish distinct formulations.

The initial [assisted title pilot](survey_screening.json) inspected the first five ranked items from each theme, yielding 37 DOI-level decisions. The 2026-10-31 extensions inspect the remaining titles from all eight saved queries, adding the initial extension decisions below (before the subsequent material-scope addendum):

| Query | Retrieval | Background/source tracing | Unresolved | Outside geomaterial scope | Added decisions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Soil | 5 | 9 | 4 | 0 | 18 |
| Bounding surface | 8 | 10 | 1 | 0 | 19 |
| Hypoplasticity | 6 | 2 | 0 | 0 | 8 |
| Rock | 8 | 2 | 10 | 0 | 20 |
| Creep | 8 | 5 | 4 | 2 | 19 |
| Coupled | 12 | 5 | 3 | 0 | 20 |
| Interface | 14 | 4 | 2 | 0 | 20 |
| Nonlocal | 4 | 4 | 8 | 0 | 16 |

The scope addendum subsequently routes three standalone concrete/geopolymer candidates from unresolved to linked background, preserving their identities, evidence locators and pending independent review. The ledger now contains 177 decisions: 93 for full-text retrieval, 46 for background/source tracing, 36 unresolved and two provisional exclusions outside geomaterial scope. Every DOI group in the bounded pilot has an assisted title decision. The local executable audit passed on 2026-10-31, checking discovery-response and protocol hashes, request parameters, unique publication identities, record structure, pending independent-review status, absence of formulation admission, and each evidence locator's publication occurrence and pinned response identity. The generated report records 177 decisions and zero groups without a title decision. All 16 focused screening-audit tests also passed. These checks do not verify scientific judgments, exact formulation identity or primary-source content. This finishes the bounded pilot's assisted title pass only; it establishes neither resolved eligibility nor completed systematic discovery. All independent review fields remain pending, and no formulation was admitted from title metadata.

The hypoplasticity query illustrates why discovery themes cannot be used as formulation labels or counts. Its remaining titles include several barodesy publications whose exact relationship requires primary-source comparison, a multilaminate candidate whose mathematical family cannot be inferred from its search route, and an experimental interaction report. Keep these publication records and review their content before assigning formulation identities, lineage or demonstrated capabilities. The recent posted-content candidate also needs its date checked against the search cutoff and its version relationship resolved.

The rock-query extension raises a further source-identity issue: several author-free records have constitutive titles, including soil laws, but title metadata do not establish whether their identifiers resolve to original formulation papers or secondary abstract/index entries. These remain unresolved pending source tracing. The same-title clay pair also remains two publication records pending relationship review. Missing authors alone do not prove that a record is secondary. Retain the discovery occurrence, link any verified original publication separately, and use the original equations for formulation extraction. Apply the material-scope addendum above; a language note is not itself grounds for exclusion.

The creep extension adds a manual near-title relationship question for the two Reedlunn 2022 rock-salt records (the conference DOI and the repository DOI); the exact-title flag did not identify this pair. Compare primary sources before merging formulation identities. Fractional-order candidates need review of the memory operator, initial history and any numerical approximation alongside constants and state variables; their titles do not establish a finite state dimension. The two material-scope exclusions explicitly name titanium alloys and steels and remain pending independent screening review. Retain these occurrences in the search accounting.

The coupled extension links the Liu–Muraleetharan Parts I and II for joint primary-source review: the formulation and its integration/calibration evidence may support one law rather than two. A surrogate candidate remains unresolved until its constitutive inputs, outputs and history map can be distinguished from a system-response emulator. For all coupled candidates, review constitutive closure, conservation equations and numerical implementation separately, and identify required thermal, hydraulic or chemical information without treating every field or component as another constitutive formulation.

The interface extension records response-scale questions for discrete joints, weak-plane continua, bulk mixtures and anchored/bolted systems. The discovery theme alone does not resolve those identities. Source review must distinguish traction/slip or opening laws from specimen-response fits and bulk stress/strain laws, and separate geometric and structural inputs from material constants. Dynamic testing or a dynamic slip program does not alone establish constitutive rate dependence; submerged or temperature-conditioned testing does not alone establish evolving hydraulic or thermal coupling. These are review questions, not capability assignments from titles.

The nonlocal extension retains general plasticity theories with unspecified material scope as unresolved rather than declaring them geomaterial laws from keywords. The standalone concrete and soil-simulant geopolymer candidates now follow the linked-background route under the material-scope addendum. Primary-source review must identify any spatial interaction or gradient operator, constitutive length information, extra boundary data and relation to discretization. These may require a boundary-value task rather than a homogeneous material-point comparison. A record returned by the nonlocal query does not establish that the law itself is spatially nonlocal.

A [partial primary-article text note](source_notes/gradient-rock-2018.json) now follows up the existing gradient-rock retrieval candidate. It has no atlas formulation identity, immutable source copy, completed full-text decision or admission. The title decision and pilot counts are unchanged. Selected source observations and a conditional analytic inference are separated and remain pending visual equation verification and independent review.

The [Margolin–Trent source follow-up](source_notes/margolin-trent-1992.json) links an unresolved discovery record to a possible original conference publication. It records selected primary-text observations and a publisher bibliographic cross-check while leaving the identifier relationship, closure, equation verification and independent review open. No title decision, formulation admission or completed full-text count changes.

One useful identity case is the joint-model title recorded under two DOIs: metadata show one page-301 record without authors and a pp.15–26 record naming Desai and Fishman. Their relationship needs primary-source review. Neither automatically merging them nor counting two constitutive formulations is justified by those metadata.

A [SANISAND publication-relationship note](source_notes/sanisand-lineage-2004-2008.json) distinguishes fabric-change, inherent-anisotropy and constant-stress-ratio compression questions using publisher abstracts. These are supplementary citation-tracing leads, not completed full-text decisions or new admitted formulations. Their exact lineage and reduction mappings require original equations.

At full-text review, establish the exact governing assumptions, equations, state evolution, variant and lineage. Keep reviews, corrections, applications, numerical implementations and recalibrations as linked evidence. A standalone failure criterion receives a criterion record; it is not a complete constitutive law. Engine limitations, inaccessible code or exclusion from the sand benchmark do not exclude an otherwise eligible formulation from the survey. Unavailable or ambiguous primary texts remain unresolved.

The [full-text screening ledger](survey_full_text_screening.json) now exercises that criterion boundary on one supplementary-route publication. It uses a provisional citation identity, without inventing a DOI or atlas formulation. The assisted decision remains pending independent review and contributes no admitted formulation or benchmark participant. It is separate from the 177 DOI groups and their title decisions above; it does not reduce that queue's outstanding title decisions. Its citation-tracing follow-up now has a partial primary-source review of selected constitutive ingredients and solution assumptions, with publication identity reconciled while preserving the title as originally cited. That partial review is not an additional completed full-text screening decision.

Run `python3 paper/scripts/validate_study.py` to check full-text record structure, evidence-page bounds and available local PDFs against their recorded SHA256. The cited-source archive and selected member are also checked when available. A missing copy is an access gap, not a successfully checked source; changed bytes require renewed review. The printed local-PDF count concerns completed screening records, not nested partial follow-ups. Full-text reading and selected visual page checks are recorded separately. The validator cannot establish scientific correctness or independent review. Local PDFs remain ignored, and the source's reuse terms must be checked before any archival distribution.

## Reproduction and next gates

Audit the pinned local retrieval and title decisions without making new requests:

```sh
python3 paper/scripts/audit_survey_discovery.py
```

A deliberate fresh retrieval uses a new directory:

```sh
python3 paper/scripts/fetch_survey_discovery.py --output paper/results/survey-discovery-rerun
python3 paper/scripts/audit_survey_discovery.py --manifest paper/results/survey-discovery-rerun/manifest.json --discovery-only --output paper/results/survey-discovery-rerun/audit
```

Review source locators before carrying title decisions into a new retrieval. The auditor rejects locators that point to different items or response hashes. It does not infer scientific inclusion from titles, keywords or ranking scores.

Before survey conclusions, audit the completed assisted title pass, resolve title-stage scope and identity questions, obtain primary texts, resolve exact variants and duplicate publications, and complete independent review. Define the final retrieval depth and stopping rule, then execute the atlas-seed, directory, foundational-source and citation-tracing routes in the protocol, screening additional discoveries. Report English-query and source-access biases. A target of fifty formulations is a collection-planning target, not a screening stopping rule or evidence of completeness.
