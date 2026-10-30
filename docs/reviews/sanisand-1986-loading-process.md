# Dafalias (1986): loading-process source access and mapping gap

Status: bounded acquisition/definition audit, 2026-10-31. **Exact identity verified; full text not acquired or reviewed.** This is an access-gap packet, not a transcription of unavailable equations or closure of original SANISAND reversal semantics. No code, build, native execution or model/review-status promotion was performed.

## Identity and access evidence

The referenced source is Yannis F. Dafalias (1986), *Bounding Surface Plasticity. I: Mathematical Foundation and Hypoplasticity*, Journal of Engineering Mechanics **112(9), 966–987**, September 1986, [DOI / publisher record](https://doi.org/10.1061/%28ASCE%290733-9399%281986%29112%3A9%28966%29). The [author's UC Davis publications page](https://faculty.engineering.ucdavis.edu/dafalias/publications/) independently lists that title, volume and page range. This is Part I, not Dafalias–Herrmann Part II (112(12), 1263–1291) or the author's different 1986 anisotropic critical-state paper. Publisher metadata identifies ASCE copyright; no redistribution permission was established.

Local checks found no exact source: filenames in Downloads and `paper/results/sources`, relevant source receipts, and first-page text extraction for all 34 unarchived PDFs in those two directories yielded no title/identity match and no extraction failures. This is a bounded search, not proof the source exists nowhere locally; archives, other directories and unindexed scans beyond their first page were not exhaustively searched.

Primary access attempts: the publisher DOI page exposes identity/abstract metadata; the [publisher PDF route](https://ascelibrary.org/doi/pdf/10.1061/%28ASCE%290733-9399%281986%29112%3A9%28966%29) returned HTTP 403 through the browser tool; `doi/epdf` returned a cache-miss error and `doi/full` was inaccessible. Author/institution searches at UC Davis and NTUA did not locate an accessible original PDF. No access controls were bypassed. A search-index result advertised a full-text third-party mirror, but its provenance/permission was unverified and it was not acquired or used as equation evidence. No 1986 PDF hash, equation/page locator or visual-review claim is invented.

## What the available 2004 source actually establishes

Dafalias–Manzari (2004), *Simple Plasticity Sand Model Accounting for Fabric Change Effects*, printed p. 631 (PDF p. 10), Eq. (24) and its following paragraph, is available and was visually checked in the preceding decision review. Its source receipt is pinned in [original papers audit](../../catalogue/source-audits/original-papers-2026-10-31.json); local PDF SHA256 `b6e0f6ccfd018729a9bbd8492745af649c7682a8a1e929348ae25a728917e023`.

| Definition / decision | Established from the available source | What still requires 1986 full text or a separate numerical contract |
|---|---|---|
| 2004 hardening distance | Eq. (24), p. 631: `h=b0/((alpha-alpha_in):n)`; alpha_in is alpha at initiation of a new loading process. | Exact source definition of the start/end of a loading process, behavior across nested reversal/reloading histories and any retained previous-process memories. |
| Change relative to 1986 | The paragraph after Eq. (24) describes the expression as slightly different from the 1986 `(delta_in-delta):n`, with delta the distance between conjugate stress points. | Precise 1986 conjugacy/mapping and stress coordinate, whether delta is an oriented vector/tensor, which image state is stored, and exact definitions of n and delta_in at each event. The 2004 cross-reference is not a substitute for those definitions. |
| Trigger | The 2004 paragraph calls for alpha_in updating when its denominator becomes negative, according to the 1986 rules. | Whether a condition is evaluated on a yield surface, a predicted new loading surface, or another image; the role of elastic unloading before a new plastic process; strict sign versus equality handling; event location versus finite-increment prediction. |
| New-memory value | At initiation, 2004 alpha_in equals alpha; the associated ideal h is infinite. | Whether all reversals simply copy current alpha or whether the referenced rules use previous processes, interpolation or an overshooting correction. **No correction is inferred from a later model or a metadata abstract.** |
| Histories outside the anchor | 2004 Eqs. (26)–(27), p. 631, evolve fabric through plastic dilation and use retained fabric in dilatancy. No fabric reset is specified there. | A reference to 1986 does not justify deleting or resetting the 2004 fabric history. Initialization/preparation and zero-distance branches still need their own domains and transaction rules. |

The existing [original-equation dossier](../models/sanisand-2004-original.md#flow-hardening-and-fabric), [source/implementation decision table](sanisand-2004-decision.md), and [bounded event fixtures](../SANISAND_EVENT_FIXTURES.md) retain these distinctions. In particular, pinned OpenSees `integrate()` selects memory by a parent elastic trial-direction contraction, while the printed 2004 paragraph refers to a cone-normal denominator. The retained fixture demonstrates their different local signs; it does not establish which complete source loading process either corresponds to.

## Conditional algebra, not an imported 1986 rule

For *any* oriented distance definition `delta=x_image-x`, subtraction gives the identity

`(delta_in-delta):n = (x-x_in):n + (x_image_in-x_image):n`.

Thus replacing a distance-difference expression by a current-minus-initial state expression is justified only after the mapped-image term is specified and shown to vanish (or its deliberate omission is identified). This is elementary algebra under an explicit assumed distance definition, **not** a claim that the unavailable 1986 paper uses this notation, sign, coordinate or mapping. It cannot establish general multiaxial equivalence by identifying x with 2004 alpha or its image with alpha_b. No assertion of triaxial equivalence is made without the exact conjugate-point definitions.

## Next acquisition and review task

Acquire the exact **22-page Part I article, pp. 966–987**, through institutional/library access, an author-provided copy, or an authenticated user-supplied download. Keep the copy private; record origin, date, byte hash and version. Following the PDF skill, extract text for navigation, then render and inspect the complete pages containing conjugate-point definitions, delta/delta_in, loading-process initiation/update rules, reverse-loading/reloading diagrams, and any overshooting discussion. Record both PDF and printed page numbers plus equation/figure locators. Do not select an equation number before seeing the page.

Then build a genuinely source-located mapping for: (1) scalar loading/reversal, (2) multiaxial direction changes, (3) elastic unloading and re-entry, (4) nested reversal/reloading, (5) zero-distance initiation. Check whether the extra mapped-image term above survives under the source definitions. Only then specify a canonical 2004 memory/event policy and its software transaction scope. Event isolation, caller partitioning, cutback rollback and finite-step integration remain additional algorithm decisions even after source acquisition.

A separately identified author/institution lead is Dafalias–Taiebat (2016), *SANISAND-Z: zero elastic range sand plasticity model*, [DOI](https://doi.org/10.1680/jgeot.15.P.271), verified on [Taiebat's UBC publications list](https://geomechanics.civil.ubc.ca/). It may help locate the authors' later explanation of loading-process updates, but it is a **different model** and its equations were not reviewed in this packet. It cannot silently supply missing 1986 or finite-elastic-range 2004 rules.

Outcome: metadata/access work completed; primary full-text and canonical loading-process mapping remain unresolved. The machine-readable [audit](../../catalogue/source-audits/sanisand-1986-loading-process.json) records this boundary explicitly.
