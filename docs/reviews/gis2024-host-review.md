> Archived AI technical review. Original temporary paths and code pins identify the reviewed snapshots; later fix sections supersede earlier findings. Current repository evidence is pinned in the corresponding investigation manifest. This is not human scientific admission.

# Independent bounded GIS HP host review

Reviewed 2026-10-31, read-only staged snapshot `/private/tmp/atlas-gis-hp-repo-20261031-v1`. No repository mutation, build, native execution, solver trajectory or model admission. Source PDF SHA256 `39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3`; printed/PDF pages 3,4,12 inspected visually, including enlarged Eq25. All six staged Python test groups pass against repository Python dependencies. The findings below are outside the retained moderate-state tests. Parent has acknowledged and plans guards/regeneration; this report reviews the original staged snapshot, not those unreviewed fixes.

## Source algebra supported

AppendixA p12 is extension/tension positive. With Atlas sigma=-sigma_source and stretching=-stretching_source, H=sigma/trace(sigma), Q,F,a,fs and L remain unchanged; N,B,Caux,G reverse sign. Eq25 has an explicit leading minus: gamma=-r*trace(B)/(G-r*trace(Caux))*fdA. Together with Eq30 this gives the **positive** Eq31 cross term, so norm(B+t*Caux)^2 with t=r*trace(B)/(G-r*trace(Caux)) is correct. No sign discrepancy found. The ratio t and Eq31 norm are invariant under simultaneous auxiliary sign reversal.

The p4 paragraph after Eq32 explicitly permits evaluating fdAstar by substituting sigmaA=sigma,eA=e in Eq31. It is not an independently solved true ASBS preparation state; the staged docs state this correctly. p3 Eqs8-12 give E=fsL, m=-B/||B||, C=||B||fdAstar, S=fd/fdAstar,f=0. Atlas m reverses source m. AppendixB B2's identity-plus-dyadic operator and the structured inverse are algebraically correct. Host HP reconstruction and GIS supplied-host compatibility are bounded algebra checks, not constitutive integration or evidence that GIS prevents finite-step overshoot.

The independent reference uses Cartesian tensor contractions, a dense Mandel action and pivoted elimination rather than the structured inverse, original source signs and the expanded Eq31 bracket. This is useful independence of contraction/inversion/sign implementation. It still shares the same source formulas and does not establish author-code equivalence, conditioning near singular Eq31, or experimental accuracy. These limitations are stated accurately.

## Blocker 1: positive density factor underflow silently accepted

`tools/inspect_gis2024_hp_host.py:50-56` checks positive p/F/fs and norms, but does not require fd>0. In the declared strict ed<e audit scope and alpha>0, fd is mathematically positive (AppendixB B10). The retained counterexample is a valid finite state within that selected scope: isotropic 100000 Pa; phi=34*pi/180,hs=111746000,n=.346,beta=2.2,ei0=1.000001,ec0=1,ed0=.5,alpha=30, e=nextafter(.5*exp(-(300000/hs)^n),+infinity)=.439512306119156. ed=.4395123061191559, fsden=5.514623196975682, fs=11976551.158714708. The host returns fd=0,S=0 and accepts. This silently erases the nonlinear rate despite strictly positive mathematical density factor. The docs line51 assertion about underflow rejection is too strong for this snapshot.

Minimal fix: require positivity of the mathematically positive factors/outputs in the selected open domain, including fd and S (and compression, limiting densities, Q,fdAstar,C where relevant), without clipping. Add this retained counterexample as a rejection test. This is a representability restriction/project numerical policy, not a source prohibition on the state. Some rejected states might be recoverable by scaled/log-domain arithmetic; rejection is honest within bounded scope.

## Blocker 2: exact isotropy and squared-norm underflow are conflated

JSON Hdev term currently uses `dev(H)` (lines78-82); docs line45 calls the zero-j2 branch exact. At spherical p=9247007.657539926 Pa,e=.7*compression=.3775062921449743, normalization produces Hii=.33333333333333337 and dev(H)ii=5.551115123125783e-17. Thus j2=9.244463733058732e-33, raw cos3theta=-1.414213562373095 and F=.9999999999999999. The raw Lode value is invalid for an actual trace-free nonzero deviator; the state is exactly spherical in input. The F error is tiny here, but the branch and raw invariant claims are wrong. The six existing test groups did not cover this pressure.

