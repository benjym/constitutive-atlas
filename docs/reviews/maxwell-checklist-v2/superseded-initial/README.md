# Maxwell nine-item independent agent review v2

Reviewer/run: `/root/maxwell_checklist_review`, separate from historical implementation, ingestion and reference generation. Actual review date: 2026-11-01. I did not author that historical work. This run read the original retained sources, the unchanged candidate and the saved source/numerical evidence, and assessed all nine current policy items. Earlier technical decisions are evidence, not fabricated retrospective checklist decisions.

Decision: **accepted for the bounded scope below**, with no unresolved in-scope blocking finding. This proposed record is ready for coordinator canonical integration; it does not itself change the registry or complete E6–E8. Human scientific signatures or another user approval are not prerequisites under the current policy.

Exact model SHA-256: `dc378ac0eb6956f7d0028b1fa5927d2906bf05e14ab45b116bc447c25e6b885f`. Candidate bytes were not changed. `source_commit` identifies repository context; the exact numerical dependency closure is the archived execution-freeze, not a claim that current shared files match it. Historical author is recorded by its documented role because its run ID is not recoverable from the inspected evidence; no author identity is invented.

Exact Itasca 9.0.182 Maxwell dry uncoupled total-Cauchy-stress, small_strain_3d, fixed_spatial, zero-spin continuous physical-time ODE specialization in models/research/maxwell/maxwell-itasca900-zero-spin-ode.json, qualified solely by the existing integration-v1 frozen source closure and dedicated native JSON CLI/C/Wasm ABI saved cases, parameters, initial conditions, protocols and solver settings. Direct cases K=20 MPa,G=12 MPa,tau=0.2/2/20 s,duration/tau=0.01/0.5/4 plus frozen hydrostatic/relaxation paths; scheduled relaxation, creep, elastic-prepared oedometer, load/hold/reverse, refinement, rejection/recovery and endpoint restart exactly as pinned. No current shared build, browser/live, vendor-discrete, finite-rotation/objectivity, experimental/FE, broad-domain or unconditional numerical energy approval.

## source_provenance

I read the retained original Itasca 9.0.182 HTML equations and adjacent sign/preparation text. The four original receipts and retention-v1 destination hashes agree. Main Eqs1–6 establish the selected vendor-manual variant; the source is not Jaeger-first-publication reconciliation, dynamic damping, Burgers or a generalized spectrum.

## equation_fidelity

The original tensor Eq4 uses G*h/(2*eta) in C1/C2 and 2G on deviatoric strain. Rearrangement yields s_dot=2G*dev(D)-(G/eta)*s, consistent with the original oedometer b=K*G/[eta*(K+4G/3)]. Eq5 gives p_dot=K*tr(D), and Eq6 reconstructs stress. I accept the explicitly disclosed replacement of malformed adjacent ij contractions by the trace-free projector: literal component subtraction fails isotropic input and cannot meet Eq5/6. The sole stress equation, positive K/G/eta domain and stress observable contain this complete branch-free closure; midpoint/backward Euler are labeled Atlas numerical choices.

## conventions_dimensions

K and G are Pa, eta is Pa s, D is 1/s and the equation is Pa/s. Negating every stress and strain component converts original tension/extension signs to compression-positive signs without changing this homogeneous linear law. Mandel sqrt(2) shear factors preserve tensor work. The complete formulation explicitly binds physical time, small_strain_3d, fixed_spatial, no objective rate, and dry uncoupled total Cauchy stress. General effective stress, rotations and objectivity are excluded.

## initialization_domain

Six persistent stress components and positive finite K,G,eta completely determine future stress for prescribed rate in this autonomous law. Complete initial sigma is required; zero stress and numeric defaults/bounds are examples, not preparation/calibration. The oedometer source requires prior elastic equilibrium with axial strain P/(K+4G/3) and radial stress P*(1-2G/(K+4G/3)), as supplied in the frozen case. There are no yield/reset branches. Broad [1e-12,1e30] bounds are mathematical declarations, not a qualified computational domain.

## integration_transactions

The record distinguishes a continuous physical-time ODE from vendor central differencing and distinguishes stress hold from strain hold. Discontinuities require split intervals and ideal strain jumps require separate events. Saved evidence supports repeat replay, direct late-budget complete stress/time rollback after internal progress, six rejection/recovery pairs and two complete endpoint restarts/backend. Schedule budget failure covers t=0 entry/interval rollback only; later nonzero-time committed-sample failure is excluded. Host transactions are Atlas semantics, not inferred vendor behavior.

## independent_numerical_evidence

