# VIBE2026 — complete explicit Appendix A source packet

Task SRC-vibe2026-original-v2; owner /root/vibe_source; 3November2026. This is a new source identity. All source-v1 bytes, failed acquisition receipts, private archive and previous gap reports remain unchanged. Scope: source acquisition/transcription/reconciliation only, with isolated algebra checks. No author code, native/Wasm artifact or production material model was executed; no shared implementation, approval or live delivery is claimed.

**The exact final original has now been acquired and its complete Appendix inventoried.** The proposed exact model identity is **Mašín2026 VIBE, published explicit Appendix A formulation**, with the tensor-rank completions justified below. This selects all A.1–A.35, including full mechanical, hydraulic, thermal and viscous terms; it does not replace VIBE with a mechanical or rate-independent reduction. It also does not claim equivalence to the body Eq.(27) for opposing simultaneous internal hydraulic/thermal contributions.

## Source receipt, scope and identity

D.Mašín, *Viscohypoplastic bentonite (VIBE) model*, Engineering Geology370 (2026),108827. [Persistent DOI](https://doi.org/10.1016/j.enggeo.2026.108827).18PDF pages. Received28June2025, revised10April2026, accepted13May2026, available online21May2026. Version of record title/DOI and Appendix visually verified. Copyright©2026TheAuthor, CC BY4.0 declaration on p1. Source receipt: [source-receipt.json](source-receipt.json).

User original `/Users/bmar5496/Downloads/1-s2.0-S0013795226002863-main.pdf`; private exact copy `.local/private-sources/vibe-2026/original-v2/vibe-2026-vor.pdf`, SHA256 **90b1c3bc56bacf1294e3e8ea60a217ffa1651981c86c63b0c0d9354534764912**. Original supplied3November2026; download origin is user-provided, not an asserted successful agent network retrieval. Read all18pages; visually inspected pp4–5 Tables1–3, pp12–13 derivation and pp15–16 Appendix. Render/text hashes and paths are in the receipt. No PDF copied to the public packet.

The final paper is now sufficient to transcribe the explicit continuous law without importing missing equations from older dependencies. Earlier 2013/2017 author manuscripts remain useful lineage; their water-retention/microvoid/thermal equations are distinct. The user archive's updated C++ class is implementation evidence, not the selected mathematical identity. Its SANISAND umat, _2017/_2022 subclasses and ordinary driver numerical safeguards remain separate. See source-v1 for their exact retained original hashes and rights. Paper permission does not imply an entire mixed-source archive licence.

## Complete equations and parameter crosswalk

[equations.json](equations.json) transcribes **every A.1–A.35** in compact named tensor notation, source-negative tensor convention. The page map is exact: A1–A12 p15; A13–A35 p16. This is a source equation inventory, not an executable Atlas JSON; it deliberately declares no fabricated schema compatibility. [parameters.json](parameters.json) contains every Table1 material parameter (22) and Table2 hidden constant (7), calibrated BCV numbers, SI conversions and proposed explicit starting context. The paper supplies values, not universal material parameter bounds.

| Source locator | Quantity | Representation / units | Source resolution |
| --- | --- | --- | --- |
| p15 notation, A1 | Net stress rate | symmetric stress6,Pa/s | Net is neither effective nor total stress; source tensor compression negative. |
| p4Table1,p15 | Physical time | seconds; strain rate1/s, suctionPa/ratePa/s,TK/rateK/s | Rate-dependent holds matter; no strain-path relabelling. |
| p5Table3,p15opening,A15 | e,a_scan | persistent scalar2,dimensionless | Only two internal memories; six stresses plus these give eight constitutive ODE components. |
| A16–17,A22–35 | em,eM,S_M,Sr,re,eA,operators | current-context derived algebra | No independently integrated saturation/porosity memory or DAE is needed for the paper formulation. |
| A14,A22 | sigmaM=sigmaNet−S_M s I; pm=−tr(sigmaNet)/3+s | macro/micro effective pressures | Suction s=ua−uw; fluid/gas compression positive. |
| A1–10 | Explicit net rate | operators from rank-one B inverse | No per-call microstructural nonlinear iteration or arbitrary matrix inverse is needed. |
| A11–14,A23–35 | Host stiffness/asymptotic state/collapse | scalar+symmetric tensor invariants, products,dyadics | Pressure/log/fractional-power/normalized-direction domains remain explicit. |
| A15,A18,A25–26 | Hysteresis | scalar branch-sensitive rate | Positive/negative suction direction matters. No reset or clipping appears in these equations. |
| A17,A20 | Microvoid | scalar algebra from current stress,s,T | Independent from thermal microstrain coefficient alpha_s; currentT required. |
| p13Eq49 | Approximate linear tangent blocks | LB,HLsB,HLTB | Paper explicitly says these do not deliver quadratic Newton convergence. They are not a consistent full integration tangent. |

A dot means derivative per physical second (p15). Source compression-negative tensor stress/strain; positive mean pressure p=−tr(sigma)/3; positive fluid/gas pressures; net sigmaNet=sigmaTotal+uaI. Source suction s=ua−uw is positive for unsaturated drying. Paper does not prescribe a Mandel encoding; use explicit passive tensor encoding `[xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz]` in an Atlas implementation, never engineering shear. Source defines the Euclidean tensor norm, which equals the Mandel6norm.

For a compression-positive Atlas representation, `Sigma=-sigmaNet`, `E_dot=-D`. Scalar s,T,e,a_scan are unchanged. Compute the source-negative full RHS at source tensors and return `Sigma_dot=-rhs`. Then e_dot=−(1+e)trace(E_dot); scalar a_scan_dot is unchanged. Transform total stress as `SigmaTotal=SigmaNet+uaI` only when an explicit pore-air pressure is supplied; do not silently equate net and total. Macro effective compression-positive tensor is `SigmaM=SigmaNet+S_M s I`.

The Appendix does not supply a finite-step spin/objective transport algorithm. A proposed small-strain, fixed spatial, zero-spin host is an explicit bounded Atlas kinematic restriction, not proof of finite-rotation objectivity. Ordinary effective-only laboratory controls cannot accept net stress by name substitution.

## Persistent state, controls, preparation and parameter units

Exact persistent constitutive vector: `(sigmaNet6,e,a_scan)`;8components. The external committed context additionally retains current time, suction, temperature, complete loading controls and parameters. For full6strain-controlled THM, supply strain-rate tensor plus stage `s`, `s_dot`, `T`, `T_dot`, and physical time. Initialization explicitly supplies stress6,e,a_scan,s,T,time and initial mechanical rate if required by the transport. Reconstruct all derived values in dependency order: pm→em→eM→sen,se→S_M,Sr→macro stress→invariants/density/ASBS→operators. No stale previous saturation may stand in for current algebra.

Paper p4 and p15: e=rho_s/rho_d−1. BCV solid density2760kg/m³; selected rho_d1600 gives e=.725. a_scan0 represents a powder-compacted wetting branch;1is drying; intermediate values scanning. Paper uses rho_w1150kg/m³ for gravimetric water content `wc=e*Sr*rho_w/rho_s`; this is a paper data-processing choice, not automatic hydraulic flow/density evolution. Thermal/hydraulic transport coefficients and field conservation equations are external to the local law (p4 refers to Simo2026).

Important SI conversions: hms150000kPa→150MPa; se02000kPa→2MPa; pr1kPa→1000Pa; Dr0.5in10^-6s^-1→5e-7s^-1; phi25degrees must be converted to radians for trigonometric functions. Tr294K is a hidden constant. The supplied old driver makes Tr an input but the final paper lists it as hidden. N remains1.43 only if the explicit pr=1000Pa is retained in all logarithms/exponentials; silently making pr1Pa changes the material.

Table1 prints dash units for a,b,IvT. For a dimensionally checked implementation, a is dimensionless and b inK^-1 makes a+bT dimensionless; EqA35 is a numerical-kelvin law and must use `(T−Tr)/(1K)` before cubing, with dimensionlessIvT and1e-8. This is an explicit dimensional reconstruction of the printed numerical equation, not a new material coefficient. A dimensional DSL may need a declared positive temperature scale1K (or equivalent supported typed literal); do not strip K units. Hidden vf=.1 is the selected viscous model. Rate-independent vf0 is an explicit special-case variant; do not infer it from IvT=0, since A35still hasIv=.004 at IvT0.

The proposed starting example in parameters.json is an unsaturated hydrostatic mathematical context, not a reproduced experiment or reconstructed consolidation protocol. `initial_context_check.py` independently verifies its derived interior inequalities with70-digit Decimal: em≈.2746943,eM≈.3532656,S_M≈.0064213,Sr≈.3828770,OA≈10.81985,re≈.4926049,rank-inverse denominator≈1.021594. It uses currentT294K and explicit net compression1kPa,s100MPa,e.725,scan0. Hydrostatic direction must be analytically extended as described below before using this example in a production candidate.

## Source discrepancies and exact variant selection

1. **Mixed hydraulic/thermal absolute value is not algebraically equivalent.** Eq.(27)p12 contains `abs(Dp/(1+em)*s_dot+alpha_s*T_dot)`. The published explicit A1,A6,A8 (and body Eq38/40) use separate absolute values. For opposite-signed internal contributions x=−.001/s,y=.001/s, the former gives0 and the latter .002/s. [algebra-results.json](algebra-results.json) preserves this exact structural witness; no full stress response is claimed from the witness. The proposed candidate is expressly **published explicit Appendix A**, whose complete selected equations are transcribed. It does not claim to be a faithful algebraic rearrangement of Eq10/15/27 for such mixed paths. Both terms and mixed paths must be retained in qualification, never removed to obtain equivalence. Independent review must accept this exact disclosed identity before model admission.
2. **A9/44 omit the dyadic multiplying the scalar correction.** Printed scalar subtraction from a fourth-order identity is not tensorially defined. Body Eq42 explicitly states `B=Id+q I⊗I`, q=bB+cB+3cBdB. Since `(I⊗I):(I⊗I)=3I⊗I`, its unique inverse is `Id−q/(1+3q) I⊗I` when denominator nonzero. Both hydrostatic and deviatoric actions follow. This is a unique source-supported rank completion, not a chosen constitutive modification.315exact Fraction component identities are retained.
3. **A7 omits identity after its scalar second term.** Body Eq39p13 explicitly prints that identity. Use Eq39's tensor form for A7. No altered coefficient/sign is inferred.
4. **Printed tensile statement near Eq17p8 is internally inconsistent.** It says tensile '(positive)' pm while A22 defines pm positive in compression. A17/A20 also become non-real/singular at nonpositivepm for nm=.9. Keep pm>0 in the initial executable domain; do not invent a tension extension or use the contradictory sentence as a sign convention.
5. **Zero suction scanning is genuinely unspecified.** A16 retention has a finite saturated limit, but A15 has division bys. For ae=.9,a_scan0,drying s_dot>0, r=.1 and a_scan_dot=8.1*s_dot/s. There is no finite saturated-start derivative. Powder initializationa_scan0 does not provide an event/reset. A saturated retention limit alone cannot settle this; no boundary projection/reset is authorized by the paper. A positive-suction-only executable domain is an honest implementation boundary, not a reduced THM equation set.
6. **fscan at exactly zero suction rate is omitted from A26.** For s>0 its branch only enters terms multiplied bys_dot orabs(s_dot); a_scan_dot is exactly0. Therefore any finite consistent branch representative gives the same constitutive RHS at s_dot0. Show this independence in reference checks; do not invent a persistent last-branch memory.

## Reconciliation with retained author code

| Old code evidence (source-v1 hash-bound generalmod.cc) | Paper exact law | Selected consequence |
| --- | --- | --- |
| Nine qstates plus stress6; suction,T,Sr,em,eM,S_M,re copied/stored | Table3 and Appendix opening identify onlye,a_scan internal memories; currentalgebra others | Use8ODEcomponents plus committed control context, not redundant15state integration. |
| cc574–707 em_new uses endpoint stress/suction but OLD Temper | A17 algebra currentpm,currentT; Sec5.3 explicitly decouples thermal strain from thermal void, not laggingtemperature | Reconstruct em at each current stage; no oldT lag. |
| State clamps, a_scan/Sr cutoffs, eMfloor.1, logcap10,meanpressurefloor−1codeunits | None specified in AppendixA; equationdomains/limits must be explicit | Reject or analytically extend only reviewed removable limits; do not import numerical clamps. |
| Small suction-rate/increment threshold10^-3 chooses nearerbranch | A26 uses exactsign; zero omitted but productindependence holds | No inherited dimensional threshold. |
| IvTinput>0 toggles viscosityfraction; Drinputscaled1e-6 | Paper vf explicitTable2; DrphysicalSI; IvA35 | Resolvevfseparately; IvT0 does not implyrateindependence. |
| Signednegative suction,negative tensorcompression,implicitkPa | Paperpositivephysicalsuctions,negative tensorcompression,pr1kPa | Explicitsignandunittransform; exactabsolutevaluesandcollapsebranches preserved. |
| Generalizedresponse7 withderivedSr | SrderivedA16 | OfferalgebraicSr observable, nofakeconstitutive saturationODE required. |
| Error branch restoresmaterialthenadvancescontrols | Paperdoesnotdefinecallertransactionpolicy | Atlasmustprospectivelyspecifyatomicfullcontextcommit/rollback. |
| CodeHTterm andcoefficientbranches | A5–A8 +Eq39 tensoridentity | Paper formulasgovernselectedvariant; nocode-byteagreementclaim. |

## Domains, limits and prospective implementation policy

Source denominators, logarithms and powers demand explicit checks: finite complete inputs; positive T,Tr,pr,hms,se0,lp; positive a+bT and a+bTr; e>0,em>0,eM>0; pm>0,pM>0; 0<S_M<1 in the strict interior; positive finite NCL slope and lambda_act; and nonzero lambda_act denominator,1+3q,eA−em,1−2nu,1+nu,1−sin(phi)^xi,ln(Oc),omega,I3+I1I2. Fractional powers need real admissible arguments: Fm>=0 and 1−Fm>0. The normalized direction must be nonzero. Iv must be positive for the viscous exponent. ae=1 makes A15 singular while eliminating the hydraulic branch distinction; avoid ae=1 in the first candidate unless a separate reviewed limit supplies a constant branch. The paper supplies no universal numerical parameter ranges.

Proposed bounded qualification uses positive suction and pm/pM, 0<ae<1, e>em>0, 0<=a_scan<=1, and inside/on-ASBS states OA>=1. Check these state and step domains at every integration stage. These are conservative explicit Atlas guards, not paper parameter bounds. Reject invalid states; do not clamp them to continue. At strictly positive suction, A15 points inward at the a_scan endpoints: drying moves zero upward and holds one; wetting holds zero and moves one downward. This continuous boundary property is independently checked; it does not authorize finite-step clipping.

At hydrostatic stress, A33 has 0/0 for cos3theta. In A12, that factor is multiplied by Fm^(1/4), which tends to zero as the deviator vanishes. Its bounded Lode-angle contribution therefore vanishes. With Fm=0 and OA=OI, `dA=−I*(2/3)*sin(phi)^xi/(1−sin(phi)^xi)` and `d=−I/sqrt(3)` for 0<phi<pi/2 and xi>0. This unique isotropic extension needs independent Cartesian and near-hydrostatic direction tests before candidate qualification. Do not declare an arbitrary finite physical Lode angle; only the product has the required limit.

As s approaches zero, retention can be extended to S_M=1 and D_sS=D_seS=0, but hydraulic memory may remain singular as discussed above. As pm approaches zero with nm=.9, Dp diverges. High-suction saturation underflow and saturation-close-to-one logarithm products need stable expressions checked against independent references. A positive-suction interior release may reject unqualified boundaries while retaining all eight ODE components and all THM terms. The public profile must explain that limitation.

## Temporal integration, transactions and qualification handoff

Use an explicitly typed physical-time controlled ODE capability. The existing path ODE has no physical-clock contract and cannot gain one by merely naming a control seconds. Values and first derivatives must be sampled at matching integration stages; the six mechanical rates must use that same stage context. A fixed-suction, fixed-temperature, zero-strain-rate interval is a genuine timed hold: e and a_scan remain constant, while net stress relaxes when NVB*Dr is nonzero. With vf=0 and all rates zero, the constitutive RHS is exactly zero. Setting IvT=0 with vf=.1 still permits relaxation. Step partitions should converge numerically; a hardcoded endpoint or old-temperature lag is unjustified.

An accepted advance must commit all eight state components, current time, controls and parameters. A failed stage, exhausted budget or out-of-domain control must preserve the complete parent context, including controls and time. Restart requires all of that context; repeated trials start from the same committed parent. No physical reset, projection, instantaneous thermal shock or saturation event is introduced. Distinguish finite controlled ramps from discontinuous reinitialization. Initial loading must be explicit; illustrative state values are not physical defaults.

Before observing compiled results, freeze an independent Cartesian or high-precision tensor oracle from A1–A35, not a rewrite of production expressions. Cover all eight state components and derived observables; all source parameter effects within explicit bounds; six strain-component basis cases, nonproportional prestress and reversals; duration/rate rescaling; viscous holds and the separate rate-independent variant; current-temperature ordering; wetting/drying and coupled suction/temperature ramps with opposing internal contributions; branch endpoint directions and zero-rate independence; near-hydrostatic limits; source-kPa versus SI conversion; ASBS/density/collapse boundaries; invalid-domain full rollback followed by good recovery; restart and partition refinement. Compare native and Wasm against those references before comparing them with each other. Freeze exact oracle/model hashes, corpus, tolerances and settings before the first compiled result; backend agreement cannot waive a source-reference failure. The source-phase checks below are isolated algebra and initialization checks, not full numerical qualification.

## Stable invariant identity and additional illustrative context

The stable invariant expression is exactly source-equivalent: for `sigmaM=-pM*I+z` with `trace(z)=0`, let `j2=z:z` and `j3=det(z)`. Then `I1=-3pM`, `I2=-3pM²+j2/2`, and `I3=-pM³+pM*j2/2+j3`. Substitution into A30 gives `Fm=(3pM*j2+9j3)/(8pM³-pM*j2+j3)`. This avoids subtraction of the hydrostatic contributions in the numerator; it does not change the equation or permit an arbitrary anisotropic regularization. Thirty exact rational symmetric-matrix cases independently verify the identity in `stability_context_check.py`.

The same supplement constructs an additional illustrative context closer to the ASBS: e=.725, a_scan=0, suction10MPa and temperature294K, with isotropic net compression5.185790988798023MPa chosen by independent 70-digit scalar bisection so that OA=1.005. It has em≈.4842606, eM≈.1621948, S_M≈.1738161, Sr≈.7256621 and re≈.9964381. At Iv=.004 the isolated viscous multiplier `OA^(-1/Iv)` is ≈.2873985, unlike the original low-net-pressure context where it is extremely small. This supplies a useful prospective timed-hold starting point, subject to full RHS/domain qualification; no relaxation response or measured specimen preparation is claimed. Exact values and construction are retained in `stability-context-results.json`.

## Reproducible checks, profile and handoff

Run from the repository root:

```sh
python3 -B docs/ingestion/vibe-2026/source-v2/algebra_check.py
python3 -B docs/ingestion/vibe-2026/source-v2/initial_context_check.py
python3 -B docs/ingestion/vibe-2026/source-v2/stability_context_check.py
```

The checks pass: 315 exact rank-inverse component identities; ten exact scanning-chain identities; inward branch-endpoint directions; a 70-digit water-retention derivative check; the opposing-THM witness; current versus old temperature microvoid comparison; and the proposed initial context's interior algebra. Original result JSON is retained. No author binary or backend was run.

[public-profile-draft.json](public-profile-draft.json) supplies reader-facing parameter meanings and bounded example guidance. The coordinator must install it alongside actual reviewed controls and routes; it does not assert that a laboratory already exists.

Source acquisition and the explicit-law inventory are complete for the selected published Appendix A identity, with printed discrepancies and undefined boundaries preserved. The executable candidate, generic capability implementation, full numerical verification, scientific admission, website profile integration and live E8 delivery remain coordinator work. A separate independent review is required; this worker does not approve its own science. No source-v1 manifest or historical claim was rewritten.

Owned new files are listed in manifest.json. The private original-v2 directory retains the PDF, text and read-only renders as reusable primary evidence. No author binary extraction, build directory, worktree or preview process was created. Downstream reviewers/reference consumers are active, so those source resources remain necessary. Source-receipt.json records their locations and sizes. No disposable full-site copy or compiled cache was created.
