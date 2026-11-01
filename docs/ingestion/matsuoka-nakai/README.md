# Matsuoka–Nakai family: selected Nakai–Hinokio 2004 ingestion packet

Task ID: ING-matsuoka-nakai  
Owner / date: coordinating parent / 2026-11-01  
Scope: first source/formulation ingestion, including the full printed branch inventory. This packet selects **subloading tij, Nakai and Hinokio (2004)**. It does not equate a Matsuoka–Nakai failure criterion with an executable law. General source/algorithm reconciliation remains open.

## Identity and sources

Teruo Nakai and Masaya Hinokio, *A Simple Elastoplastic Model for Normally and Over Consolidated Soils with Unified Material Parameters*, **Soils and Foundations 44(2), 53–70 (2004)**. [DOI](https://doi.org/10.3208/sandf.44.2_53), [publisher record](https://www.jstage.jst.go.jp/article/sandf1995/44/2/44_2_53/_article), [original PDF](https://www.jstage.jst.go.jp/article/sandf1995/44/2/44_2_53/_pdf). Publication date April 15, 2004; received April 15, 2003. Title, authors and equation pages verified against the PDF images, not the abstract.

The selected formulation uses the modified stress/SMP concept associated with Matsuoka–Nakai, but adds elasticity, flow, density hardening and loading rules. Earlier tij-clay (1986), tij-sand (1989), the 1974 criterion, later structured/time-dependent extensions, and later implementations are distinct identities. The 2004 paper itself distinguishes its associated-only construction (Eqs 21–39), full path-dependent extension (Eqs 40–52), Appendix V option, and sand-specific split of parameter a (p65). A future executable identifier should be `nakai-hinokio-2004-subloading-tij-<selected-variant>`, rather than the undifferentiated candidate identifier.

Private receipt: `/private/tmp/atlas-nakai-hinokio-2004-source/original.pdf`, 1,870,619 bytes, SHA-256 `e2ed4ed2416d5ca65f7760a02ebe4913ea3610579ca6447397db6f03912c6395`, accessed 2026-11-01. This is temporary private storage, not a durable archive. All 18 pages (printed 53–70) were rendered with Poppler and inspected; page 69 was additionally rendered at 2500 pixels. Text extraction yields library watermarks only. No raw PDF/images are included in the repository. The publisher says free access and retains Japanese Geotechnical Society copyright; redistribution permission has not been established.

Downloads filename inventory found no matching Nakai/Hinokio/subloading/tij/44_2_53 source; repository catalogue/queue contained a candidate but no dedicated packet or equation audit. This is a bounded filename/content-index search, not a claim about every private file. Initial sandbox curl failed DNS (exit 6); the same public download succeeded with approved network access. Web PDF fetching also timed out; that did not prevent local acquisition. See [receipt](source-receipt.json).

## Existing work and gaps

The [catalogue manifest](../../../catalogue/manifest.json) lists `matsuoka-nakai` as candidate/non-executable and asks for a complete law. The [historical queue](../../../catalogue/research-queues/parallel-source-queue-2026-10-31.json) has only the selection gate. The [roadmap](../../../ROADMAP.md), [charter](../../RESEARCH_CHARTER.md), [status](../../STATUS.md) and live board were reviewed. This packet supplies the previously absent named law, original PDF receipt, full-paper equation/branch inventory, explicit v0.3 proposal and small independent checks. It does not change historical evidence or catalogue status.

## Equations and schema crosswalk

Target: [schema v0.3](../../../schemas/model-v0.3.schema.json) and [formulation contract](../../FORMULATION_CONTRACT.md). [crosswalk.json](crosswalk.json) contains `schema_version: "0.3"` and a complete explicit **proposed zero-spin small-strain host** formulation. It is a crosswalk, not a loadable model record. No legacy top-level `integration` is used. The paper supplies differential constitutive relations; a finite-increment residual or backward-Euler update is a further numerical choice. Neither has been silently selected here.

Notation below: colon is a full Cartesian tensor contraction; `I` is the identity; all source tensors are symmetric; positive principal effective stresses mean compression. `a_tensor` below means the paper's a_ij, while `a_par` means its density parameter. Both are denoted a in print. Stress units are Pa in a future record; paper examples use kPa. Strain and void ratio are dimensionless. Source Cartesian shear strains are tensor components; Mandel conversion multiplies off-diagonals by sqrt(2), not 2.

### Modified stress and yield geometry

For positive-definite effective stress sigma, let I1, I2, I3 be its three principal invariants; r=sqrt(sigma). The following equations are direct source relations or explicitly identified equivalent forms:

- **p54 Table 1; p55 Eqs 1–5; p69 A1–A6:** a_tensor = sqrt(I3/I2) sigma^(-1/2), a_i=sqrt(I3/(I2 sigma_i)); a_tensor:a_tensor=1; t=a_tensor sigma (coaxial product). Eq 1 also gives an invariant matrix expression through r and its invariants. General 3D orthogonal transformation A1–A4 and the planar angle construction A5–A6 describe the same tensor. Repeated positive eigenvalues are not a physical exclusion; the planar angle formula alone is undefined at a repeated in-plane pair.
- **Table 1:** tN=t:a_tensor, tdev=t-tN a_tensor, tS=sqrt(tdev:tdev), x=tdev/tN, X=tS/tN=sqrt(x:x); dεSMP*=dε:a_tensor and dγSMP*=norm(dε-dεSMP* a_tensor). Ordinary p=tr(sigma)/3, s=sigma-pI, q=sqrt(3 s:s/2), η=q/p, dεv=tr(dε), dεd=sqrt(2 dev(dε):dev(dε)/3). q in figures can carry a signed triaxial plotting convention; X here is a norm.
- **p70 A24–A25, equivalent invariants:** tN=3 I3/I2 and X=sqrt(I1 I2/(9 I3)-1). The latter loses accuracy near isotropy if evaluated literally; this packet does not prescribe that floating-point algorithm.
- **p56 Eqs 14–15, p58 Eqs 25–28:** ζ(X)=(X/Mstar)^β/β; f=ln(tN/tN0)+ζ-ln(tN1/tN0)=0. tN1=tN exp(ζ) is the current passing surface size. Normal size tN1e represents plastic volume: εvP=Cp ln(tN1e/tN0), Cp=(λ-κ)/(1+e0). Density index ρ=(λ-κ)ln(tN1e/tN1). Consequently f=ln(tN/tN0)+ζ-(εvP-ρ/(1+e0))/Cp. Logarithms must use dimensionless ratios; tN0 is a fixed reference pressure, not an extra loading input.
- **p56 Eqs 16–20; p69–70 A7–A11:** with R=Rcs, Xcs=sqrt(2)(sqrt(R)-1/sqrt(R))/3; Ycs=(1-sqrt(R))/(sqrt(2)(sqrt(R)+1/2)); Mstar=(Xcs^β+Xcs^(β-1)Ycs)^(1/β); Y=(Mstar^β-X^β)/X^(β-1). Eq 19 is the surface tangency relation tN dεSMP*+tS dγSMP*=0. Eq 20 must not be evaluated as a quotient at X=0.

**Source reconciliation item:** the intermediate triaxial strain-ratio expression A8 on p69 needs a separate literal algebra audit. This packet independently obtains Ycs from the Table 1 orthogonal projection and finds agreement with Eqs 18/A10; it does not certify every printed intermediate equality in A8. No amended equation is substituted for the source.

### Flow, density and elasticity

Use `m=∂f/∂t` for the paper's modified-space flow and `n=∂f/∂sigma` for ordinary-stress loading/consistency. These are different tensors. In particular, normality in modified stress is **not** ordinary-stress associated flow.

| Source locator | Relation / role | Mapping and qualification |
| --- | --- | --- |
| p55 Eqs 6–13 | Original Cam Clay comparison: f=ln(p/p1)+η/M; M=3(Rcs−1)/(Rcs+2); εvP=Cp ln(p1/p0); dεP=Λ∂f/∂sigma; Λ=df_sigma/hP; hP=tr(∂f/∂sigma)/Cp; loading on surface with positive df_sigma; p dεvP+q dεdP=0 and dεvP/dεdP=M−η | Context only; do not import its ordinary-stress normality into selected law. |
| p56–57 Eqs 21–24 | dεP=Λm; NC hP=tr(m)/Cp, Λ=(n:dσ)/hP; df=n:dσ−dεvP/Cp=0 | Associated-only NC predecessor of full extension. |
| p58–59 Eqs 29–34 | df=n:dσ−[dεvP−d(ρ/(1+e0))]/Cp=0; d(ρ/(1+e0))=ΛL; L=−G(ρ)/tN; G=a_par ρ²; hP=[tr(m)+G/tN]/Cp | Associated-only construction; ρ approaches NC during plastic deformation, but can increase during elastic unloading through the surface/density definition. Do not freeze ρ on all elastic steps. |
| p59 Eqs 33, 35–36; p70 A12–A16 | Λ=(n:D_el:dε)/(hP+n:D_el:m), loading based on strain-direction test n:D_el:dε; Macaulay activation in stress-controlled form | Captures hardening and softening; hP can vanish/change sign. Division by hP is not a safe universal strain-controlled algorithm. |
| p59 Eqs 37–39 | dεE=[(1+νe)dσ−νe tr(dσ)I]/Ee; Ee=3(1−2νe)(1+e0)p/κ; dε=dεE+dεP | Instantaneous isotropic stress-dependent elasticity. e0 is fixed reference void ratio in these equations, not automatically current e. |
| p60 Eqs 40–45 | At hydro tN1=tN=p and m=a_tensor/tN. Isotropic dεvP=[Cp/(1+G/tr(a_tensor))] dtN/tN. General IC share scales by tN/tN1=exp(−ζ), active for dtN>0. | Differential source equations, not finite log-update instructions. |
| p60 Eq 46 | dεP_IC=K I/3, K=[<dtN>/tN1]/[(1+G/tr(a_tensor))/Cp] | IC is ordinary isotropic compression, not flow along a_tensor. |
| p60 Eqs 47–49 | dεP_AF=A m; A=[n:dσ−<dtN>/tN1]/hP | May be negative on some hardening paths; Appendix V is a distinct treatment. |
| p60 Eqs 50–52; p61 Fig 12 | Elastic if Λ<0. Plastic hardening if Λ>=0 and hP>=0: dε=dεE+A m+K I/3. Plastic softening if Λ>=0 and hP<0: dε=dεE+(n:dσ/hP)m. | IC split is not applied indiscriminately to softening. Equality and hP=0 require a finite algorithm decision. |
| p61 Eqs 53–54 | Peak hP=0; m=[a_tensor+X^(β−2)(x−X²a_tensor)/Mstar^β]/tN | Critical peak/tensor expression; hydro must use an analytical continuation, not raw 0 times infinity. |
| p68 Eqs 55–56 | b=2tanθ/(sqrt(3)+tanθ)=(σ2−σ3)/(σ1−σ3) | True-triaxial test metadata, not evolution or a hydro b definition. |
| p70 A17–A25 | m=(1/tN)a_tensor+ζ'(X)(x−X²a_tensor)/(X tN), n=(1/tN)∂tN/∂sigma+ζ'(X)∂X/∂sigma | Source differentiation convention A20 treats a_tensor as fixed in the modified-space derivative. Do not differentiate a_tensor again inside m. n includes stress transformation through the invariants. |
| p70 A26–A28, Fig A2 | Optional region IV when AF becomes negative: dεP=ΛIC I/3 with ΛIC=(n:dσ)/[(1+G/tr(a_tensor))/Cp] | Fourth branch; source describes it as a method to avoid negative AF. Variant selection and branch consistency are explicit open implementation gates. |

The complete full-extension density relation is the compatibility equation in Eq 29 using **total** plastic volume, including IC/Appendix V contributions when selected. The associated-only evolution d(ρ/(1+e0))=−ΛG/tN is not automatically the full-extension update. The constant-reference small-strain void bookkeeping dεv=−de/(1+e0) is consistent with the linear e–ln(p) construction; exponential current-volume updates would be separate project discretization/kinematics choices.

### Parameters, state, preparation and domain

All of λ, κ, N, e0, νe, β, Rcs, a_par and ρ are dimensionless. tN0/reference pressure and stress are Pa. A stress-controlled Λ multiplying m has Pa units, since m has 1/Pa; plastic strain is dimensionless. A strain-rate formulation would use its path derivative, not store an unscaled strain as Λ. Proposed physical parameter conditions are λ>κ>0, −1<νe<1/2, e0>−1, Rcs>1, β>1 for the intended smooth hydro flow, a_par>=0, and positive radicand defining Mstar. These are inferred mathematical restrictions, **not published universal calibration bounds**. Paper examples β=1.5 and 2 do not justify a blanket C2 smoothness claim.

- **Fujinomori clay, p61 Table 2:** Cc=λ/(1+e0)=0.0508, Ce=κ/(1+e0)=0.0112, N=eNC at p=98 kPa and q=0 is 0.83, Rcs=3.5, νe=0.2, β=1.5, a_par=500. Cc is not Cp: Cp=Cc−Ce=0.0396. Do not treat Cc/Ce as λ/κ without e0. Reference-state choice and specimen preparation need the cited 1986 paper.
- **Toyoura sand, p64 Table 3 and p65 text:** λ=0.07, κ=0.0045, N=1.1 at 98 kPa/q=0, Rcs=3.2, νe=0.2, β=2, a_AF=30, a_IC=500. Unlike the one-a clay calibration, the authors deliberately use two a values in the two plastic components. A future implementation must select this named split and reconcile density compatibility, not silently use one coefficient. Sand NC parameters are fitted, not directly measured by an ordinary isotropic test.
- **Persistent state proposal:** effective sigma (six Mandel components), εvP (one scalar), ρ (one scalar). Derived tN1 and tN1e avoid redundant surface-size states. Accumulated plastic tensor/void ratio may be exposed for diagnostics but require consistent explicit initialization if retained; they are not necessary independent hardening variables. No fabric tensor, rotational-hardening memory, clock or intergranular-strain tensor occurs in this law. A multiplier is a temporary solve quantity, not persistent history. Appendix V ΛIC multiplies I/3 and has strain units, unlike Λ multiplying m.
- **Explicit initialization:** supply sigma, εvP, ρ plus reference e0/tN0 and parameters; enforce positive-definite sigma, ρ>=0 for the selected NC/OC domain, finite state and Eq 28. Equivalently supply consistent normal size tN1e>=tN expζ and derive εvP and ρ using Eqs 26–27 in a separately declared preparation recipe. This is a consistency recipe, not a published complete laboratory preparation algorithm. Do not infer ρ just from void ratio, OCR just from pressure, or all history from sigma. Unloading changes the passing subloading surface and the density index.
- **Domain:** strictly positive principal stresses for the literal inverse-square-root/log law, tN0>0, finite nonzero pressure. Zero/tensile stress needs a separate supported limiting/continuation policy. Positive repeated spectra and nonzero isotropy must be retained, not rejected to avoid numerical degeneracy. Physical applicability is narrower than arbitrary mathematical continuation.
- **Test preparations:** p63 Fig 18 uses OCR 1/2/4/8; OCR8 tests at p=98 kPa, others at 196 kPa. p64 describes saturated dense sand deposition/rod compaction versus loose underwater deposition; approximate initial e=0.68/0.92 precedes isotropic consolidation. Figures 23/24 give individual e196 values; those differ by path and are not interchangeable universal states. No arrays were digitized and no specimen-specific history was invented.

### Formulation and capability decisions

The differential source is strain-path dependent, not physical-time dependent (p68 explicitly excludes time/age effects). Its effective-stress interpretation is supported by the saturated-soil context and p66 effective-stress axes. The proposed fixed-spatial, zero-spin, infinitesimal 3D Cauchy host is a **bounded Atlas approximation**, not a source-defined objective finite-deformation update. Tensor rotation tests of instantaneous algebra do not supply a spin transport law. The explicit crosswalk records those decisions and initialization semantics separately.

Existing scalar/tensor expressions and 32-component capacity do not appear to be the main obstacle. However, full noncoaxial tensor a(sigma), including repeated spectra and first derivatives, needs a generic demonstrable inverse-square-root/matrix-function construction (or equivalent invariant construction from Eq 1). Existing eigenprojector primitives do not by themselves certify a repeated-spectrum differentiable tensor function. The X=0 continuation for β=1.5 needs value/derivative policy, as do hP=0, loading equality, AF/IC transitions and optional region IV. This packet requests a **capability feasibility study**, not an immediate shared compiler change. First settle the source and finite-integration decisions.

## Temporal integration and transactions

These are homogeneous differential stress/strain relations with path-dependent branches. A mechanical hold gives zero rates in the regular nonsingular domain, with no autonomous creep or aging; this does not excuse evaluating undefined 0/0 terms at hP=0 or X=0. No physical duration, rate history, temperature, pore-pressure evolution or hydraulic solver is supplied. Effective stress control and undrained constraints belong to a separately specified host.

The source gives stress-controlled differentials and associated-only strain-controlled conversion (Eq 33/A16), but no complete full-extension finite-step strain-driven algorithm, error controller, return mapping, consistent update tangent, or trial/commit/rollback API. Old/new staging of pressure-dependent Ee, surface and density values is not a stated backward-Euler rule. Substepping is a numerical choice. One cannot label the printed dε relation a finite residual without selecting and naming that discretization.

Proposed future host requirements: each trial starts from an immutable full parent state; solve stress and branch-coupled density consistently; stage all derived quantities at declared values; commit all persistent state only after acceptance; reject/rollback all state on failure including late internal failures; replay/reset restores supplied history; outer mixed-control retries never accumulate trial history. No parent-increment reversal reset is present in the source. Loading direction and hardening/softening crossings are local events, not permission to erase ρ. All are **requirements for later implementation**, not behavior verified here.

A full tangent must differentiate both n and modified-space m, elasticity, hardening and the selected active flow split. It is generally non-associated in sigma space; ordinary-stress symmetry cannot be assumed. Branch-boundary and hydro differentiability require explicit guarantees separate from a regular-branch residual Jacobian. Peak singularities under stress control require analysis before any numerical regularization or restriction is chosen.

## Independent checks

Run from the repository root:

```sh
python3 docs/ingestion/matsuoka-nakai/check_algebra.py
python3 docs/ingestion/matsuoka-nakai/verify_packet.py
```

[check_algebra.py](check_algebra.py) imports only the Python standard library and implements direct principal/Cartesian algebra independently of Atlas. Nine groups pass: Table 1/invariant identities in four states, finite hydro limit, clay/sand critical-state projection, three pressure scales, a non-diagonal Cartesian rotation, ordinary-stress gradient finite differences and Euler homogeneity, distinction of n from m, NC/density hardening identities, flow-boundary algebra and positive-principal-domain witnesses. Criteria were fixed in the script before execution: algebra 2e−12 times max(1, magnitudes); finite-difference derivative 3e−7 on the same scale. Derivative tolerance is a bounded sanity check, not a high-precision derivative certificate.

The initial check failed because the draft oracle used the wrong principal components in a simplified Ycs denominator (`−0.318158680283498` versus `−0.2597272742916145`). It was replaced by the actual Table 1 projection of `(1,−1/2,−1/2)` onto a_tensor and its orthogonal complement. No tolerance or source equation changed. This failure and correction are retained in [check-history.json](check-history.json). That corrected check supports Eqs 18/A10, not the unresolved printed A8 intermediate equalities. No paper benchmark, numerical stress update, complete branch selection, scientific signoff, native or Wasm check was run.

## Handoff

Exact files: `README.md`, `source-receipt.json`, `crosswalk.json`, `check_algebra.py`, `check-results.json`, `check-history.json`, `verify_packet.py`, `manifest.json` in this directory. The verifier checks their exact hashes, the proposed formulation/initialization structures against the current schema fragments, and deterministic replay of the saved algebra result. Optional `--source` also checks private PDF bytes. The optional `jsonschema` package is absent; verification uses a strict keyword subset for these fragments and rejects unknown keywords, rather than claiming whole-model JSON Schema validation. Its first run rejected `minLength`; support was added explicitly and that failure is retained in `check-history.json`. No raw PDF or vendor code is redistributed or executed. No unrelated file is staged, committed, built or deployed.

- **Source completeness:** original full paper acquired and all pages visually read; complete bounded equation/branch inventory provided. A8 literal equality audit, full-extension density staging, two-a sand reconciliation and external clay preparation references remain unresolved. This is not a source-complete runnable record.
- **Executable status:** none added. Crosswalk is a proposal; no canonical model, compiler or schema was changed.
- **Numerical verification:** nine standalone algebra groups only; finite paths, all active-branch tangents and transaction checks remain open.
- **Scientific admission:** pending/unassessed; no new evidence of predictive accuracy or independent scientific review.

Smallest next action: select the clay one-a full extension with either the printed negative-AF allowance or the explicitly named Appendix V alternative, audit A8 against Table 1, and freeze a regular-state independent strain-controlled reference/branch policy. Then assess a repeated-spectrum-safe generic stress transformation and hydro continuation before a distinct v0.3 research transcription. Do not begin by adding the failure criterion alone, changing the parameter domain after failures, or substituting a handwritten model kernel. The full ING task stays WIP until those source/algorithm gates are resolved; the board separately records this bounded inventory handoff.
