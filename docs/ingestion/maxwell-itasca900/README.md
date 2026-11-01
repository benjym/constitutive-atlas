# Maxwell Itasca 9.0 — ingestion packet

Task ID: ING-maxwell-itasca900  
Owner / date: coordinating parent / 2026-11-01  
Scope: first source/formulation ingestion, with a packet-only continuous-law draft and independent algebra. The selected identity is the continuum **Maxwell Model**, Itasca Software **9.0.182**, manual updated **12 November 2025**. This is distinct from dynamic Maxwell damping, Burgers, contact rheology, generalized Maxwell spectra and a plastic yield model. The manual's property section uses a viscoplastic label, but Eqs1–6 contain no plastic surface or multiplier.

## Identity and sources

[Source receipts](source-receipts.json) pin four unmodified private HTML files, retrieval times, URLs, byte counts and SHA-256 hashes. Source HTML is retained under `/private/tmp/atlas-maxwell-itasca900-sources/`; temporary storage is not a durable source archive. Copyright belongs to Itasca; raw pages and vendor programs are not redistributed. Downloads filenames and existing source/model inventories were checked before acquisition; no Maxwell source copy was identified. No PDF was used.

- [Maxwell Model](https://docs.itascacg.com/itasca900/common/models/viscous/doc/modelviscous.html): Eqs1–3, scalar series spring/dashpot; Eq4 and adjacent definitions, deviatoric update; Eqs5–6, volume elasticity and stress reconstruction; Model Properties and Notes, material inputs. Main receipt SHA-256: `b3848e97c2a0249859a61db4915afd1347a271540eca0fe69fd8e83706b5756c`.
- [Sign Conventions](https://docs.itascacg.com/itasca900/common/docproject/source/manual/program_guide/modelformulation/signconventions.html): direct stress, direct strain, shear stress and strain rate. Tensor stress/strain are tension/extension positive. Contact force has a different sign convention and is outside this packet.
- [Maxwell Oedometer Test](https://docs.itascacg.com/itasca900/flac3d/zone/test3d/Creep/OedometerMaxwell/oedometermaxwell.html): Eqs1–6 and preparation paragraph; small-strain setting in the displayed data file. Code was read as evidence and never executed. Figures and the called `parameter` file have not been acquired; numerical figure agreement and full example reproduction are not claimed.
- [Creep Model Group](https://docs.itascacg.com/itasca900/common/docproject/source/manual/program_guide/models/creep/description/description.html): same-version family index only; it supplies no additional equations.

The main page cites J.C. Jaeger, *Elasticity, Fracture and Flow*, third edition, Wiley (1969). That book was not inspected, so this is an exact vendor-manual ingestion, not a first-publication reconciliation. Initial web-reader/DNS/HTTP failures and the subsequent successful browser-user-agent retrieval are recorded in the receipts.

## Existing work and gaps

The [temporal design](../../TEMPORAL_INTEGRATION.md), [physical-time API](../../TIME_ODE_API.md), [timed schedules](../../TIMED_SCHEDULES.md) and [synthetic Maxwell fixture](../../../tests/fixtures/time/maxwell.json) already supply analytical engine tests. The fixture remains unchanged and is not a source receipt or literature admission. Its `tau` corresponds to eta/G here; its artificial `time_limit` is absent from this source law. The separate Burgers ingestion is not owned by this task.

This packet adds first manual receipts, exact finite-step versus continuous identity, an explicit [v0.3 draft](candidate-v03.json), source anomalies, preparation and solver boundaries, and independent equation checks. No current model definition, compiler, schema, public catalogue or historical evidence was changed.

## Equations and schema crosswalk

Target: [schema v0.3](../../../schemas/model-v0.3.schema.json) and [formulation contract](../../FORMULATION_CONTRACT.md). The draft declares `schema_version: "0.3"`, complete `formulation`, state semantics and initialization. It has no legacy top-level `integration` field.

Let sigma be the compression-positive Cauchy tensor, p=tr(sigma)/3, s=sigma-pI, D the compression-positive infinitesimal strain rate, d=D-tr(D)I/3, h the physical timestep, tau=eta/G and x=h/(2tau). The source's tensor Eq4 coefficients fix tau=eta/G. The scalar spring constant k in Eqs1–3 must not be substituted blindly for 2G in its damping coefficient.

| Source locator | Equation / quantity | v0.3 representation / status |
| --- | --- | --- |
| Main Eq1 | u_dot=F_dot/k+F/eta | Scalar series-element motivation; not a separate 3D state equation |
| Main Eqs2–3 | F_new=[(1-kh/(2eta))F_old+k Delta u]/[1+kh/(2eta)] | Source central-difference algorithm; requires physical h |
| Main Eq4 | s_new=[(1-x)s_old+2G dev(Delta epsilon)]/(1+x) | Trapezoidal integration of s_dot=2G d-s/tau, derived by rearranging Eq4; not an exact exponential update |
| Main Eq5 | p_new=p_old+K tr(Delta epsilon) | No viscous volumetric strain; p_dot=K tr(D) |
| Main Eq6 | sigma=s+pI | Combined ODE: sigma_dot=K tr(D)I+2G dev(D)-(G/eta)dev(sigma) |
| Main properties | K,G,eta | Positive finite material constants, Pa, Pa, Pa s; eta has SI exponents [1,-1,-1,0] |
| Main properties | E,nu alternative to K,G | Standard isotropic conversion K=E/[3(1-2nu)], G=E/[2(1+nu)]; algebraically derived, with E>0 and -1<nu<1/2 for positive K,G; no extra independent parameters |
| Sign page | tension-positive tensors | Negate **all** stress and strain tensor components to obtain the declared compression-positive law; linear law unchanged |
| Oedometer displayed small-strain setting | selected host approximation | `small_strain_3d`, `fixed_spatial`, objective rate `none`; explicitly zero-spin specialization, not vendor finite-rotation equivalence |
| Source symmetric tensors | tensor transport | Mandel order xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz; raw tensor shear maps with sqrt(2), engineering shear strain with 1/sqrt(2) |
| Main stress; dry uncoupled oedometer | stress output | Packet selects **total stress in a dry uncoupled material point**; physical-time observable `stress=sigma`. Pore pressure is absent; no saturated effective-stress interpretation inferred |

**Printed anomaly:** the two adjacent deviator definitions under Eq4 use ij in the subtracted contraction instead of kk. Taken literally, they are not valid trace contractions and do not produce a deviator. The candidate uses the trace projector, justified by the word “deviatoric,” Eq5's kk trace and Eq6 reconstruction. An isotropic input 3I gives nonzero trace 6 under componentwise literal subtraction, versus zero under the trace projector. This interpretation is explicit and awaits independent source review.

**Parameters and admissibility.** Positive finite K,G,eta are the selected physically dissipative regime. The source gives no calibrated interval or material dataset here. Candidate values K=20 MPa, G=12 MPa, eta=24 MPa s and bounds [1e-12,1e30] in each parameter's SI units are illustrative project settings, not source recommendations or a qualified computational range. Domain comparisons use dimensionally typed zero. There is no yield surface, pressure floor, tension cutoff, density, void ratio, multiplier, memory surface or reset variable in this closure. No finite-state magnitude guarantee follows from these broad bounds.

**State and loading.** The only material history is persistent symmetric `sigma` (six Pa components, Cauchy spatial-tensor semantics). Stress-free initial values in the draft are examples only. Every run must supply complete initial sigma; finite tensile, hydrostatic or deviatoric states are permitted by this linear closure. With the known initial stress and future strain rate, neither accumulated viscous strain nor absolute total strain is needed to predict stress. Strain-output reconstruction would separately require an initial strain reference. The model supplies no preparation inversion.

**Complete formulation.** The draft declares `physical_time` / `ode`, six Mandel strain-rate components at each physical time stage, SI seconds for time, finite start time, and strictly positive finite duration. Its stress binding is observable `stress`, Cauchy, total. These input descriptors are explicit in [candidate-v03.json](candidate-v03.json); no strain-path rate or duration-free increment substitutes for physical time.

## Temporal integration and transactions

For a constant D over h, the independent continuous solution is:

`p(t+h)=p(t)+K tr(D)h`,  
`s(t+h)=exp(-h/tau)s(t)+2eta[1-exp(-h/tau)]dev(D)`.

Under zero strain rate, p stays fixed and s relaxes exponentially. Zero applied stress and zero strain rate are different controls: under constant deviatoric stress, d=s/(2eta), with no ongoing volumetric strain at fixed p. Pure hydrostatic loading is elastic. Strain and stress jumps require explicit event treatment: an ideal strain jump adds K tr(Delta epsilon)I+2G dev(Delta epsilon) instantaneously; the finite-rate ODE interface cannot encode a Dirac impulse. Split rate discontinuities into distinct advances. A zero-duration hold is outside the current update API; it is not a finite hold with zero rate.

The source algorithm reads old stress, current tensor strain increment and h, then evaluates C1/C2 and volume stress and recombines. It has no lagged history beyond old sigma and no reversal reset. With D fixed, the source discrete tangent is K I⊗I + [2G/(1+x)] Pdev with respect to Delta epsilon at fixed h. The exact continuous-map tangent is K I⊗I + [2eta(1-exp(-h/tau))/h] Pdev. Both approach the elastic stiffness as h tends to zero. A numerical tangent must identify which map and timestep policy it differentiates.

Source central differencing is stable for positive h but need not preserve monotone stress relaxation: at h=4tau its hold multiplier is -1/3, while the exact multiplier is exp(-4)>0. This diagnostic is retained, not regularized away. Temporal refinement is required. The current engine uses adaptive explicit midpoint for ODEs; that is a project algorithm, not vendor central differencing. Its stiffness, rollback, mixed controls and settings need separately frozen source-specific qualification.

**Transactions:** the main manual does not specify parent trial/commit/rollback or restart APIs. The Atlas proposal preserves complete sigma and clock for repeated trials, commits only success, and rolls back all internal substeps on failure. This is a host requirement, not a verified vendor behavior. No plasticity solve or active-set tangent is needed for the continuous local equation. The exact source physical-time residual/discrete map is unsupported by v0.3; it must not be relabeled an incremental residual without h or emulated by a model-specific kernel. The continuous ODE specialization itself fits the existing profile. Finite-rotation objective transport and coupled pore-pressure semantics remain separate capabilities.

**Preparation/reference case:** the oedometer page obtains an elastic equilibrium first, then resets velocity and begins creep under fixed axial pressure P and zero lateral strains. In compression-positive notation, A=K+4G/3, a=2G/A, b=KG/(eta A), c=4G/(3A):

`epsilon_zz=P/K[1-c exp(-bt)]`, `sigma_zz=P`,  
`sigma_xx=sigma_yy=P[1-a exp(-bt)]`.

Thus initial epsilon_zz=P/A and initial radial stress=P(1-a); an arbitrary zero stress start cannot reproduce this creep phase. Long-time stress is hydrostatic P I and epsilon_zz tends to P/K. Source example timestep starts at 1e-4 and reaches 1e-2 against eta/G=2 in its consistent unit system; those are example settings, not universal limits. The called parameter file and equilibrium process are not reproduced here.

## Independent checks

Run from the repository root, with jsonschema installed in the active Python environment (this run used jsonschema4.26.0 in temporary storage):

```sh
PYTHONPATH=/private/tmp/atlas-maxwell-validation-deps python3 docs/ingestion/maxwell-itasca900/check_packet.py
```

[Results](check-results.json): **13 groups pass**, including structural/semantic/dimensional validation, explicit initialization, 40 independent Cartesian full-tensor rate comparisons, four rational trapezoidal identities, coarse-hold witness, second-order refinement, exact energy dissipation, three rational oedometer derivative substitutions, hydrostatic hold/shear creep and full tensor sign conversion. The Cartesian oracle uses raw 3x3 tensors rather than shared DSL trace/dev. Exact rational work balance is `sigma:D - psi_dot = s:s/(2eta) >= 0`, with `psi=p²/(2K)+s:s/(4G)`. Refinement errors over one tau are 3.0690e-4, 7.6662e-5, 1.9162e-5 and 4.7902e-6 for 10,20,40,80 partitions.

[Retained failures](retained-failures.json) record the initial dimensioned-zero validation error, missing validation dependency and corrected initializer keyword. These are packet preparation failures, distinct from the deliberately retained source-algorithm coarse-step diagnostic. Four private source hashes are rechecked. The private receipt checks require those files; loss of temporary source storage is a reproducibility blocker and must not be reported as a pass. No native/Wasm builds, compiled calls or vendor execution occurred. No historical synthetic compiled report was rerun or rebound to this candidate.

## Handoff

Exact owned files: `README.md`, `source-receipts.json`, `candidate-v03.json`, `check_packet.py`, `check-results.json`, `retained-failures.json`, `manifest.json`. The coordinating parent additionally owns the single new task row in IMPLEMENTATION_PLAN.md. [Manifest](manifest.json) pins packet inputs, current schema/contract/interpreter inputs and unchanged historical synthetic fixture.

- **Source completeness:** selected manual mechanical equation inventory complete; independent acceptance of trace-index interpretation, original Jaeger reconciliation, full vendor host stress/rotation semantics and example dependencies remain open.
- **Executable status:** packet-only schema-valid continuous-law draft; no canonical installation, browser entry, vendor-equivalent discrete map or compiled qualification.
- **Numerical verification:** bounded independent algebra/analytical checks and interpreted rates only; no full solver trajectory qualification or experimental validation.
- **Scientific admission:** unreviewed draft; no promotion or reviewer signature.

Smallest next action: independently review the exact pinned equations, trace interpretation and dry zero-spin scope; retain receipts in durable private source storage. Then freeze source-specific continuous relaxation/creep/oedometer trajectories, parameter envelope and transaction/hold/restart budgets **before** any serial common-engine native/Wasm run. If vendor timestep equivalence is required, scope a separate generic physical-time residual/discrete-update capability rather than changing this continuous-law identity. No release or deployment is part of this ingestion.
