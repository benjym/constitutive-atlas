# VIBE 2026 — original-source acquisition and contract inventory

Task: SRC-vibe2026-original-v1. Owner: /root/vibe_source. Access date: 2 November 2026. Owned paths: this new packet and ignored `.local/private-sources/vibe-2026/` only. No author code, object, executable or Fortran was executed. No model definition, production implementation, approval or compiled/browser result is supplied.

**Source completeness: blocked.** The exact final 2026 article has been bibliographically identified, but its complete readable equation set was not acquired. The supplied archive contains substantial readable updated double-structure model code, contrary to the earlier inference from its unrelated `umat.f`. This code is useful primary implementation evidence; it is not an established exact transcription of the 2026 paper. Do not mark source-complete or implement a reduced substitute from this packet.

## Identity, provenance and rights

The target is D. Mašín, *Viscohypoplastic bentonite (VIBE) model*, Engineering Geology 370 (August 2026), article108827, [DOI10.1016/j.enggeo.2026.108827](https://doi.org/10.1016/j.enggeo.2026.108827). Elsevier metadata and Crossref confirm the title, DOI, publication and CC BY4.0 version-of-record licence. The author bibliography independently links the same [publisher article](https://www.sciencedirect.com/science/article/pii/S0013795226002863). These receipts establish identity and licensing, not missing equations.

The [official dataset description](https://soilmodels.com/download/vibe-paper-dataset/) attributes a VIBE dataset to the paper, dated19June2026, with implementation, element-test driver, inputs, graphs and BCV experimental data. Its page advertises1.46MB. The user-supplied Downloads archive is8,952,082bytes; association by title/member content is strong, but exact identity to the current publisher download was not verified. Preserve this discrepancy. ZIP timestamps are metadata, not a release signature. The readable `generalmod.cc`/.h members are dated28May2026 in the ZIP. No independent semantic release number is declared.

- Original user archive: `/Users/bmar5496/Downloads/VIBEPaperDataset.zip`; exact verified private copy `.local/private-sources/vibe-2026/VIBEPaperDataset.zip`.
- [dataset-inventory.json](dataset-inventory.json) hashes every ZIP member, including unextracted binaries. Only text source/inputs/gnuplot members were extracted to `.local/private-sources/vibe-2026/dataset-readable/`; raw binaries remain inside the private original archive.
- `lintriax/umat.f` remains SANISAND; do not use it as VIBE. The actual relevant updated class is `Hypoplasti_unsat_expansive_thermal` in `lintriax/generalmod.cc`/.h. Separate `_2017` and `_2022` subclasses explicitly preserve older variants.
- `generalmod.cc`/.h carry a three-clause BSD-style copyright licence (David Masin, since2003). This does not automatically licence the entire heterogeneous archive or experimental data. Keep all originals private; redistribute no vendor/author source here.
- [private-retention.json](private-retention.json) binds each retained response/PDF/text/render to exact bytes and usable private paths. Error responses are deliberately retained and are not labelled papers.

Author-linked dependencies acquired separately:

1. [2017 THM double-structure manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_expans-thermal16-pp.pdf), title *Coupled thermo-hydro-mechanical double structure model for expansive soils*,49PDF pages; author bibliography associates it with Journal of Engineering Mechanics143(9), DOI10.1061/(ASCE)EM.1943-7889.0001278. Title page visually inspected. It is an author manuscript, not a verified byte-identical final article. Full equations occur in its Appendix; pp2–3 give conventions, p35 gives reference pressure1kPa, pp40–41 parameters. Keep its older power-law retention and thermal microstructure distinct from VIBE.
2. [2013 HM double-structure manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_EG11-pp.pdf), title *Double structure hydromechanical coupling formalism and a model for unsaturated expansive clays*. Title page visually inspected: it explicitly says manuscript submitted, dated3February2012. Author bibliography associates the later publication with Engineering Geology165,73–88 (2013). This prepublication version is not final-equivalent evidence.
3. SSRN DOI10.2139/ssrn.5348185 is a separate preprint/version identity. No readable PDF was acquired; do not infer equivalence. Author bibliography also lists the2013 host and2017 dependency, not a downloadable2026 author PDF.

## Retained acquisition failures

Publisher HTML, official `/pdf` and `/pdfft` endpoints returned a Cloudflare error document despite an HTTP200 transfer. Web reader opening the exact DOI/PII returned403/redirect errors. Elsevier default article XML returned bibliographic metadata only; explicit `view=FULL` returned `AUTHENTICATION_ERROR` / invalid API key. Crossref's declared plain-text TDM endpoint returned `INVALID_INPUT`, not the article. SSRN delivery returned a challenge response. OpenAlex lists only the publisher PDF and SSRN locations. No access-control bypass, credential search or substitute mirror was attempted. Search snippets may describe the full Appendix but cannot supply a verified readable equation transcription.

The smallest source-unblocking action is a readable exact2026 version of record (especially its complete Appendix, notation, parameter/calibration tables and initialization/time units), or a properly versioned author manuscript with final-equivalence reconciliation. Then compare it line by line against the retained updated code, rather than treating the code's class name as proof.

Institutional leads were also checked: the official SIFEL project page exposes2019/2022 THM releases and older reports, without a complete2026 VIBE law. The complete57-page RELABEN report (second transfer; first partial timeout retained) has conceptual VIBE development/validation plans in p53 section3.2.1 and refers to the2025 SSRN manuscript on p57. It supplies no missing full equation set. Parent additionally reports an ordinary in-app publisher navigation blocked by a CAPTCHA; no challenge interaction occurred.

## Inspected implementation equation map

All following locators refer to the exact hashed `VIBEPaperDataset/lintriax/generalmod.cc`, with `.h`/driver locators explicitly named. They describe the implementation, not a completed source-paper crosswalk. Scalar pressures below follow its signed controls; no Atlas sign/units convention has been silently assigned.

| Locator | Inspected relation or role | Contract consequence / unresolved issue |
| --- | --- | --- |
| cc29–73; h115–123 | Eight controls:6 engineering strains, signed suction, absolute temperature. Seven responses:6 net stresses and total saturation. Nine qstates listed below. | Requires THM controls and physical duration. Public stress output is net stress, not an inferred effective/total label. |
| cc171–246 | Converts all increments to rates by division by `dtime`; returns stress increment by multiplication by `dtime`. Let r=`pdivpsbs`, v=.1 if Iv>0 else0, I=.004+Iv(T−Tr)^3×10^-8, a=1. Then net stress rate = L_BE:D +(H_s_BE+H_s_BEC) ds/dt +(H_T_BE+H_T_BEC)dT/dt +(1−v)N_BE‖D‖+v r^(1/I−a) N_BE Dr. | Physical time matters. Zero mechanical/thermal/hydraulic rates can still relax for Iv>0. Rates cannot be relabelled strain-path derivatives. Temperature range must keep I positive and finite; no calibrated admissible range established. |
| cc491–495 | f_m=1−r_e^m, same for internal swelling/shrinkage in updated class. | Separate2017/2022 branch functions differ; do not import their switching. |
| cc808–813; cc899–902 | e_m=e_m* exp[−(p_sat/s_m*)^κm](a_T+b_T T)/(a_T+b_T Tr); derivative −e_m κm (p_sat/s_m*)^κm/p_sat after clipping positive p_sat to0. | Endpoint p_sat=0 has a possible0/0 derivative; source limit/domain decision required. Thermal void evolution differs from microstructural thermal strain coefficient. |
| cc832–844 | sigma_M=sigma_net+S_M s I (pt=0); p_sat=tr(sigma_net)/3+s. | Signed suction is negative for physical drying in example driver. Positive physical suction and compression-positive Atlas stress require an explicit reviewed transformation. |
| cc922–946 | N_use=N+n_s log(1/S_M^(1/lambda_p))+n_T log(T/Tr); lambda_use=lambda+l_s same suction-log+l_T log(T/Tr). Implemented suction-log cap10. Equivalent pressure exp[(N_use−log(1+e))/lambda_use]. | Implicit pressure reference must be restored under SI conversion;2017 manuscript uses1kPa. Cap10 is implementation policy, not automatically paper law. |
| cc975–1100 | Explicit net-stress operators use B^-1=I−q/(1+3q) I⊗I, q=b+c+3cd. b=s(dS_M/de_M)(1+e_M)(de_m/dp_sat)/(3(1+e_m)); c=f_s f_m(de_m/dp_sat)/(9(1+e_m)); d=nu/(1−2nu). Includes separate collapse switches and internal-strain terms. | Rank-one scalar denominator1+3q must stay nonzero; a general matrix inverse is unnecessary. Full coefficient expressions remain available in the private original. |
| cc1118–1280 | Host uses stress invariants trace,trace(square),determinant; normalized deviator and Lode angle; pressure/density-dependent f_s,L,N; dyadics and symmetric contractions. L=f_s[I+nu/(1−2nu)I⊗I]. N=−r^a[L+sigma_M⊗I/lambda_act]:normalized_asymptotic_direction. Includes clamps/floors. | Requires validated hydrostatic/Lode/normalized-direction limits and tension-boundary policy. Matrix products are polynomial3D tensor operations. Finite objective-rate transport is not established by this local implementation. |
| cc1306–1323 | lambda_act=[e_M lambda_use(1+e_m)+A(de_m/dp_sat)p_M(1+e_M)]/[e_M(1+e_m)−A(1+e)], with A=−[(1−S_M)log(1−S_M)/S_M](n_s−l_s log(−p_M)), limiting branches. | Denominator/sign/domain must be qualified; effective pressure logarithm needs source reference units. |
| cc1422–1458 | Updated main retention S_M=1−exp[−(s_e/s)^lambda_p], for signed s<0, with saturation underflow guard; endpoint evaluation uses new suction/new air-entry value. | Updated smooth retention differs from2017/2022 power law. s=0 handled by branch, not raw division. |
| cc1482–1494; cc1520–1549 | Retention derivatives and scanning factor r_lambda=.1+.9f^3, f selected from a_scan or1−a_scan according to suction direction; near-zero signed increment/rate threshold10^-3 chooses nearer main branch. | Threshold use differs between rate operator calls and finite update calls; units and invariance must be reconciled before continuous-law implementation. |
| cc750–775; cc790–795 | a_scan advances by (1−r_lambda) ds/[s_D(1−a_e)] when a_e<1,s_D<0, then clips[0,1]. Drying air entry s_eD=s_e_ref e_M_ref/max(e_M,.1), thermal factor applied separately. | Boundary event and clipping policy must not be invented from a smooth ODE. e_M floor is implementation-specific. |
| cc574–707 | Finite endpoint update e_new=e+(1+e)tr(deps); e_m reconstructed from endpoint p_sat using OLD temperature; e_M=(e−e_m)/(1+e_m); new retention uses endpoint temperature; S_total=[S_M(e−e_m)+e_m]/e; r_e reconstructed against normal compression state and clipped. | Important ordering ambiguity: oldT in e_m_new versus newT elsewhere. Algebraic variables, numerical endpoints and persistent memory must be separated against2026 equations. No exact currentODE/DAE/update-map equivalence asserted. |
| cc1752–1796 | Initializer requires supplied e,a_scan and initial stress/suction/T; reconstructs other qstate quantities. Negative macrovoid triggers error; outsideSBS warns. | Zero placeholder state values in dataset inputs are not physical defaults. Initialization needs a reviewed source recipe, explicit total density and hydraulic branch. |
| cc1798–1844 | 23 material inputs and fixed internal constants, table below. | No complete calibrated bounds/ranges established. |
| cc148–156 | On error restores stress and qstates then advances strain/suction/T controls. Return excludes `errorstatev` although combined error branch tests it. | Not the Atlas full-context transactional guarantee. Preserve evidence; do not clone error lifecycle as physical law. |
| cc4003 onward | Saturation/scanning/tension corrections and severe-error counters. | Numerical projection/correction requires separate source/policy choice. |

## State, parameters and starting context

Code response tensor order is `[11,22,33,12,13,23]`; engineering shear strains have factor2. Atlas Mandel order instead places23 before13 and uses sqrt2 on tensor components. Compression is negative in code tensor and signed pressure variables;2017 paper conventions use negative tensor compression but **positive** physical gas/water pressure and suction s=ua−uw. Therefore code and manuscript pressure symbols are not interchangeable. Stress called “total” in some internal comments is actually passed as net stress by the main API. Do not settle this ambiguity by copying a comment.

Nine qstates (cc43–52): `e` total void ratio; `suction` duplicated current hydraulic control; `Sr` global saturation; `T` duplicated thermal control; `em` microvoid ratio; `eM` macrovoid ratio; `SrM` macrosaturation; `a_scan` hydraulic branch memory; `re` relative density/void ratio. Stress6 plus9qstate=15 scalar slots in author interface, but some are algebraic/duplicated quantities. This is not a reviewed15-persistent-state ODE specification. Mechanical strain history, current controls and time must also survive restart at the host level.

| Parameter index | Code name / interpretation | Unit evidence / caveat |
| --- | --- | --- |
| 0 | phic, critical friction angle | degrees on input, converted radians |
| 1,2,3,4 | lambda,kappa,N,nu | dimensionless compression/unloading slopes,log-void intercept,shear stiffness |
| 5,6 | n_s,l_s | dimensionless suction dependence of intercept/slope |
| 7,8 | n_T,l_T | dimensionless log-temperature dependence |
| 9 | m | dimensionless shared coupling/collapse exponent |
| 10 | alpha_s | inverseK thermal microstrain coefficient |
| 11 | kappa_m | dimensionless microvoid exponent |
| 12 | s_m* | positive input stress scale, stored negative |
| 13 | e_m* | dimensionless reference microvoid |
| 14 | Dr input | multiplied by10^-6 internally; physical rate1/time; exacttimeunit/scale requires2026paper |
| 15,16 | s_e_ref,e_M_ref | suction scale and dimensionless macrovoid reference |
| 17 | Tr | K |
| 18,19 | a_T,b_T | a_T+b_T T must be dimensionally homogeneous; conventiondimensionless a_T and b_T inK^-1 is consistent but not final-source-confirmed |
| 20,21 | a_e,lambda_p | dimensionless wetting/drying ratio and retention exponent |
| 22 | Iv parameter | coefficient in I=.004+Iv(T−Tr)^3×10^-8; temperature-dependent factor dimensional convention requirespaper |

Fixed code values: Oc=1.4,xi/Kpow=.2,v=.1,mNorm=.5,pt=0,scan floor=.1,e_M air-entry floor=.1,alpha=1.0. These are genuine model/internal choices to reconcile, not generic runtime defaults. Driver help at main.cc1058–1067 and stale `.inp` comments mislabel final parameter placement (e.g. `csh`/`pt`); authoritative actualassignment is cc1798–1844. Shared `plasti_data.dta` contains23numbers ending0, hence this file switches off viscosity; it does not supply a checked relaxation example. Dataset `.inp` members inspected contain no explicit `time`/`dtime` stage control. No example was executed or declared reproducible numerical truth.

## Integration contract and capability handoff

Physical duration is essential when viscosity is enabled; holds are genuine constitutive evolution. Need matching mechanical strain-rate, suction value/rate and absolute temperature value/rate stages. Mixing end-of-step controls with old state silently changes the law. Net stress is a distinct stress scope. Current schema physical-timeODE admits time+strain-rate but no hydraulic/thermal channels, and has only effective/total stress enums. Its controlled-path profile has scalar channels but **no physical clock interpretation**; adding time as a user control would not by itself meet this law. A physical-time continuousODE with properly reconstructed observables may be possible after exact source reconciliation; the supplied endpoint clipping/update does not prove it.

Trial/commit/rollback, full-contextrestart and rejectionmust be specified prospectively by coordinator capability work. Source code's partial-control advancement on error is retained as an observed numerical choice, not an endorsed Atlas policy. Heating/cooling, wetting/drying, near-zero-rate and saturation transitions require explicit boundary tests. Perturbation/generalized tangents occur cc1553onward; source solver choices are separate from equation identity. No finite-spin/finite-deformation capability is claimed. See sibling `../capability-v1/README.md` for independent runtime inventory.

## Independent algebraic checks

Run `python3 -B docs/ingestion/vibe-2026/source-v1/algebra_check.py` from repository root. [algebra-results.json](algebra-results.json) retains105 exact Fraction component identities for the rank-one inverse and a70-digit Decimal finite-difference check of the smooth water-retention derivative. The derivative decreases with positive physical suction, and agrees with `(1−S)lambda_p log(1−S)/s`. These checks validate two isolated algebraic facts; they do not execute author code, integrate VIBE, qualify backends or establish scientific admission.

## Handoff and cleanup

Source acquisition remains incomplete; executable support, numerical verification and scientific admission are all **not established**. Exact original2026 equation acquisition is the first blocker, followed by code/paper reconciliation, physical-timeTHM/net-stress capability, exact model/candidate, independent full-state references and separate scientificreview. No shared board state was changed by this worker.

Owned outputs: this README, dataset-inventory.json, private-retention.json, algebra_check.py, algebra-results.json, public-profile-draft.json, acquisition.json and manifest.json. Private originals and failure receipts remain intentionally retained for source continuity. No preview server/worktree/build cache was created. Extracted text and PDF renders are small source-inspection evidence, preserved under the private source directory; nothing uncertain was deleted. Parent may archive/reclaim after verifying all hashes and downstreamconsumers. Exact2026 originalPDF remains the smallest next action; neither a fully checked checklist nor live delivery can be asserted from this source packet.
