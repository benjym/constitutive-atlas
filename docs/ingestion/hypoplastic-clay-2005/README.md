# hypoplastic-clay-2005 - ingestion packet

Task ID: ING-hypoplastic-clay-2005
Owner / date: review_vw96 / 2026-10-31
Scope: original isotropic five-parameter Mašín 2005 base model; source/schema/integration handoff, with bounded independent algebra checks. No executable definition or admission is added.

## Identity and sources

The selected model is David Mašín, *A hypoplastic constitutive model for clays*, International Journal for Numerical and Analytical Methods in Geomechanics 29(4), 311-336 (2005), [DOI](https://doi.org/10.1002/nag.416). The [primary university author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf) is an accepted preprint, 26 pages, SHA-256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`. Its footer copyright 2004 does not change the publication identity. All main locators below use manuscript printed page = PDF page, not journal pagination. The [author bibliography](https://web.natur.cuni.cz/uhigug/masin/bib/DMbib.htm) warns that preprints can differ from final typesetting/proofreading. Final-publisher reconciliation remains a gate.

The separate companion is Mašín and Herle, *State boundary surface of a hypoplastic model for clays*, Computers and Geotechnics 32(6), 400-410 (2005), [DOI](https://doi.org/10.1016/j.compgeo.2005.09.001), [accepted author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/MH_CaG05-pp.pdf), SHA-256 `549e337e39505ba2757da6f4ab95a00c702d08952fbd9e2c48c8022be2e4189a`. It has a cover: printed page k = PDF page k+1. Its swept-out-memory (SOM) surface is not an exact state boundary surface (SBS).

The user's Downloads and existing source inventories were searched first; no identifiable original 2005 copy was located there. Private PDFs, renders, text extraction and author code remain outside the packet. [source-receipt.json](source-receipt.json) pins bytes, URLs, local private paths, visual locators and the separate legacy implementation. No blanket redistribution permission was established for either paper.

## Existing work and gaps

The [2013/2014 source dossier](../../reviews/clay-2013-2014-source-packet.md) concerns later models. The 2005 stiffness uses **r = initial Ki/Gi**, not the later Poisson-like parameter nu. The 2013 explicitly-defined-asymptotic-state formulation and 2014 anisotropy coefficients must not be backfilled here. Main Appendix A is the **reference HK model**, not this selected model; Appendix C is the selected complete base formulation. Main Appendix B is an optional Niemunis-Herle intergranular-strain extension, not ISA or GIS.

This packet newly pins the original main and SOM companion and identifies a source inconsistency: main p10 **Eq38 prints Q - f_di*a*sqrt(3)** for unloading, but substituting positive e_dot into p9 Eq30 requires a plus, as printed in subsequent **Eq40**, and as used to derive Eq41. The packet records both. The algebra checks use Appendix C plus Eq40/41; they do not silently repair Eq38 or declare it reviewed. Comparison with the final publisher equation and independent review remain required.

## Equations and schema crosswalk

[contract.json](contract.json) is a non-executable equation/operation inventory, not an Atlas model-schema instance. Stress and elasticity are genuinely 3D tensor laws; triaxial calibration does not justify a triaxial-only implementation.

| Source locator | Equation / quantity | Schema representation / units | Status / ambiguity |
| --- | --- | --- | --- |
| Main p2; p3 Eqs1-4; p24 Eqs73-74 | T° = fs[L:D - fd*Y*(L:m_unit)*norm(D)] | Coupled objective stress-rate; effective T negative in compression | Jaumann; no independent elastic/plastic split |
| Main p7 Eqs15-16; p24 Eqs75-77 | L:X = 3[c1*X+c2*a^2*hatT*(hatT:X)]; hatT=T/trT | Fourth-order action via tensor and dyadic contractions; L dimensionless | F does **not** multiply L here |
| Main p7-8 Eqs17-20; p24 Eqs78-79 | I1=trT, I2=(T:T-I1^2)/2, I3=detT; Y from stress ratio | Scalar invariants; I2 is negative of the usual second principal invariant | MN f=0 has Y=1; this is not a yield-return rule |
| Main p8 Eqs22-24; pp24-25 Eqs80-82 | m, F, tan(psi), cos(3theta) | Tensor flow direction plus invariants, norm, sqrt and division | Eq80 multiplies hatT/3, **not I/3**; F denominator 2+sqrt(2)*tan(psi)*cos(3theta) |
| Main pp9-10 Eqs25,33-35; p25 Eq83 | pe=pr*exp((N-ln(1+e))/lambda); pcr=pe/2; fd=(2p/pe)^alpha | Density-derived pressures, not extra history; pr=1000 Pa | Log must use dimensionless p/pr; N changes with reference units |
| Main p9 Eq32; p25 Eq83 | fs=3p/[lambda*(3+a^2-2^alpha*a*sqrt(3))] | Positive pressure-valued stiffness scale | No void dependence in fs |
| Main pp10-11 Eqs41-45; p25 Eqs84-85 | alpha, c1, c2 from five parameters | Recomputed derived coefficients, no independent calibration | Eq38 vs Eq40 unloading conflict retained |
| Companion p9 Eq25 (PDF10) | e_dot=(1+e)*trD | One dimensionless evolving state; incompressible grains | General continuity; main Eq26 is NCL-only and cannot replace it |
| Companion pp8-10 Eqs21-36 (PDF9-11) | Tn=T/pe; A=fs*L+T tensor I/lambda; fd_SOM=1/norm(A^-1:(fs*N)) | Optional diagnostic linear solve, no constitutive return map | Here N=-Y*(L:m_unit); fs is absorbed into companion L,N |
| Companion pp12-14 Sec6, Figs7-9 (PDF13-15) | SOM generally differs from SBS; outside-SOM trajectories exist | Diagnostic metadata, no universal initial inequality | A inverse can fail; companion Appendix B pp19-20 Eqs60-66 |
| Main pp23-24 Eqs68-72 | Optional delta tensor, rho, direction and IGS branches | Separate 13-state/10-parameter extension | Not included in seven-state base; explicit source delta=0 branch exists |

Five material parameters: phi_c (radians in API; main Table I uses degrees), lambda_star, kappa_star, N and r (dimensionless). Source Table I p17 gives London-clay basic values 22.6 degrees, 0.11, 0.016, 1.375, 0.4. These are source calibration values, not defaults for every clay. Reference pressure is exactly 1 kPa = 1000 Pa. A solver pressure scale is numerical metadata, not a sixth source material parameter.

For Atlas use sigma=-T and E=-D, positive in compression, with sigma and E symmetric. Define m by the printed **source** formula (spherical negative at isotropy). Then sigma°=fs[L:E + fd*Y*(L:m_unit)*norm(E)] and e_dot=-(1+e)*trE. Do not also negate m without reversing the nonlinear sign. State is `[sigma_xx,sigma_yy,sigma_zz,sqrt(2)*sigma_xy,sqrt(2)*sigma_yz,sqrt(2)*sigma_xz,e]`; E has the corresponding six-component Mandel order. Dot products equal Cartesian tensor contractions. No pc, OCR, sensitivity, integration counter or total strain is constitutive base history.

At exact isotropy F=1 and m=-a/(3+a^2)*I, so m_unit=-I/sqrt(3). cos(3theta) is undefined there; use the derived spherical limit rather than evaluate 0/0. Near-isotropic cancellation, determinant ratios and roundoff in the Lode invariant need a separately reviewed numerical policy. No broad clipping is prescribed.

### Initialization and domain

Require explicit effective sigma0 and e0 and all five source parameters. Isotropic NCL initialization is e0=exp[N-lambda*ln(p0/pr)]-1, p0>0. A specified e0 instead determines pe0 and pcr0; it must not overwrite the stress or introduce a hidden preparation path. Overconsolidated or anisotropic starts need explicit state/preparation provenance; no source universal initialization procedure is inferred. The companion's SOM surface cannot be imposed as an exact SBS. States outside SOM are not automatically invalid. Main p16 Sec5.3 restricts this base model to reconstituted clays/natural clays with stable structure; destructuration is a different variant.

A proposed bounded research implementation would check finite inputs, 0<phi_c<pi/2, lambda>kappa>0, r>0, alpha>0, positive finite derived scales, strict positive-definite sigma, e>=0 and finite nonzero denominators. These are explicit project support restrictions, not a proof of the full physical domain. Source fd properties on p9 support positive alpha; lambda>kappa alone does not ensure it. Check L positive definiteness using c1>0 and c1+c2*a^2*(hatT:hatT)>0; do not require c2>0 unnecessarily. Main Eq17 is the MN critical-state condition, not an unconditional ban on dry-side peak stress ratios. Companion p17 gives **rough** guidance kappa<lambda/4 and calls for more precise SOM/invertibility inspection, not a universal theorem.

The source physically bounds void ratio below by zero; the differential law itself need not prevent e crossing zero during an arbitrary path. Reject a transaction that leaves declared support; do not clip e. e0=0 with compressive volumetric input has an immediate outward rate and needs an explicit API boundary policy before implementation. Singular A prevents an optional SOM diagnostic but need not make the base stress-rate law singular.

## Temporal integration and transactions

This base model is rate independent and positively homogeneous for a positive rescaling of D (companion Sec3 Eqs4-6). It needs ordered strain-path increments, not a physical frequency or time unit. During one smooth segment all seven state components must be recomputed together at every integration stage; fd, Y, m, L and fs are current-stage quantities. Reversal changes the direction but not a persistent loading flag. There is no elastic yield activation, hardening return map, reset or event in the base equations. At E=0 all seven rates are zero; in a rotating frame, stress still requires the prescribed objective spin treatment. Initial implementation should explicitly declare zero spin, or provide a separately validated corotational contract. A finite strain total-deformation interface is not established by this packet.

Trial/commit/rollback and failure budgets are project API semantics, unspecified in the 2005 article. Proposed common-engine contract: immutable committed seven-state input; trial stages isolated; accept only finite supported states at every stage and final state; commit all seven together; on invalid state/budget exhaustion return the exact original state, no partial history. Reversal/caller partitions carry the generated parent state and never reinitialize density from NCL. Separate numerical counters and step-size hints from constitutive history. No static hold aging/creep is predicted. The norm term makes a unique stress-rate derivative at E=0 generally unavailable; zero-direction AD/tangent claims need a directional convention.

The [legacy implementation's integration documentation](https://web.natur.cuni.cz/uhigug/masin/umat/node10.html), dated 2011-02-07, describes explicit adaptive RK2/3 with local substepping and asks the FE host to reject/reduce the global step at a minimum step or maximum substep limit. This is later implementation evidence, not a 2005 article-mandated method or proof that today's common solver matches it. Its [state/parameter documentation](https://web.natur.cuni.cz/uhigug/masin/umat/node13.html) includes optional IGS/structure and implementation diagnostics; its eleven UMAT state slots are not the minimal base state. The pinned 2007-copyright archive contains GPL-2.0-or-later source plus object files; none were executed, compiled or redistributed. The separate acknowledgement sentence in its header warrants license review before reuse.

For the optional original IGS extension only: source delta_hat=0 at delta=0; rho=norm(delta)/R; branch test delta_hat:D>0; delta°=(I4-rho^beta_r delta_hat tensor delta_hat):D on that branch and D otherwise. It needs supplied full tensor history, objective transport and a declared norm-radius integration policy. Source Eq71 stiffness interpolation, not the base nonlinear equation, must be used. A zero-history declaration is a specific preparation choice, not universal. This packet does not implement or merge that extension with ISA/GIS.

## Independent checks

Run from this directory:

```sh
python3 check_packet.py --output checks.json
python3 -m unittest -v test_packet.py
```

The retained result contains 40 passing checks; all six unittest groups pass. Checks use only stdlib, the supplied source equations and derived isotropic identities. They test coefficient closure, Ki/Gi=r, all-shear Mandel conversion, F/m spherical limit, finite NCL compression, local NCL unloading, density/reference-pressure conversion, isotropic SOM consistency and the strict distinction between unloading tangent and a global kappa line. They also demonstrate a parameter set satisfying lambda>kappa but violating alpha>0. No author code, Atlas interpreter, native or Wasm computation is used. These are bounded algebra/analytic diagnostics, not independent verification of the full nonisotropic stress kernel, experimental validation or source review completion.

## Handoff

The local [manifest.json](manifest.json) lists only authored files with exact hashes; its own hash is supplied separately. Source receipt is replayable by optional `--main-source` and `--som-source` arguments, without shipping PDFs. Seven-state base equation inventory is available; final-publisher Eq38 reconciliation, independent nonisotropic Cartesian oracle, cancellation-aware branches/domain policy, common-schema draft review, objective rotation, coupled finite-path convergence/transactions and experimental studies remain gates. No existing candidate/model status is changed. Smallest next task: freeze a research-only seven-rate declarative definition and independent Cartesian action oracle for Appendix C, explicitly identifying the Eq38 conflict and using source Table I plus isotropic/sign/rotation witnesses; only then commission a bounded compiled study.
