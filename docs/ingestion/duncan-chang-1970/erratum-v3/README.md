# Duncan-Chang - 1971 erratum reconciliation v3

Task SRC-duncan-chang-erratum-v3, under MODEL-duncan-chang-1970. Coordinator /2026-11-01. Additive resumption after the user supplied the previously missing correction. [Current delivery ledger](../DELIVERY.md). Historical acquisition packets, failed checks, original scan and v2 independent review remain unchanged.

## Source receipt and identity

[receipt.json](receipt.json) records the exact one-page publisher PDF, private path, attachment provenance, SHA-256, byte count, access date and scope. The page/metadata identify Journal of the Soil Mechanics and Foundations Division97(11), November1971,p1597, [DOI10.1061/JSFEAQ.0001706](https://doi.org/10.1061/JSFEAQ.0001706). The filename2021 is not a new constitutive version. The page was text-extracted, rendered at1800pixels with Poppler and visually inspected. The raw PDF, OCR and render remain private under publisher rights.

The top of this page finishes an unrelated discussion about coupled flow and stress; it is not Duncan-Chang material. The lower section headed Errata explicitly identifies corrections to Behzad Rohani and N. Radhakrishnan's July1971 discussion, page1037, Eq26. Its footnote identifies the original September1970 Duncan/Chang article (Proc.Paper7513), but does not change the stated correction target to the original. Thus this receipt resolves the previously unknown correction scope: it does not instruct replacement of any original1970 Eqs1-15 or its constant-nu Hooke closure. No claim is made about the unseen discussion's full argument.

## Exact available equation and limits

Write x=sigma3/pa and A=2c cos(phi)+2sigma3 sin(phi). The corrected expression printed in the erratum is:

`epsilon_v = [3(1-2nu)/(K(1-n))] [x^(1-n)-1] + [(1-2nu) A^2]/[Rf K pa (1-sin(phi)) x^n]`.

This transcription is separately stored in [reconciliation.json](reconciliation.json). It is discussion Eq26, not an additional production state equation. The square on A, the pressure-reference factor in the denominator and exponent1-n were read from the image rather than inferred from broken OCR. The expression visibly contains denominators1-n and1-sin(phi); no limiting branch or zero-confinement handling is supplied by this one page.

Using the original article's units (c,sigma3,pa pressure and K,Rf,nu,n dimensionless), the first term is dimensionless while the second has one power of pressure. This is an apparent dimensional concern if epsilon_v has its original volumetric-strain meaning. The complete corrected discussion context is unavailable; this is not a proved defect in the original1970 material law. Do not remove a square, insert a missing factor, normalize stresses implicitly, or incorporate the expression into the original on inference. If the corrected discussion relation is used later, acquire p1037 and surrounding derivation, establish its normalization/notation, then independently verify it.

## Source-to-schema impact and integration contract

The [v2 source crosswalk](../supplied-original-v2/crosswalk.json) and [original-law packet](../supplied-original-v2/README.md) retain their original bytes and identity; their then-unread erratum statements are historical. This v3 reconciliation resolves that acquisition dependency without rewriting hash-bound evidence. Original Eqs1-15, constant-Poisson3D compliance, maximum historical principal-stress-difference memory, available parameters and proposed explicit v0.3 residual host are unchanged.

No new parameter, state field, physical-time term, objective rate, stress binding or generic capability follows from a separately targeted discussion correction. No legacy integration field, guessed equation, model-specific kernel or candidate is introduced. The existing finite averaging, equality/crossing/history ordering, initial prehistory and postfailure decisions still need a prospectively reviewed implementation contract. A source-complete claim is still unavailable: printed original1647 is missing from the supplied article (PDF19 repeats1645). Missing1647 must not be inferred from adjacent FE text.

## Checks and separate review

[checks.json](checks.json) records source size/hash, exact historical-v2 pin checks, local link/ignored-private checks and independent review binding verification. These are source-integrity checks. The dimensional observation is unit bookkeeping, not numerical validation. No new constitutive simulation, native/Wasm build, compiled call, fitting or author/vendor execution was needed for a correction that does not target the original equations. The existing363 source-algebra assertions remain evidence for their original scope and are not expanded into verification of discussion Eq26.

[Independent source review](independent-review/README.md) checks the exact one-page scope/transcription and dimensional caveat. It is not E5 model approval.

## Handoff and resumption

Erratum received and correction target reconciled. Main original source mapping remains available, but complete original-source gate stays open for printed1647. The discussion need only become a new source dependency if its Eq26/derivation is actually selected for a study; do not turn its absence into an unnecessary blocker for the original1970 formulation.

Smallest next source action: obtain original printed1647 through authorized access and reconcile it to the privately retained article. Continue finite-algorithm scope decisions and freeze candidate/reference/acceptance identity under a separately recorded implementation handoff. E3-E8 remain unstarted; model umbrella remains open. No approval, atlas/browser delivery, experimental validation, commit/push or deployment is claimed.