Source-derived continuous exponential, creep and oedometer references, exact rational substitutions and energy algebra in the separate historical technical review provide independent equation evidence beyond backend parity. I inspected their construction and retained results, and replayed saved-data checks using the pure frozen assessor without generating references or calling a model. All 24 main plus 14 transaction cases twice/backend remain within predeclared gates, with fine relaxation improving over coarse. Direct maximum 0.0238843 Pa is below 0.05 Pa; fine schedule maximum 1.375203 Pa is below 15 Pa; coarse diagnostic 138.381 Pa has its distinct 1000 Pa gate. No new numerical tolerance is introduced.

## backend_delivery

Native build receipt and successful separately retained Wasm attempt2, raw responses, matching exact model/catalogue identities, existing CLI examples and saved transaction qualification establish only the frozen dedicated research CLI/ABI delivery. My check hashes all 92 archived execution inputs and assesses 76 saved calls/backend. Original parity-v1 failure remains failure; v2 classifies physical initial fields under original 1e-6 Pa/1e-11 budgets and passes 5962 comparisons. No current shared engine, newly built artifact, packaged browser or live deployment qualification is claimed.

## applicability_claims

I accept only dry fixed-frame zero-spin small-strain continuous linear Maxwell material-point use at the explicit frozen cases/settings. K=20 MPa and G=12 MPa are fixed in trajectory qualification, viscosity varies for tau=0.2,2,20 s and duration/tau=0.01,0.5,4 direct cases; named schedule examples use their pinned preparation and settings. Continuous dissipation is analytical, not unconditional numerical dissipativity: legal rtol=0.5,h/tau=6 can accept multiplier 25/4 and energy growth 625/16. This algebraic witness is retained and not a compiled observation. No experimental, FE, finite-rotation, full vendor, broad-parameter or general tolerance claim follows.

## reproducibility_rights

Exact candidate and frozen closure, prospective plan, reference/assessor identities, saved observations, prior separate technical review and original failures are hashed in this record or its receipts. Four original HTML files (59248 bytes) are now durably retained in ignored private storage with hashes identical to original receipts, closing only the former temporary-source lifecycle concern. Itasca raw-source redistribution permission is not established; no raw pages or vendor programs are copied into this public review. Reproduction uses retained evidence; a new build requires a separately authorized qualification and matching inputs. Original historical decisions remain unchanged; this run actually supplies the current nine-item decision.

## Retained limitations

- Approval is limited to the exact dc378ac0 candidate and frozen integration-v1 source closure, dedicated CLI/ABI cases, parameters, initial states, loading histories, solver settings and acceptance gates; it does not approve the current shared build, browser package or live website.
- Dry uncoupled total Cauchy stress, fixed spatial axes, zero spin and infinitesimal strain only. No poromechanics, objective finite rotation, FE host, vendor discrete algorithm or full vendor example reproduction.
- Positive broad parameter declarations are not numerical qualification. Saved direct paths use K=20 MPa,G=12 MPa,tau=0.2/2/20 s,duration/tau=0.01/0.5/4; named schedules and recovery/restarts use pinned integration-v1 inputs/settings.
- Continuous dissipation does not imply unconditional numerical energy decay. Retain algebraic loose-tolerance witness rtol=0.5,h/tau=6,two-half multiplier 25/4,energy ratio 625/16; no compiled observation of that witness is claimed.
- Schedule failure evidence covers t=0 entry/interval rollback, not failure after a nonzero-time regular committed sample. Complete endpoint restarts and direct late rollback have separate saved evidence.
- Original parity-v1 failure, Wasm cache failure, packet preparation failures and prior vacuous endpoint diagnostic remain historical failures; corrected studies retain distinct identities and original budgets.
- The printed ij trace indices are explicitly interpreted as the trace projector. Jaeger book, linked figures, called parameter file, full host semantics, experimental validation and calibration are unassessed.
- Raw Itasca HTML stays private; no redistribution permission established. Durable retention closes only source lifecycle, not broader scientific or delivery claims.

## Reproduce and integrate

Run from repository root:

```sh
python3 -B docs/reviews/maxwell-checklist-v2/check_saved.py
python3 -B -m atlas.agent_review docs/reviews/maxwell-checklist-v2/proposed-review.json --for-approval
```

The checker executes only pure saved-data assessor functions extracted by AST from the hash-verified frozen source, and pure parity functions; it never imports or invokes a production evaluator, generator or collector. It does not recompute or freeze references. `checks.json`, `receipts.json`, stdout/stderr and validation output retain the checks. Private originals were read directly for this assessment; only hashes/locators are public. All 92 archived input members match their freeze. Both backends retain 76 saved calls; original parity-v1 fails and v2 passes 5,962 comparisons. Durably retained originals are 4 files/59,248 bytes.

Coordinator next action: verify this exact proposed record and install it canonically with its report/receipts; preserve model bytes and frozen qualification boundaries. If canonical path changes, regenerate the approval entry from that canonical record. E6–E8 need separate integration/browser/live evidence. No model/catalogue/registry edits, builds, material calls, staging, commits or remote actions occurred in this review.
