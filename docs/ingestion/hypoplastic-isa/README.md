# hypoplastic-isa - ingestion packet

Task ID: ING-hypoplastic-isa
Owner / date: review_vw96 / 2026-10-31
Scope: consolidate the retained 2020 source; reconcile main text, appendix and VW96; specify a bounded supplied-host rate contract. No shared executable law, source repair or admission change.

## Identity and sources

Fuentes, Wichtmann, Gil and Lascarro, *ISA-Hypoplasticity accounting for cyclic mobility effects for liquefaction analysis*, Acta Geotechnica 15(6), 1513-1531 (2020), [DOI](https://doi.org/10.1007/s11440-019-00846-2). Online publication 2019-07-01 and issue June 2020 are distinct dates. Selected identity is the **2020 cyclic-mobility extension**, not ISA-SF2024, IGS97, GIS2024 or an unspecified SoilModels code release.

Retained [publisher PDF endpoint](https://link.springer.com/content/pdf/10.1007/s11440-019-00846-2.pdf), private `/private/tmp/atlas-isa-source-20261031-v1/private/publisher-pdf.pdf`, SHA256 `97b8762b7773e86a7778835f24f46734bb82522052c0856f63e42bc98ba76821`, 4,502,870 bytes, 19 pages. One-based PDF page = printed page minus 1512. Receipt acquisition and this reinspection: 2026-10-31. Read access does not establish redistribution permission. This packet contains no PDF, extracted article text, images, vendor code or binaries.

Paired host: von Wolffersdorff, *A hypoplastic relation for granular materials with a predefined limit state surface* (1996), pp251-271, [DOI](https://doi.org/10.1002/%28SICI%291099-1484%28199607%291:3%3C251::AID-CFM13%3E3.0.CO%3B2-3). User-supplied Downloads PDF SHA256 `70eb1297cd25e67daf8b35b8f8c22f42c3a7fae2c0a62ae9e0079e3b03e64100`; original receipt linked below. One-based PDF page = printed page minus 250. This inspection revisits p263 equations visually, not the entire derivation.

Base ISA dependencies remain [Fuentes-Triantafyllidis2015](https://doi.org/10.1002/nag.2370) and [Poblete-Fuentes-Triantafyllidis2016](https://doi.org/10.1007/s11440-016-0492-2), references11/35 of the selected paper. No matching local Downloads filename was found by the bounded filename search. Their complete sources and exact author-code release are still missing from this packet; bibliographic identities alone do not close algorithmic lineage. Existing SoilModels2018 access timeout and numgeo implementation notes are historical dossier observations, not new acquisition attempts or interchangeable reference implementations.

## Existing work and gaps

Read first: [2020 dossier](../../models/hypoplastic-isa-2020-original.md), [source audit](../../../catalogue/source-audits/hypoplastic-isa-2020-original.json), [original host reconciliation](../../models/hypoplastic-sand-vw96-original.md), [original receipt](../../../catalogue/source-audits/original-papers-2026-10-31.json), and [retained scalar evidence](../../../catalogue/investigations/isa2020-source-v1/manifest.json). Existing `tools/isa_source_diagnostics.py` already covers the barotropy bracket, rate-magnitude defect and reversal chord; this packet does not replace that evidence.

New work: exact denominator correction, explicit main/appendix precedence, compression-positive supplied-host mapping, complete-history initialization/restart inventory, trial/commit ordering and a non-executable machine-readable fragment contract. `source-receipt.json` binds the inspected existing repository files and private PDFs. All statuses remain research-candidate.

### Reconciliation ledger

| Locator | Literal reading / comparison | Disposition |
| --- | --- | --- |
| Main11-12 p1517 vs Appendix33 p1529 | Main beta_h includes `(1-f_z)*f_h`; main image direction uses current normalized strain rate. Appendix uses normalized h_b and d_b and has no mobility factor. | Main extension is selected for this packet; Appendix33 is superseded, not blended. The two separately defined d_b roles must use separate identifiers. |
| Appendix29 p1528 | Rate in `N:strain_rate` has no normalization arrow. Its units and dependence on magnitude conflict with the stated bounded stiffness factor. | Literal conflict retained. Neither a rate-independent executable choice nor normalized repair is authorized. |
| Appendix38 p1529 vs VW96 Eq46 p263 | Inner bracket exponent beta in 2020, alpha in 1996. With Table1, bracket signs differ. | Material unresolved conflict; supplied host must name its exact definition. No silently repaired complete2020 law. |
| Appendix39 p1529 vs VW96 Eq42 p263 | 2020 square-root denominator is **2 + 2*sqrt(2)*tan(psi)*cos(3theta)**; VW96 is **2 + sqrt(2)*tan(psi)*cos(3theta)**. The 2020 terminal subtraction is reciprocal `1/(2*sqrt(2)*tan(psi))`; VW96 subtracts `tan(psi)/(2*sqrt(2))`. | Earlier dossier prose calling first constant `a^2` is itself incorrect; source image reads `2`. This packet corrects that description only, without editing old dossier or resolving the source. |
| Appendix40 p1529 vs VW96 Eq42 p263 | Positive versus negative sqrt(6) in normalized cubic Lode expression under matching normalized stress. | Compare complete definitions/conventions before any change; no isolated sign correction. |
| Table1 p1516 vs closing AppendixC p1529 | Table supplies m_R and new c_z; closing parameter list omits both and state list omits new Z. | Preserve Table1 and main Eq6 inventory; appendix closing list is incomplete for2020. |

Visual reinspection used complete retained renders of printed1514-1517,1519,1526,1528-1529 and VW96p263 following the PDF skill. These differences are not resolved by compiled/interpreter parity.

## Equations and schema crosswalk

Use symmetric3D Cartesian tensors or Mandel order `[11,22,33,sqrt(2)*12,sqrt(2)*23,sqrt(2)*13]`; all six components retained, no deviatoric reduction of h,c,Z. This is the Atlas order `[xx,yy,zz,sqrt(2)*xy,sqrt(2)*yz,sqrt(2)*xz]`, not a claimed source Voigt order. Contractions/norms must preserve Cartesian Frobenius values. Source is compression-negative stress and strain; the contract is compression-positive, zero spin. Set `sigma+=-sigma_source`, `D+=-D_source`, `h+=-h_source`, `c+=-c_source`, `Z+=-Z_source`, `N+=-N_source`. p,q,e, scalar histories and norms stay unchanged; the supplied host nonlinear coefficient is `N_hyp+=-N_hyp_source`. Its linear action is unchanged. Objective rotation/transport for all tensors remains unreviewed.

| Source locator | Quantity / action in compression-positive contract | Schema / units | Status |
| --- | --- | --- | --- |
| Main3-5 p1514 / App25-32 pp1528-29 | `F_H=norm(h-c)-R/2`; `N=(h-c)/norm(h-c)` | h,c sym6 strain; F_H strain; N sym6 unit | N undefined at h=c; guard must be lazy on supported elastic-only action |
| App26 p1528 | Elastic stress action `m_R*L_hyp(D)`; boundary action `m*(L_hyp(D)+rho^chi*N_hyp*(N:D))` | sym6 Pa per path coordinate | Branch-local candidate action; no plastic return algorithm |
| App28-30 p1528 | `m=m_R+(1-m_R)*y_h`; `rho=1-norm(R*N-h)/(2R)` | scalar | y_h literal unnormalized-rate conflict blocks nonelastic rate-independent contract |
| Main3 / App31 p1528 | `h'=D-lambda*N`; elastic h'=D. Boundary `lambda=positive(N:D)/(1+N:c_bar)` | sym6 / strain per coordinate | `c_bar` dimensionless; positive denominator mandatory in proposed support |
| App32 p1529 + Main11-12 p1517 | `c'=lambda*c_bar`; `c_bar=beta_h*((R/2)*unit(D)-c)/R`; `f_h=abs(unit(D):unit(R*unit(D)-h))`; beta_h main11 | sym6 strain per coordinate | Current direction image separate from App30 `R*N-h`; zero images unresolved |
| App34-35 p1529 | `eps_acc'=c_a/R*(1-y_h-eps_acc)*norm(D)`; `chi=chi0+eps_acc*(chimax-chi0)` | scalar / per coordinate | Same unresolved y_h; no independent persistent chi state |
| Main6-8 pp1515-16 | `Z'=c_z*positive(F_d)*(N-Z)*norm(D)`; `F_d=(q/p)/(M_c*F*f_d0)-1`; `f_z=positive(-Z:N)` | Z sym6 dimensionless; derivative per coordinate | Baseline f_d0, not modified f_d, enters F_d. No circular stage solve |
| Main9-10 p1517 | `f_e=(1-f_z)*f_e0+f_z`; `f_d=(1-f_z)*f_d0+f_z` | scalars | Host must accept both modified density factors in same stage |
| App36-41 p1529 | Host L,N_hyp,F,a,f_b and pressure-dependent e_i,e_c,e_d | Pa and dimensionless scalars | Literal host contradictions above; use supplied named host for bounded fragment only |
| VW96 Eq2 p252 | `e'=-(1+e)*trace(D)` | e scalar1 | Paired-host continuity source, not printed2020 general closure |

### Parameters, state and initialization

Sixteen source parameters: host `(phi_c,h_s,n_B,e_d0,e_c0,e_i0,alpha,beta)`; ISA `(m_R,R,beta_h0,beta_hmax,chi0,chimax,c_a)`; mobility `c_z`. phi radians internally, h_s Pa internally; all other SI units1 with R explicitly strain. Exact Table1 calibration and original units remain in linked audit; they are not defaults. In particular h_s=4,000,000kPa=4e9Pa. Project mathematical support should at least require R>0, h_s>0, 0<phi<pi/2, m_R>=1, positive exponents where evaluated and ordered positive limiting densities. A universal admissible parameter theorem is not provided by this source. Do not label these candidate guards as a complete source range.

Conservative full state26: `[sigma6,e,h6,c6,eps_acc,Z6]`. Initial API must require **all26 values explicitly**, exact parameter/host/version identity and a preparation label; no automatic zero/reset of missing histories. Derived beta_h,chi,N,rho are recomputed from one consistent stage, not recursively carried as extra states. Initial sigma has positive pressure under this sign mapping; no tension/zero-pressure fixture supported yet.

Specific FE example Sec5.2p1526: geostatic selfweight/K0/surcharge, source h33=-R,c33=-R/2 (thus Atlas +R,+R/2 on gravity axis), source Eq22 `e0=r0*e_c(p)`,r0=.85. This **does not** specify all h,c components nor full Z/eps_acc for every element test; assuming omitted tensor components zero is a preparation choice requiring explicit declaration. Figure4's Z11=0 and e0=.8,p0=100kPa,q-amplitude60kPa do not give full initial history. No universal virgin-state initialization established. The quoted FE physical timestep .01s is an external dynamic loading schedule, not a material relaxation parameter.

Project diagnostic support can require finite histories, e>e_d, p>0, `F_H<=0`, `0<=eps_acc<=1`, `norm(Z)<=1`, `0<=rho<=1`, `0<=f_z<=1`, nonzero normalized vectors and positive finite host factors/denominators on the **evaluated branch**. These are explicit bounded support choices, not clipping instructions or a proved invariant set of all source trajectories. Under a unit N and nonnegative k=c_z*positive(F_d)*norm(D), the continuous `Z'=k(N-Z)` preserves the closed unit ball if initialized within it; a generic finite step need not. h=c is inside the elastic locus, so rejecting it globally would reject a physically relevant elastic reversal; a lazy pureelastic action may avoid N, but Z' still needs a justified zero/continuation rule in the coupled full model.

## Temporal integration and transactions

A local rate/history law uses a monotone **dimensionless path coordinate** s and full D=d(epsilon+)/ds. It is intended rate independent, but literal Eq29 prevents claiming that property for the complete printed equations. Choosing s=arc length/normalizing D does not establish invariance under other parameterizations. No viscosity, thermal, pore-pressure evolution, physical hold relaxation or inertia belongs in this bounded effective-stress fragment. Coupling Eq21p1526 is separate.

Same-stage order: validate supplied full state and selected branch; derive N/rho; derive F and baseline densities/factors from current stress/e and explicitly named host; compute F_d and f_z; compute modified f_e/f_d; request current host actions with those values; compute main beta_h/current strain-image quantities, c_bar and lambda; evaluate all derivatives from this same stage. y_h and chi dependencies must be resolved before claiming an implemented nonelastic order; do not mix old Z with new beta_h or commit c before evaluating h. Return derivative bundle, branch/domain diagnostics and full unmodified input identity. No mutation during evaluation.

Main3 selects elastic F_H<0 and plastic F_H=0. Boundary unloading has lambda=0 by the Macauley numerator; do not silently replace printed boundary stress M by the interior elastic M solely because unloading begins. An outward predictor with F_H>0 is **not a third branch**. Sec4p1519 says explicit substeps norm(Deltaepsilon)<R/4 plus an elastic trial for yield entry. It supplies neither complete event localization/return algorithm nor error estimator/order theorem, old/new split details, equality tolerances or rollback protocol. R/4 is not an accuracy bound and is not enough to guarantee event capture or positivity.

Zero D makes direction normalization undefined; do not evaluate `0*undefined`. A whole-state zero-increment identity is a proposed API choice, pending consistent source-domain preflight and a declared continuation; it does not prove each printed rate is defined at D=0. Constant applied stress is a mixed-control solve, not necessarily zero strain or a hold identity. Spin is zero; rotating an entire input/axis dataset is a covariance test, not finite-spin validation.

Required engineering transaction: snapshot all26 states, branch/event data and diagnostic counters; all substep/RK stages remain trial-local; accept only complete supported result with error/domain/event checks. On budget/domain/normalization/event failure, return the original full snapshot exactly and explicit partial attempted coverage; discard all trial h,c,Z,eps_acc changes. Retry with reduced step starts at last accepted snapshot. Restart restores full histories and selected variant; geostatic initialization is not replayed. Never retain beta_h recursion implicitly. A consistent mixed-control tangent is the derivative of the chosen finite-update algorithm and its branches; source M is a local action, not that discrete tangent.

## Independent checks

`check_packet.py` is project-authored stdlib algebra and receipt validation, not a material kernel. It verifies private hashes when paths exist, frozen repository dependencies when `--repo` is supplied, the different host shape formulas at an explicit point, bounded fixed-direction Z analytical evolution, elastic reversal geometry and compression-sign invariants. Exact policies are in `fragment-contract.json`; no missing source equation is guessed. Existing3 scalar tests also passed unchanged on2026-10-31:

```
python3 -m unittest tests.test_isa_source_diagnostics -v
python3 docs/ingestion/hypoplastic-isa/check_packet.py --repo . --output /private/tmp/isa-ingestion-checks.json
```

The second command can run from the staging directory with absolute `--repo` until integrated. `checks.json` retains outcomes. These checks do not establish full history integration, material trajectories, calibration, experimental agreement or compiled parity.

## Handoff

Owned files: README.md, fragment-contract.json, source-receipt.json, check_packet.py, checks.json, manifest.json. All reside only in assigned ingestion directory in the delivery overlay. Manifest excludes itself, binds original authored files and explicitly contains no copyrighted source. Coordinator handles integration/board updates and any correction to prior dossier prose.

Blockers: (1) authoritative resolution/version identity for Eq29 and Appendix38-40; (2) exact2015/2016 complete base-history and matching author numerical source; (3) initial full histories/preparation for a numerical source target; (4) zero-direction continuation and elastic/Z interaction; (5) boundary entry/unload/return and finite update algorithm; (6) source domain/near-liquefaction and objective transport; (7) rights/release pin for external comparison. Neither canonical VW96 substitution nor normalized y_h closes a2020-source completeness claim.

Smallest next task: a separately named supplied-host **instantaneous**, zero-spin ISA fragment, with explicitly supplied positive host action, baseline F/f_d0/e_c/e_d and declared variant choice for y_h; evaluate supported interior and regular boundary states independently in Cartesian tensors. First prove sign mapping, scalar boundedness, contractions, basis conversion and lambda/coupled-state nonmutation. Pureelastic h'=D/c'=0 geometry may precede that without resolving the full law. Do not begin finite-path claims until branch/zero/history gates close. Symmetric tensor algebra and dyadic action `N_hyp*(N:D)` need no general fourth-order primitive solely for this coupling; same-stage supplied-host callbacks/typed action composition and branch-local lazy guards are proposed generic capability requirements, not new shared-code changes in this packet.

**Source completeness:** exact2020 primary receipt and bounded equation inventory, unresolved contradictions/dependencies. **Executable support:** contract only; no ISA model admitted or added. **Numerical verification:** retained scalar algebra plus new bounded diagnostics only. **Scientific/public admission:** unchanged, pending independent source reconciliation and later finite/reference/experimental studies.