A separate state p=.1 Pa, Mandel shear1e-170,e=.7*compression=.6992427161350566 has nonzero Hdev shear3.333333333333333e-170, but squared j2 underflows to0; host silently selects the isotropic diagnostic cos3theta0/F1. For somewhat larger tiny shears it rejects division by zero when j2**1.5 underflows; the branch therefore has an unrecorded representability gap.

Minimal fix: stable algebraically equivalent deviator from stress before normalization, preserving raw exact isotropy; detect nonzero computed deviator with zero squared norm and reject rather than treat as exact isotropy; guard raw Lode to its mathematical [-1,1] domain with a declared limited roundoff allowance, not broad clipping. A double deviatoric projection is a numerical project choice and must be documented. Add both explicit regressions and ordinary axisymmetric/rotated cases. Root proposes this correction. I have not reviewed its implementation.

## Other scope constraints

Positive mean stress alone does not imply compressive principal stresses. The packet expressly excludes a tensile-eigenvalue filter and labels itself bounded algebra, not full physical admissibility; no additional source-backed SPD requirement was established in this review. Preserve this limitation before any model admission. The exact-zero Eq31 denominator guard is mathematically correct but insufficient to establish numerical reliability near singularity; docs correctly leave this unresolved and retained36 samples have only moderate denominator margins.

Typed-fragment validation checks metadata/units and identities, not an immutable expression inventory. That is adequate for this reviewed pinned fixture when manifest verification is external; it must not be presented as proof that any supplied dimensionally valid fragment preserves this particular source law. Keep manifest/dependency pins and rerun independent tests after any expression change. The Cartesian reference is an independent numerical oracle for the tested regular states, not a general validated input API.

## Reproduction

```sh
PYTHONPATH=/private/tmp/atlas-gis-hp-repo-20261031-v1:/Users/bmar5496/code/constitutive-atlas PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/atlas-gis-host-root-review-20261031-v1/reproduce_findings.py
PYTHONPATH=/private/tmp/atlas-gis-hp-repo-20261031-v1:/Users/bmar5496/code/constitutive-atlas PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s /private/tmp/atlas-gis-hp-repo-20261031-v1/tests -p test_gis_hp_host.py -v
```

`counterexamples.json` retains Python-only observations. `review-manifest.json` binds the source and inspected files, report and reproducer. No copyrighted source content is included. After the two blockers are fixed, regenerate retained diagnostics/manifest and rerun tests before treating this bounded algebra packet as ready; no full admission follows.

## Post-fix recheck: no remaining blocker for bounded algebra packet

I separately inspected `/private/tmp/atlas-gis-integrate-20261031-v1` after the parent corrections. Evaluator now checks positive Q,compression,ei/ec/ed,fd,fdAstar,C,S in addition to existing required factors, rejects nonisotropic input when computed j2==0, and checks raw Lode within 64 binary64 ulps of [-1,1] without clipping. JSON uses dev(dev(sigma))/trace(sigma), algebraically equivalent to the source deviator, documented as its numerical realization. No source formula/sign change was introduced. Exact-zero/near-singular denominator limitations remain explicit.

All three independent retained examples were replayed with this corrected overlay. fd underflow now raises ValidationError; spherical p=9247007.657539926 gives exact zero Hdev,j2 and F=1; nonzero squared-norm-underflow shear now raises ValidationError. All eight staged test groups pass under Python with the corrected overlay. `post-fix-counterexamples.json` retains these observations, and the review manifest binds both inspected snapshots. The post-fix assessment supersedes the earlier statements that the parent's corrections had not been reviewed.

No remaining blocker was identified for installing this explicitly bounded algebra fragment. This does not settle physical admissibility, near-singular Eq31 reliability, representable extreme states beyond rejection scope, author-code equivalence, finite integration or scientific admission. Regenerate/verify the repository evidence manifest against the final installed paths and contents before committing; my review hashes are of the staged files, and cannot cover later modifications.
