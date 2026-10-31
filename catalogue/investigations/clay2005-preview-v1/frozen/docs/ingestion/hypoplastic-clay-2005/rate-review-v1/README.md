# Clay2005 rate draft — independent audit v1

Task AUDIT-clay2005-rate. Owner review_igs97,2026-10-31. Read-only audit of the frozen [rate-study-v1](../rate-study-v1/README.md); no numerical model, admission or historical bytes changed. **Two blockers remain before a compiled rate study: a false source-discrepancy statement and an unsafe numerical SPD guard.**

## 1. Additive correction: the pinned Eq38 has a plus sign

The exact accepted manuscript [Mašín2005 source](https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf), [DOI](https://doi.org/10.1002/nag.416), is718767bytes, SHA256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`. Its printed/PDF page10 Eq38 visibly reads the unloading bracket **Q + f_di*a*sqrt(3)**, not minus. Eq40's corresponding plus numerator and Appendix C are consistent with that sign. This corrects the prior packet's interpretation; it is not a publisher typo correction or a new mathematical variant. Final-publisher equivalence is still unverified, but the stated conflict is not established within the pinned manuscript.

Visual verification used the PDF skill, full page10 at1800and3000pixel height, then a288dpi direct PDF-render crop. Page size595×842pt, top-origin equation crop bbox[170,460,510,510]pt. The disputed **plus** has bbox[326.279970,483.308020,334.070754,493.270660]pt from an independent pdftotext-bbox extraction; the rendered sign is unambiguous. Private crop path is `/private/tmp/atlas-clay2005-rate-review-20261031/private/eq38-crop-10.png`. No copyrighted crop, page or extracted source text is delivered in the public whitelist. Optional private reproduction:

```sh
pdftoppm -f 10 -l 10 -r 288 -x 680 -y 1840 -W 1360 -H 200 -png /private/path/masin-2005-author.pdf /private/tmp/eq38-crop
```

Affected frozen statements, whose original hashes are retained in [reviewed-inputs.json](reviewed-inputs.json):

- Parent source-receipt.json lines178–189 (`conflicts`, especially line182); parent README.md lines19,33,76; parent contract.json's publisherEq38 gate; parent manifest.json's conflict gate.
- Parent check_packet.py lines102–103 and the corresponding checks.json row: the alleged source-minus slope is a **counterfactual synthetic expression**, not a measurement of the printed source. Passing that test establishes only that1/lambda differs from1/kappa.
- rate-study-v1/README.md lines5,72; model.json description line6 and source locator line11; reference.py line128 and reference.json source_selection; the rate manifest's reconciliation gate.

Preserve these records as historical extraction error. Attach this additive correction in the live index and carry corrected provenance into a separately named revision. No instantaneous rate equation needs to change because the current rates already use the source-consistent plus sign.

The accompanying algebra computes `(Q+2**alpha*a*sqrt3)/(lambda*Delta)=1/kappa` and its counterfactual minus counterpart `=1/lambda` at default parameters. This supports interpretation after visual reading; it does not automate proof of a printed glyph.

## 2. Numerical SPD guard accepts an indefinite stress

The invariant identities themselves are correct in exact arithmetic. The problem is using their cancelled determinant as an unqualified floating-point positivity certificate. rate-study-v1/model.json derived `detH=1/27-j2/6+j3/3`, together with `pairH>0`, `detH>0` and positive mean stress, is not a reliable binary64 guard near rank loss. The same determinant also appears in Y's denominator (model.json lines172–173).

A minimal exact-input witness, with default parameters:

```
sigma6 = [1,1,-1e-20,0,0,0] Pa
e = .8
E6 = [.001,0,0,0,0,0]
```

The stress is diagonal and has a strictly negative third eigenvalue; its determinant is the actual binary64 negative number represented by-1e-20. Nevertheless `prepare_increment` and `evaluation_environment` accept it. Computed detH is `1.734723475976807e-18`, Y is `6.712477032916275e16`, and a finite but unsupported seven-rate result is produced. The exact normalized determinant is negative; its90digit Decimal value is retained. The rank-loss case `[1,1,0,0,0,0]` is also accepted with that positive computed determinant. The independent Cartesian oracle rejects both at reference.py lines59–60.

[probe.py](probe.py) reproduces both against the hash-pinned current draft and retains the input, rates, invariant values, actual diagonal determinant, exact-input normalized determinant, oracle rejection and unchanged parent in [evidence.json](evidence.json). These are defect witnesses, not source-calibrated states or accepted numerical results.

Smallest useful fix: a **new revision** with a declared conservative normalized Cartesian/Mandel Sylvester interior, independently checking diagonal positivity and leading minors with an explicit roundoff margin, separate from the rate's algebraic invariant evaluation. The probe demonstrates a prospective all-three-diagonals/leading2minor/determinant64epsilon interior rejects these witnesses while admitting all41old comparison inputs. This is an illustrative support restriction, not a certified SPD theorem or proof for arbitrary near-singular rotations. Add tiny positive/zero/negative diagonal and oblique rotated rank-loss adversaries to the new corpus; review arithmetic and margins before compiled observations. Do not silently install the illustrative helper as a scientific admission policy or rewrite old frozen files.

## Verified mathematics and bounded limitations

Visually inspected Appendix C pages24–25 Eqs73–85, plus p10 Eqs38–41. The source N=-Y L:m_unit and T=-sigma,D=-E give `sigma°=fs*(L:E+fd*Y*(L:m_unit)*norm(E))`: retaining the negative spherical source direction m is correct. The draft's plus nonlinear term, H/3 in m, factor2 in fd, sqrt2 in F, normalized H, and all six Mandel component positions match this selected source. The Cartesian oracle explicitly contracts81fourth-order entries and uses its own cofactor invariant route; it does not call the DSL.

Derivation checked: with traceH=1, Hdev=a, j2=a:a,j3=tr(a³), detH=1/27-j2/6+j3/3 and `(I1*I2+9I3)/I3=(-j2+3j3)/detH` using the source's negative second-invariant convention. Thus the DSL Y rewrite is sign-correct; the determinant's positivity test is the separate numerical failure above.

At exact sphere, F=1,Y=Yi,m=-a/(3+a²)I are the correct limits. The double-deviator projection and independently tested exact-component sphere residual prevent the tiny-shear norm-underflow cases from being relabeled an accepted sphere in the checked witnesses. The declared nonzero-j2 floor and64ulp raw-Lode allowance are support decisions, not clipping or source material constants. The packet candidly limits accuracy evidence to exact spheres and its41comparison cases with nonisotropic j2>=1e-8. High-precision near-isotropic accuracy remains unresolved; this audit does not extend its certification range. No finite integration, AD, spatial spin, initialization or physical SBS admissibility is established by instantaneous comparisons.

## Reproduction and scope

From the installed review directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 probe.py --check evidence.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_audit
```

For staging, add `--repo /path/to/constitutive-atlas` to the probe and set `ATLAS_REPO=/path/to/constitutive-atlas` for unittest. Reviewed input hashes are checked before execution; a changed historical file is an intentional audit replay failure. The review does not require the private PDF for numerical replay. Four audit groups pass; both defects reproduce; all41existing corpus inputs lie inside the illustrative conservative guard. Only bounded Python and private PDF inspection ran. No C++/Wasm builds, binaries, source programs or shared edits occurred. Scientific/public admission remains unchanged.
