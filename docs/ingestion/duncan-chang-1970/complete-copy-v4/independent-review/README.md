# Independent complete-copy source review

Reviewer run: `/root/duncan_complete_review`, 2026-11-01. Independent of the coordinator's acquisition/transcription and candidate authoring. Owned path: this directory only. This is a bounded E1/E2 source review, not E5 approval.

## Decision

Accept the alternate source as closing the missing original printed page1647 acquisition gap. Across the retained v2 and v4 copies, original printed pages1629-1653 are available. The separate erratum review remains valid: its correction targets Rohani and Radhakrishnan's July1971 discussion Eq26, not an original1970 constitutive equation. The discussion expression and its dimensional caveat do not enter the original-law implementation scope.

The alternate private PDF `.local/private-sources/duncan-chang-1970/original-alternate-user.pdf` independently hashes to `ff4ea5af81cfb9c618d77fcd66555aa98d364c747bd43acd5221c9ae6330eb1f`, 2,125,314 bytes. It has25 pages in sequence1629-1653. OCR misreads the1651 header as165}; visual inspection confirms1651. Some right-hand word endings in its1651 summary are faded/clipped, so this is not a claim of flawless legibility of every pixel; the retained publisher v2 page23 supplies the readable1651 text. No copyrighted source bytes or renders are distributed here.

## Visual findings

Read the PDF skill and agent-review policy. Visually inspected alternate title1629, constitutive equations8-12 on1635, Eq15a-f and surrounding text on1643, newly recovered1647 including Fig17 and surrounding paragraphs, and1651; compared1651 with retained publisher v2 render. Full alternate extracted text and historical v2 packet support surrounding passage checks.

Page1647 completes the preceding1646 sentence about Eq12 modulus evaluation. Its new content is the sand-footing finite-element example:204 elements,234 nodes, plane-strain strip-footing representation, Fig17,2.5psi load increments and mesh-boundary constraints. It introduces no new constitutive equation, state variable or universal modulus. It does not settle the material algorithm choices listed below.

Eqs8-12 agree with the v2 transcription: D=sigma1-sigma3, Df from Mohr-Coulomb, Ei=K pa(sigma3/pa)^n, Et=Ei(1-Rf D/Df)^2. Eq15 normal and engineering-shear compliance agrees; Mandel shear compliance is(1+nu)/E, not2(1+nu)/E. The source text explicitly calls the modulus an average-stress evaluation during an increment. It distinguishes stress-difference memory from strain-reference origin.

## Remaining algorithm requirements

Original acquisition completeness is separate from executable completeness. A named numerical realization still must declare equality at prior maximum D, unloading departure, reloading crossing, history update/rollback ordering, average stress convention, strength-boundary/postfailure scope, repeated principal values and initial preparation. Source1645 supports maximum attained D, not maximum normalized D/Df. Source1646 uses extrapolated load-induced stresses plus gravity for its FE demonstration; an implicit midpoint residual would be a project numerical choice. Source1643's small positive postfailure modulus is unspecified generally;1648's10psf is an arbitrary example value, not a universal constant. Constant nu and isotropic incremental closure are source approximations and do not reproduce dilatancy or prove general3D accuracy. No native/Wasm artifact, author binary, build, fitting, browser or experimental check was executed.

This review clears the original-source acquisition defect only. Exact executable model review, numerical qualification, backend qualification, admission and release remain separate gates.
