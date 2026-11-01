# Independent erratum source-gate review

Task: MODEL-duncan-chang-1970, bounded E1/E2 review, 2026-11-01. Reviewer run: `/root/duncan_erratum_review`. This separate run did not author the coordinator's erratum receipt or reconciliation packet. Owned output is this directory only. This is not E5 model approval.

## Exact source and inspection

Private PDF: `.local/private-sources/duncan-chang-1970/erratum-1971-user.pdf`; independently recomputed SHA-256: `86ffd8f287981082869ee56b6cf69b490a8a598810930e6d836c867a0601d03a`.

The complete single rendered page was visually inspected at `.local/private-sources/duncan-chang-1970/erratum-1971-user.png`; extracted text was used only as a secondary aid. Printed page 1597 bears the title *Nonlinear Analysis of Stress and Strain in Soils*, heading *Errata*, and footer *Journal of the Soil Mechanics and Foundations Division*, 1971, 97(11):1597-1597. The title footnote identifies the September 1970 paper by James M. Duncan and Chin-Yung Chang, Proc. Paper 7513. The user's filename does not establish a 2021 formulation.

The PDF skill and `docs/AGENT_REVIEW_POLICY.md` were read. No author binary, compiled model, native/Wasm build or remote action was executed. The copyrighted PDF and render remain private.

## Scope and exact transcription

The correction expressly identifies the **discussion by Behzad Rohani and N. Radhakrishnan (July 1971), page 1037, Eq. 26**. It does not identify an equation in the September 1970 original as erroneous. Its common title and original-paper footnote do not authorize replacing any original Eq. 1-15.

The corrected displayed relation reads, using `nu` for the printed Poisson-ratio symbol and `pa` for the printed atmospheric-pressure symbol:

```text
epsilon_v = 3(1-2nu)/(K(1-n)) * [(sigma3/pa)^(1-n) - 1]
          + (1-2nu)(2c cos(phi) + 2sigma3 sin(phi))^2
            / [Rf K pa (1-sin(phi)) (sigma3/pa)^n]
```

Visual details matter: the square is outside the complete strength-like numerator parenthesis; `pa` occurs to the first power in the second denominator; `(sigma3/pa)^n` is also in that denominator. There is no second visible `pa` factor or additional strength divisor. No symbol definitions, derivation, parameter ranges or integration algorithm accompany the correction on this page. The unrelated discussion printed above the horizontal separator is not part of this erratum.

## Dimensional caveat and gate decision

Under the original article's conventions, `K`, `Rf`, `n`, `nu` and trigonometric factors are dimensionless, while `c`, `sigma3` and `pa` have stress units. Under those assumptions, the first term is dimensionless but the displayed second term has stress units: its squared stress numerator is divided by only one stress factor. This is an apparent dimensional incompatibility with a dimensionless volumetric strain. That conclusion is conditional on importing the original definitions into the separate discussion; the supplied erratum alone does not establish those definitions. It is not evidence for a particular repair.

**Accept this PDF as a readable, identity-bound erratum receipt; retain the corrected expression verbatim with the caveat above.** Do not implement this expression, change its power or denominator, or treat it as a correction to the original constitutive equations without the July 1971 discussion and context. This review does not certify full source completeness, a candidate, numerical verification, backend delivery, scientific admission or experimental validation.

The parent reports that original printed page 1647 remains missing; this review does not revisit or clear that independently documented defect. The smallest next source gate is to acquire original printed 1647. If the Rohani/Radhakrishnan Eq. 26 is to enter the implemented scope, also acquire their July 1971 discussion including p1037 and its symbol definitions, then reconcile the dimensional issue against readable source without inventing a correction. The original-law finite-increment, branch/event and postfailure decisions remain a separate E2 task.

Reproduction: run `shasum -a 256 .local/private-sources/duncan-chang-1970/erratum-1971-user.pdf`; render the complete single page with Poppler and compare the targeted discussion identity, equation numerator, denominator and exponents visually. This is a bounded source review and does not replace the nine-item exact-model E5 checklist.
