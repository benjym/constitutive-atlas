# Terracotta journal follow-up v1

SRC-terracotta-journal-followup; worker `terracotta_journal_source`; 2026-10-31. Separate additive packet. The parent packet, historical model and all compiled/reference evidence remain unchanged. This task used the PDF skill for read-only inspection. No author code was imported or executed, no native/Wasm build ran, and no model was admitted.

The requested complete journal PDF was **not obtained**. This acquisition task therefore remains a bounded source-access result. Ten new exact-rational checks expose the existing equality-boundary policy; they do not settle the journal's admissible domain. A descriptive v0.3 crosswalk makes the intended physical-time contract explicit without migrating the historical record.

## Acquisition evidence

Target: Max Wiebicke and Itai Einav, *A simple hydrodynamic model for clay*, JMPS192(2024),105789, [DOI](https://doi.org/10.1016/j.jmps.2024.105789). The primary publisher search identifies [PII S0022509624002552](https://www.sciencedirect.com/science/article/pii/S0022509624002552). Its landing route returned403 and PDF route a cache miss. DOI/Crossref routes were inaccessible in the web tool. Ordinary shell HTTP attempts failed DNS resolution under the worker's network restrictions; those failures are access evidence, not evidence that the URLs are invalid.

All20 current Downloads PDFs yielded first-page text without extraction errors; none matched hydrodynamic/Wiebicke/Einav/105789. Nine ZIPs had no matching member names for those terms or Terracotta. This extends the previous first-page scan with ZIP names, but does not search full PDF text, archive contents, RAR files or all private folders. [inventory.json](inventory.json) records these limits and the private detailed receipt path; unrelated filenames are omitted from this packet.

The [author-uploaded journal web text](https://www.researchgate.net/publication/382467665_A_simple_hydrodynamic_model_for_clay) remains readable and identifies an Itai Einav upload. Its page header identifies an open-access CC BY article. That is useful rights metadata, but this worker did not acquire or render the journal bytes. The directly linked [author journal PDF](https://www.researchgate.net/publication/profile/Itai-Einav-2/publication/382467665_A_simple_hydrodynamic_model_for_clay/links/685cea1e93040b17338dfdb4/A-simple-hydrodynamic-model-for-clay.pdf) returned a web cache miss. The [SSRN January2024 predecessor](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4699137) stays a distinct version and was not substituted. Neither raw source PDF nor figures are redistributed here.

The [author repository](https://github.com/MaxWiebicke/Terracotta-pq) root shows code/images/LICENSE/README, with no root PDF listed. Recursive API access failed; no whole-repository absence claim follows. [source-receipts.json](source-receipts.json) preserves attempted URLs, access classes, exact private source hashes and inspection distinctions. The source image and two author-code files still match all three parent hashes.

## What was actually rechecked

The pinned author equation image was opened and visually inspected in full. Its pressure, signed q, temperature and solid-fraction rates, elastic-strain system and factored transport coefficients remain consistent with the Figure1 transcription recorded in the parent packet. This is author-image evidence. It supplies no new journal page-image verification.

Read-only code inspection reconfirms:

- `plastCoefficients`, lines78–106: the implementation embeds `1/pc` in a,b,c, rejects only `a*c-b**2 < 0`, but prints a message asserting `>0`. Equality therefore is not rejected by this guard. A diagnostic string does not override executable branch semantics or establish journal strictness.
- `TmRate`, lines139–146: unhalved temperature production/sink. Mixed-control residual line301 halves the entire expression. The author image supports the unhalved form; full journal visual reconciliation remains open. No correction was selected.
- Example lines12–25: K=13e6kPa,G=5e6kPa,p1=.543e6kPa, M=.73,omega=.6,Lambda10, alpha=gamma=6e5Ks,eta150/(Ks),Gamma1K²/kPa. These establish the **rounded code preset**, not a newly verified journal Table1 calibration. The code comment claiming Table1 is provenance to verify, not independent table evidence.
- Example line36 adds Tm² to both stress entries without Gamma. Its zero-temperature start masks the issue. No general initialization rule was inferred.

## Strictness witness

[checks.py](checks.py) evaluates only rational algebra with Python's standard library, independently of Atlas and author implementations. With K=3/4,G=1, elastic strains(ev,es)=(1,1/2),phi=1,Tm=0, alpha=gamma=eta=1,M=1,omega=1/3,pc=1, the Figure1 formulas give pe=3/4,qe=3/2 and transport matrix[[1,-2],[-2,4]]. Its determinant is zero. The elastic Hessian also has determinant zero. All current nonstrict elastic/transport/global-order inequalities pass; the author's negative-only determinant branch does not reject equality. Strict positive-definiteness would reject this witness.

This intentionally marginal algebraic case is not a calibrated clay, admissible specimen, executable fixture or journal-supported boundary. It isolates the exact decision that the missing source must settle. [checks.json](checks.json) records ten passing assertions. Reproduce with `python3 -B docs/ingestion/terracotta-2024/journal-followup-v1/checks.py`. No creep histories were repeated.

## v0.3 mapping and pending reconciliation

[schema-crosswalk-v03.json](schema-crosswalk-v03.json) is a **non-executable crosswalk**, not a complete model document. It declares physical-time ODE, fixed spatial zero-spin axisymmetric-x loading, explicit SI time/rate inputs, Mandel storage, compression-positive conventions and algebraic total-stress binding. Four persistent states require explicit initialization; the signed shear-strain component retains fixed-component semantics. It does not claim full3D, finite-strain or finite-rotation support. No legacy `integration` field or implicit formulation defaults are used.

| Required journal check | Exact locator to obtain | Current result |
|---|---|---|
| Image/body expression reconciliation | Figure1 p2; Eqs23–24,29–32; Eq36 p10; Eqs37–38 | Author image verified; journal images absent |
| Strictness | Eqs28,53–54; determinant/stability derivation and Eq54 complete page | Nonstrict software policy exposed; journal equality policy unresolved |
| Calibration/preset identity | Eqs42–43,48,51; Table1 p14,Table2 p16 and complete captions/footnotes | Rounded code preset remains distinct from rounded phi1-derived preset |
| Fuller variant | AppendixB p26,B.1–B.4 and FigB.19 | Separate target; no coefficients transcribed from flattened text |
| Units/notation | AppendixC pp27–28 | Existing dimensional derivation remains author-image/code based; journal table unverified |

The smallest next source-supported action is an authorized download of the directly linked journal PDF, then hash and render the listed complete pages. A readable copy must first establish article identity, page count, exact inequality signs and table/footnote values. Full-source comparison precedes any change to domain guards, defaults or variant identity. Full journal source closure, author mixed-control reconciliation, source-matched external histories, scientific review and experimental validation remain open. Prepared creep parity already exists and cannot close these source gates.
