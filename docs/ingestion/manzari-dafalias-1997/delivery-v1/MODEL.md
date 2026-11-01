# Manzari–Dafalias1997 original constant-m / Atlas backward Euler

Exact candidate: `manzari-dafalias-1997-constant-m-be-v1.json`. Complete source-supported constant-m variant from the original numerical examples, with the first source b_ref alternative; no2004 fabric or reversal-anchor terms. The original optional evolving-m appendix is a distinct inventoried variant. Source receipts and every original equation locator: [source packet](../source-v1/README.md), [visual reconciliation](../source-v1/visual-verification.md).

## Full source-to-schema crosswalk

| Original content | Candidate representation |
| --- | --- |
| Effective Cauchy stress, Eq7/9/13 | Persistent first six Mandel `sigma` components in Pa; compression positive |
| Void ratio/state parameter, Eq1/29 | Persistent scalar `e`; `ec=ec_ref-lambda_c*log(p/p_ref)`, `psi=e-ec` |
| Cone translation, Eq9/24 | Persistent six-component deviatoric ratio `alpha`, dimensionless; trace invariant checked |
| Constant yield width, p262/264 | Parameter `m`; cm=0; no isotropic-history field |
| Elasticity, Eq7–8 | `Gc`, `Kc` pressure power laws; no optional bulk-pressure floor |
| Flow and stress, Eq11/13 | BE integrated temporary multiplier `gamma`, common residual engine; allstress and allalpha residuals solved together |
| Images, Eq16–22 | Translated ratio normal; `cube_trace` algebraic modified Lode cosine, three distinct interpolationratios; bounding/dilatancyimages fulltensor |
| Kinematic hardening, Eq24/26 | Source literal h distance quotient; first b_ref choice; allow negative b:n/softening; no bounding clamp |
| Dilatancy, Eq27/p263 restriction | A contraction of image distance; zero only for psi>0 and rawD<0 |
| Loading/unloading, Eq9/11 | Project Fischer–Burmeister complementarity of gamma and yieldfunction; exactyieldinterior elasticpredictor; no userincrement historyreset |
| Source total volume completion | `e-e_n+(1+e0)trace(de)=0`, fixedinitiale0 parameter; consistent infinitesimalmassbalance completion of printed plastic relation; project choice |

Full units/defaults/project parameter envelopes are embedded in the candidate; printed values are independently tabulated in source-v1. G0/K0 are converted31400kPa→31400000Pa; CSLreference160kPa remains distinct from project atmospheric100kPa. No sourcevalidity claim follows from UI bounds. m, allparameters and e0 persist over a prepared history and replay.

## Integration and initialization contract

A caller supplies finite symmetric infinitesimal strain increments in Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. Physical seconds do not influence this rate-independent law. Allpersistent fields and fullparameters are explicit; literals are examples only. The illustrative state is isotropic160kPa,e=e0=.65,alpha=0, inside the elastic cone. Other prepared states need complete alpha and yield/pressure/distance admissibility. The original qualitative alpha≈stressratio statement is not used as a unique preparation algorithm. Small-strain e0 is the fixed reference voidratio at preparation, retained on restarts; it is not silently replaced by currente.

The original source specifies continuous rates. Atlas chooses backward Euler for stress and alpha, consistent first-order volume balance, unitnorm relative direction off yield and zero direction at exactlyzero translatedratio. On the yield surface this equals the source normal. The origin convention influences only inactive plastictrial terms; it requires zero/hold/entry numerical checks. Complementarity and BE rootselection, Newton/backtracking/subdivision and equalityderivatives are project numerical choices, not original author algorithms. No firstyield eventlocation is promised by one finite callerincrement; sourcefirstyield reference and refinement expose discretization error.

No past reversal state or accumulated plasticstrain memory is introduced. Unloading/reloading follows the cone and currentalpha; each internal residual reads immutable committed histories. Solver temporarygamma is not physicalhistory; every internal solve resets it. Success commits sigma/e/alpha together; failedcaller increments return the original fullparent, including anytemporarylayout fields. Mixed-control iterations restart from the same accepted parent. Zero increments should preserve physicalstate; holdseconds are inapplicable. Restart/replay must retain allpersistent state, parameters, controls and fixede0, with temporarygamma handled by normalAPIsemantics.

The literal source domain requires p>0 and b_ref>|b:n|. No clipping, denominator epsilon, tensioncap or postfailureextension is supplied. Branch equality derivatives follow the common DSL/AD; stresscontrol tangents and constitutive Jacobians retain existing common-engine semantics. The unconstrained parameterbox is not a scientific qualification envelope. Source calibration is illustrative; sourceexperimentalcurves are not redistributed or treated as new validation.

## Prospective qualification and delivery

[Referencepolicy](reference-v1/POLICY.md) was frozen before anycompiled observation. Independent scalarconsistency-eliminated sourceODE paths cover dense/loose, compression/extension, drainedconstantradialstress/undrained, complete stress/e/alpha checkpoints and analytic firstyield; separate analyticelasticity and elasticunloading are included. Exactfullplasticcyclic qualification is still open, not inferred from these monotonicpasses. Parent compiledpolicy additionally freezes fulltensorcovariance, Jacobian, rollback/recovery and replay checks. E5 approval and finalexposed protocolscope await a separate actualagent decision. This dossier records a candidate; no scientificapproval, atlasinclusion, browser or liveclaim follows.
