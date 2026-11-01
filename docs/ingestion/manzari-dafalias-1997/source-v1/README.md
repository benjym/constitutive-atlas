# Original Manzari-Dafalias 1997 source acquisition v1

Final source status: original full18-page public document read, privately captured and visually inspected. All constitutive equations (1)-(29), Appendix(A1)-(A2), Table1 and extension calibration prose have visual mathematical verification. Figure3's image remained blank in the normal viewer, although its complete caption, surrounding definitions and all associated equations are readable. No original PDF bytes were obtained. The earlier acquisition-stage notes below are retained and superseded by `visual-verification.md`.

Task: SOURCE-md1997-v1. Owner: /root/md1997_source. Date: 2026-11-02.
Owned scope: this new directory and ignored `.local/private-sources/manzari-dafalias-1997/`. Historical parent packet is unchanged.

## Identity and receipt

M. T. Manzari and Y. F. Dafalias (1997), *A critical state two-surface plasticity model for sands*, Géotechnique 47(2), 255-272, [DOI](https://doi.org/10.1680/geot.1997.47.2.255).

The normal [public document preview](https://fr.scribd.com/document/370351301/manzari-dafalias-1997) supplies original-paper OCR covering printed pages 255-272 and a public cover image. The cover image was actually inspected visually: title, both authors, 1997, volume 47, issue 2, pages 255-272 and printed page 255 match. This resolves the conflicting GW profile citation in the historical packet in favour of the DOI/UCD identity. The rehost is user-uploaded and marked all rights reserved, not an author repository or redistribution licence.

Private receipt paths and exact hashes appear in `source-receipt.json`. No PDF was obtained. The saved HTML and extracted OCR are copyrighted source content and remain ignored/private. The full public OCR contains corrupt mathematical glyphs (lost overbars, radicals and rate accents); it is a useful source-navigation aid, not a fully verified equation transcription. Only the cover has visual verification. No all-page scan or equation-page visual verification is claimed.

The public response declares `showFullDoc: false`, `show_archive_paywall: true`, and `type: view_restricted`. No access-control bypass was attempted. Normal computer browser inspection could not proceed because CUA reported no browsers and a locked Mac. Docin's normal public route returned HTTP 555. These are session outcomes, not a claim that an authorized original is unavailable everywhere.

## Renewed acquisition evidence

Downloads/private source filenames were checked first. First-two-page `pdftotext` indexing across all 34 PDFs in those two locations found only the supplied 2004 paper, not the target original. This expands the historical filename-only check, but does not exhaustively index every page or all arbitrary filesystem locations.

Direct normal DOI and ICE PDF requests each returned HTTP 403, including an approved network-enabled retry. Fresh targeted GW/UCD/NTUA/eScholarship searches found original citation records and later models. [NTUA original record](https://dspace.lib.ntua.gr/xmlui/handle/123456789/12121?show=full) lists no attached files. OpenAlex metadata marks the NTUA location green/open, but its `pdf_url` is null; its full-text flag does not establish acquired original bytes. SciSpace's normal article page exposes an original DOI and a Get PDF label, but the web representation returned no direct PDF link. No author was contacted, no form submitted and no author binary executed.

## Equation navigation and bounded transcription plan

The following inventory is from the received original-paper OCR, rather than search snippets or the 2004 formulation. Expressions requiring mathematical-page verification must not be used as source-approved executable definitions yet. `equation-inventory.md` separates the readable structure from glyph questions.

| Printed page | Original equations/content | Required reconciliation |
| --- | --- | --- |
| 257-259 | (1)-(5), state parameter; triaxial wedge; peak/dilatancy/critical ratios | Signs and Macaulay operations; compression/extension branches |
| 259 | (6)-(8), additive rates and pressure-dependent isotropic hypoelasticity | Rate symbols; exponent; optional bulk-pressure floor |
| 260 | (9)-(15), cone, normal, flow, multiplier, stress rate and hardening consistency | Radicals, accents, barred hardening direction symbols |
| 260-261 | (16)-(17), modified Lode angle and interpolation | Overbar on translated stress ratio; invariant powers |
| 261-262 | (18)-(22), image tensors and three surface radii | Tensor versus scalar alpha; radical prefactor |
| 262 | (23)-(26), isotropic and kinematic hardening | Barred coefficients; eq25 factors; eq26 fraction |
| 263 | (27)-(29), dilatancy, modulus and logarithmic CSL | Restriction branch; radical coefficient in (28) |
| 264 | Table 1, Nevada sand calibration | All entries and unit text need visual table check |
| 266 | Extension constants and cyclic comparison | Values and parameter identity need visual check |
| 269-270 | State sufficiency and initialization | Approximate alpha/r relation is not a unique exact initialization |
| 271-272 | (A1)-(A2), optional void-ratio-driven isotropic hardening | Exponent n, limiting branch and coefficient |

## Schema v0.3 crosswalk and integration contract

The current schema and formulation contract were read. No executable JSON record, legacy `integration` field, state-size assumption or generic capability implementation is supplied by this source task.

The inspected original prose identifies additive elastic/plastic strain rates and isotropic hypoelasticity; a dot is described as a time rate, while no physical rate-dependent material coefficient is identified. A strain-path rate representation is a candidate only after complete equation and homogeneity checks. Effective stresses are explicit on page 256. The volumetric relation for void ratio and compression-positive interpretation must be reconciled with actual source notation; tensor notation uses the trace inner product. A fixed spatial, small-strain Mandel implementation is an Atlas adaptation requiring its own declared scope, not a source statement that an objective rate or finite deformation update is unnecessary in every use.

Candidate persistent quantities are effective stress, void ratio, back-stress-ratio deviatoric tensor and yield-size scalar m (constant in the published numerical examples). Bounding/dilatancy/critical images are derived from current state. The original conclusion explicitly distinguishes this model from history-memory schemes. No 2004 fabric tensor or reversal-anchor state should be added without another source. The appendix supplies an optional evolving-m variant; it must not be silently mixed with the constant-m example calibration.

Original source numerical finite-step details remain insufficiently inspected: trial/commit/rollback, adaptive-substep ownership, first yield intersection, unloading selection, singular states and an algorithmic tangent are not established by the rate equations. Atlas transactions should read an immutable committed parent state, atomically commit every persistent state on success, and restore all state on failure/cutback. These are project requirements, not attributed source quotations. Preparation must carry a consistent stress/void-ratio/alpha/m state. Initial alpha is described qualitatively as close to initial stress ratio for a small elastic range; that does not uniquely determine alpha for a finite radius.

Critical unresolved implementation branches include yield-interior elasticity, first yield, reverse loading, p approaching zero, bulk-only pressure floor selection, the denominator in (12), distance denominator in (26), bounding-surface crossing/softening, the loose-state zero-dilatancy override, and the optional appendix e=emin limit. Freeze their policy before compiled results. No new generic schema gap is asserted solely from partial OCR.

## Independent checks and next action

No compiled call or constitutive numerical check was run. A source-only acquisition report need not invent a reference fixture. After mathematical-page verification, prospective independent checks should cover: (i) cone-gradient finite differences against (10); (ii) Lode interpolation endpoints; (iii) equality of all three image surfaces at psi=0; (iv) triaxial reduction of (27); (v) consistency derivation of (15)/(28); (vi) critical-state zero dilatancy and fixed-m hardening limit; (vii) both branches of the loose-state dilation restriction; and (viii) appendix endpoint/derivative checks if that variant is selected. Independent Python algebra should precede implementation and compiled observations.

Acquisition-stage next action was resolved using the normal public viewer's offered ad-supported reading option. The selected source-supported constant-m variant, exact verified formulas and remaining project choices are in `visual-verification.md`. The parent retains E0-E8 continuation; receipt completion does not establish numerical verification, scientific admission, browser qualification or live delivery.
