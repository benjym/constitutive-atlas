# Barodesy sand 2015 rate v1: bounded independent automated audit

Task AUDIT-barodesy2015-rate; review_vw96, 2026-10-31. Reviewed inputs are pinned in [reviewed-inputs.json](reviewed-inputs.json); no author packet, common code or scientific status was changed. Findings are scoped to [rate-study-v1](../rate-study-v1/README.md), not scientific admission.

**Outcome:** no source/sign or exponential-envelope blocker was found for the frozen 37-case instantaneous numerical proposal. Two reproducible wider-envelope oracle/support issues require revision before generalizing that result. Preserve the original v1 files and results. The frozen corpus still passes and is not evidence that every input in the declared parameter/loading envelope is certified.

## F1 (P2): fixed precision loses an admissible tiny volumetric trace

Locators: `rate-study-v1/reference.py:124` sums Decimal diagonals at the active 80/120-digit precision; `reference.py:140-142` repeats those grids. `check.py:29-32` accepts equal rounded outputs; `check.py:71-72` then requires exact zero when the reference void rate is zero. README line35 calls its void reference correctly rounded; protocol `void_accuracy.nonzero` makes the same claim.

The retained oblique admissible state/parameters with loading `[500,1e-130,-500,0,0,0]` is within the loading norm ceiling (about707.1), angle/expm support and state bounds. The exact sum of its actual binary64 diagonal inputs is the nonzero binary64 value 1e-130. At e=.75, exact rational arithmetic followed by one binary64 rounding gives **-1.7500000000000002e-130**. Both 80- and120-digit oracle evaluations return zero, while200digits and the current common DSL return that nonzero answer. The assessor falsely rejects the correct DSL rate as `exact zero void rate required`. The independent witness and complete inputs are in [findings.json](findings.json).

This demonstrates shared precision-grid loss, not a theoretical claim that200digits suffices for every allowed cancellation. Use exact Fraction summation of actual binary64 diagonals and exact multiplication by1+e (or dynamically sufficient Decimal precision) for the void channel. Use a distinct revision and retain v1. Do not simply increase a fixed precision and call the result correctly rounded. All37 frozen oracle void channels were separately checked against exact Fraction arithmetic and currently round correctly, so this finding does not invalidate that corpus.

## F2 (P2): ideal oracle acceptance differs from the model's operational domain

Locators: `reference.py:115-118` requires0<B<1 but does not check the model's additional rounded `ec>emin` condition, present at `model-draft.json:200`. Retained witness: the oblique request with c5=.1 and equal diagonal stresses `465000*1e9/sqrt(3)` has normalized stress norm1e9, inside the documented numerical envelope. B is positive but too small to separate ec from emin in binary64. The oracle accepts and returns float ec=.35; the model rejects its `ec>emin` domain condition. This is an operational-support mismatch, not proof of an incorrect physical CSL equation.

Separate an ideal/high-precision source oracle from a paired binary64 support validator, or explicitly enforce/report the rounded critical-density condition for the latter. Retain this case as a negative domain witness. It is outside the existing37valid/19invalid corpus and does not alter its replay result.

## Checks that support the narrow handoff

- Visually checked pinned primary2015 PDF printed pp53-56 and59: source R=-exp[c1*exp(c2*delta)*D0], Eq31, Frobenius stress norm and density continuity. With T=-Sigma,D=-E, delta=-tr(U), R0=-P and h=-K, the model's **positive** K[(v-c3*ec)P+c3*e*S]||E|| follows. No sign discrepancy was found. Three additional diagonal scalar-exponential witnesses independently reproduce the DSL's seven rates; this avoids shared matrix-exponential algebra.
- Verified2019 author-manuscript Table1 values remain a separately attributed fixture, not an exact2015 calibration/publisher equivalence. Standard trace interpretation, zero-loading extension, nonzero stress and W=0 restrictions are explicit. General finite-spin and zero-stress continuation remain unsupported.
- The bound ||argument|| <=2*exp(1.5*sqrt(3))≈26.876 is below the current generic Frobenius limit64. The argument is dimensionless, Mandel order/shear factors match Cartesian tensors, and the independent Decimal forward series differs from the generic Horner18 scaling/squaring algorithm. The series stopping rule and80/120agreement are empirical numerical evidence, not a rigorous total-roundoff certificate. No matrix-exponential AD or integration claim follows.
- Original13Python groups pass (including source generation only, not compilation); fresh37valid/19invalid replay passes with maximum reported stress scaled error≈7.60e-16. The independent audit additionally checks all37 void channels by exact Fraction arithmetic, three diagonal source witnesses and both findings. These bounded checks do not establish the full parameter envelope's accuracy.
- The future numeric proposal count68/backend is consistent: descriptor1+valid37+15(rejection+recovery)=68. Four named/type-only Python requests remain excluded, explicitly. Raw preparse journals, source/artifact binding and persistent recovery are proposed rather than implemented/executed. A later collector must bind every request/output and both raw companions, and reject malformed types independently; this audit does not certify a nonexistent collector.

## Reproduction

The audit verifies all reviewed source/dependency hashes before importing the original modules. From this directory in an installed checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 audit.py --output /tmp/barodesy2015-review.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_review.py
```

For a staged packet use `--repo /path/to/constitutive-atlas`; set `ATLAS_REVIEW_REPO=/path/to/constitutive-atlas` for unittest. Output must be a fresh path. Sources are linked and hashed, never redistributed; private PDF availability is not needed for numerical replay. Reviewed bytes changing makes replay fail explicitly rather than bless a revised implementation. `findings.json` is deterministic and fresh replay is checked exactly. Three independent audit groups pass. No builds, native/Wasm calls, author-code execution or repo writes occurred. No scientific admission is implied.
