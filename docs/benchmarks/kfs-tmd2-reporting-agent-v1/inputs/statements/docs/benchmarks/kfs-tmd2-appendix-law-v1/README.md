# TMD2 benchmark: source-law and input review

1 November 2026. The complete printed 2016 Appendix A was checked against the
existing VW96+IGS record. **No constitutive transcription correction was
identified.** The appendix directly supports the general eight-constant host,
including the selected beta = 2.5, composed with the IGS overlay. This closes a
technical source-reading gap for this benchmark, not a scientific-admission gate.

The original NH97 appendix specializes its host to beta = 1. This review checks
the general composition actually used by TMD2 against [Wichtmann and
Triantafyllidis (2016)](https://doi.org/10.1007/s11440-015-0402-z), Appendix A,
Eqs 7–19, rather than transferring that specialization or illustrative defaults.
The [2019 comparison](https://doi.org/10.1016/j.soildyn.2019.05.001) remains the
source for the previously frozen isolated model curves. Sources and persistent
hyperlinks are retained in [the review receipts](source-review/sources.json).
Private PDFs and renders are excluded.

## What was checked

The [source review](source-review/README.md) records the full equation crosswalk,
visual inspection coverage and source/project distinctions. It independently
checks backbone factors, both IGS loading branches, stress/strain/history sign
conversion and Cartesian/Mandel contractions. Its exact structural checker
passes 24 stress/history/branch fixtures, including shear history directions,
and 10 independent Cartesian-to-Mandel contraction checks. Coefficient
surrogates test algebraic structure; they are not TMD2 material-rate references
or runtime verification of the model expressions.

The coordinator's separate [input audit](bindings.json) passes 26 checks:

- Current IGS definition matches the selected case hash and the complete model embedded in the compiled benchmark metadata.
- All 13 published material constants, the separate p_ref scale and unit conversions bind to the named parameter order.
- Nominal 100 kPa isotropic stress, e0 = .975 and mobilized isotropic history bind to the complete state order. The measured first point and example defaults remain separate.
- Both recorded source and portable runs bind to the same three requests, 400/800/1600 increments, numerical settings and exact full-range control bits. The portable receipt reuses shared frozen files as documented; it does not duplicate all inputs.

A descriptive inspection of the existing 401/801/1601 saved points finds
history-norm/R ranges of approximately .99999215–1, .99998955–1 and
.99998890–1 respectively, with no displayed binary64 norm above one. This is
not an exact inequality proof or evidence about unrecorded internal stages.
No new numerical acceptance gate was introduced.

## Qualifications that remain

The 2016 appendix alone is not a self-contained historical implementation
specification. Void-ratio continuity comes from original VW96 Eq 2; explicit
tensor conventions are supported by the original NH97 sign discussion.
Zero-history and near-isotropy continuations, the rho cap/1% history admission
band, runtime guards and finite-step integration policies retain their separate
source/project provenance. The review establishes printed-law correspondence
on its stated physical domain, not equivalence throughout numerical overshoot
bands or all internal stages.

Exact historical decks, source software versions and finite-strain/output
conversion remain unverified. The existing 0–25% study is a qualified
operational reconstruction. Its publication-precision envelope, refinement
gates and failed/passing results remain unchanged. Experimental errors remain
descriptive calibration-campaign errors, not held-out validation. Original
measurement redistribution permission is unresolved.

The [unsigned review checklist](SCIENTIFIC_REVIEW.md) makes the next decisions
concrete. Reviewer and decision remain unassigned/pending. A scoped review of
this benchmark does not grant general IGS admission or close REV-04/REV-05,
M1 or M4. No model/schema/status change, material call, build, fitting, author-code
execution, push or deployment occurred in this task.

## Replay and retained weaknesses

```sh
python3 -B docs/benchmarks/kfs-tmd2-appendix-law-v1/verify.py
```

Replay checks file/source bindings, repeats the exact structural algebra and
reproduces bindings.json without invoking an Atlas evaluator or backend.
The visual source-reading claim requires the private primary PDFs; replay does
not certify that claim or confer scientific approval.

The first input-check script incorrectly assumed the reduced portable receipt
packet duplicated requests.json. Its FileNotFoundError and exact initial
script are retained. The corrected resolver follows the already documented
shared-input layout and checks the portable freeze's exact hashes; no study
input or gate changed.

The coordinator also rejected the first Mandel check as weak: it repeated its
own weighted-dot definition. The source-review initial files are retained;
the final checker constructs full Cartesian matrices and independently maps
and contracts Mandel vectors in exact Q(sqrt(2)) arithmetic. No equation
conclusion changed. This review was performed after the original numerical
observations and is not claimed as a prospective review of them.
