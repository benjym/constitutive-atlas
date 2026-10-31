# barodesy-sand — ingestion packet

Task ID: ING-barodesy-sand
Owner / date: review_igs97 / 2026-10-31
Scope: select the dated Kolymbas2015 sand formulation and transcribe its interior rate, state and integration contract. This packet does not implement or admit a model.

## Identity and sources

Selected: D. Kolymbas (2015), *Introduction to barodesy*, Géotechnique **65(1),52–65**, [DOI10.1680/geot.14.P.151](https://doi.org/10.1680/geot.14.P.151). The original title page explicitly says sand, and records revised acceptance28November2014. The received institutional publisher PDF has14pages and a current Emerald delivery watermark. [source-audit.json](source-audit.json) records exact received bytes, private paths, hashes and visual scope. PDF pages1–9 (printed52–60) were visually inspected using the PDF skill. Raw copyrighted PDFs, extracted text and rendered pages are excluded.

The [2012 predecessor](https://doi.org/10.1002/nag.1051), online2011/issue2012, is a different law. Original2015 p52 identifies changes to its exponential stress-direction mapping and stress-dependent stiffness. Its full equations were not acquired or inferred here. The [2017 Medicus–Fellin clay law](https://doi.org/10.1007/s11440-016-0458-4) and clay subroutine are distinct. The [2019 Kolymbas–Bathaeian author manuscript](https://doi.org/10.1002/nag.2984), obtained from an [author-affiliated publication download](https://www.ilf.com/news/publications/?download-id=752351), independently reproduces the2015 sand law in Eqs11–15 and attributes it to2015. The [2021 critical-void-ratio revision](https://doi.org/10.1002/gete.202000037) is not substituted. No author program was executed or copied.

## Existing work and gaps

This resolves the previously unspecified sand candidate in [parallel candidate triage](../../reviews/parallel-candidate-triage.md). Existing [clay2017 source work](../../reviews/barodesy-clay-2017-source-packet.md) remains unchanged. Existing symmetric matrix-exponential infrastructure may be reusable after its actual current support envelope is checked; clay equations and calibration are not reusable sand evidence.

## Equations and schema crosswalk

Use tension-positive source Cauchy stress T and stretching D, norm |A|=sqrt(tr(A²)), normalized A0=A/|A|, sigma=|T|, d=|D|, delta=tr(D0). Compression is negative. D is a symmetric velocity gradient, not engineering shear. The source's p53 printed trace mistakenly repeats D22; the same paragraph's strain trace and Eq20 support D11+D22+D33. This explicit interpretation is used below.

| Source locator | Quantity | Schema representation / units | Status |
| --- | --- | --- | --- |
| p53 notation; Eq20 p55 | T and e, e_dot=(1+e)trD | symmetric stress6 plus scalar void ratio; seven state components | No fabric, yield memory or reloading flag in this selected version |
| Eq9 p54 | R=-expm(c1 exp(c2 delta) D0), R0=R/|R| | dimensionless symmetric **matrix** exponential and norm | Not scalar/componentwise exponential |
| Eqs23,26–27 pp55–56 | h=-(c4+c5 sigma)/(e-emin); B=(ec0-emin)/(ec0+1) ((c4+c5 sigma)/c4)^(-(1+emin)/c5); ec=(emin+B)/(1-B) | h stress; B/ec algebraic dimensionless | ec recomputed at every stage; not an extra history state |
| Eqs29–31 p56 | f=delta+c3 ec; g=-c3 e; T_dot=h(f R0+g T0)d | six stress rate components | Final full sand interior rate |
| Eqs25–27 pp55–56 | d sigma/d ec=-(c4+c5 sigma)/((1+ec)(ec-emin)) | independent CSL derivative fixture | Inverse identity; not the arbitrary finite-path e trajectory |
| pp57–59 calibration/tests | c1..c5,ec0,emin | c4 has stress units, all others dimensionless | Calibration is tentative; not experimental validation |

Parameter order proposed: c1,c2,c3,c4,c5,ec0,emin. Original2015 gives approximately c1=-1.025,c4=465kPa,c5=28,c2=1,c3=-2.3 in final calibration Eqs32–36. Its earlier trial c2≈0.8 is not the final step(c) choice. The inspected original does not provide one unambiguous complete seven-number calibration table: ec0=.90 is identified for the Fig2 illustration, and Table1 is experimental data, not a seven-parameter list. The independent2019 Table1 supplies c1=-1.0246,c2=1,c3=-2.3,c4=465,c5=28,ec0=.87,emin=.35. Those are explicitly **2019 illustrative fixture values**, with c4 interpreted in kPa for these tests, not a claim to exact2015 calibration. Its prose's measured Hostun minimum .63 differs from internal emin=.35; original2015 pp55–56 explains that the internal minimum can be smaller than conventional measurements.

Proposed restricted numerical interior: finite parameters, c1<0,c3<0,c4>0,c5>0,ec0>emin>=0, finite nonzero compressive stress, e>emin, nonzero D; positive finite power base and1-B>0. These restrictions support a first research implementation, not source-declared universal parameter bounds. No clipping of e, B, eigenvalues or tensile stress. Physical cohesionless applicability is not established merely because an algebraic evaluation is finite. Stress-free starts, minimum-density boundary and parameter limits such as c5=0 need separate source/limit decisions.

For Atlas compression-positive Sigma=-T and E=-D, set U=E/|E|, v=trU, a=c1 exp(-c2 v), P=expm(-a U), P0=P/|P|, K=(c4+c5|Sigma|)/(e-emin). Then Sigma_dot=K[(v-c3 ec)P0+c3 e Sigma/|Sigma|]|E| and e_dot=-(1+e)trE. This sign map is derived, not a new sand variant. Use orthonormal Mandel ordering xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz with explicit conversion tests. [schema-integration-ledger.json](schema-integration-ledger.json) makes proposed orders and guards machine-readable.

## Temporal integration and transactions

The law is positively homogeneous of degree1 in D and rate independent. A monotone path parameter may replace time when D is its derivative; physical hold duration has no constitutive effect in this version. Parameterizing by strain does not imply that stress or void ratio can be advanced independently. Every trial stage recomputes sigma,D0,delta,R,R0,B,ec,T0,h from the same trial T/e and supplied instantaneous D. No lagged ec, retained direction, unloading surface or reset is specified. Reversal changes D0 and must be evaluated freshly.

At D=0 the continuous stress and density rate extension is zero for a fixed admissible nonzero T/e and bounded directions, but D0 itself is undefined. This is an explicit candidate extension, not a literal source branch; the general loading derivative is not unique at zero. At T=0, g T0 has a direction-dependent limit when g≠0. Finite stiffness at sigma=0 does not resolve this normalized-stress ambiguity. No artificial stress seed or T0=R0 policy is selected.

Original p58 permits forward Euler with sufficiently small steps; it does not define error tolerances, embedded stages or acceptance policy. An eventual common solver must keep each trial local; reject any invalid intermediate, nonfinite derived quantity, expm overflow or density boundary; restore the complete parent state on failed update. Commit all seven components atomically only after a successful complete requested update. Accepted substep diagnostics are evidence of attempted progress, not committed partial state after failure. Source does not supply this transaction API: it is the proposed Atlas numerical contract.

The first bounded target should be a fixed or supplied corotated frame with W=0, full strain-control, nonzero compressive initial stress and specified initial e. Source p59 notes prior Jaumann usage but leaves substantial-shear objective-rate choice unresolved. A future spatial rate needs an explicitly versioned spin/objective convention and work-conjugate input mapping; do not silently append W T−T W as source-equivalent. Mixed drained triaxial conditions require solving the unknown lateral D2=D3 at each stage (p59), not prescribing an arbitrary lateral strain or using old-state lateral closure. No plastic/elastic decomposition or source analytic consistent tangent is specified. Matrix exponential derivatives and normalization derivatives are needed for general implicit AD; zero loading and zero stress require separate treatment.

## Independent checks

Run from the installed owned directory: `python3 -m unittest -v test_algebra` and `python3 algebra.py --check fixtures.json`. The stdlib-only algebra checks CSL endpoint/derivative/asymptote, mass balance, diagonal critical-state cancellation, positive rate homogeneity, reversal distinction, matrix-vs-componentwise exponential, conjugation covariance and the zero-stress directional ambiguity. Fixtures retain exact definitions and finite numerical outputs. They are deliberately not a full tensor integrator, independent finite-path reference, AD verification, native/Wasm parity or experimental validation. No Atlas imports and no author code are used.

## Handoff

Public files are listed with relative paths/hashes in manifest.json. Private source material is not required to run the tests. Remaining decisions: source-origin stress initialization; objective-rate/frame scope; exact calibration and valid range; finite numerical support and stable normalized expm; derivative/zero-load policy; independent Cartesian rates followed by finite-path refinement and transaction tests. The immediate next implementation task is an explicitly named2015 fixed-frame nonzero-stress research variant with seven states and no IGS, using existing declarative operators after envelope review. Freeze an independent full-Cartesian reference before any compiled observations.

Source status: original interior equations and their locations inspected; boundary/frame/calibration decisions remain. Executable status: no model added. Numerical verification: bounded independent algebra only. Scientific/public admission: unchanged and not claimed.
