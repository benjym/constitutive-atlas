# sls-comsol63 — ingestion packet

Task ID: ING-sls-comsol63-v1  
Owner / date: sls_ingestion / 2026-11-01  
Scope: source-complete bounded transcription of the COMSOL 6.3 ordinary Standard Linear Solid (Zener), one Maxwell branch in parallel with the equilibrium spring, deviatoric relaxation and purely elastic bulk. Parent owns the separate `execution-v1/` study. This packet does not reconcile the historical first publication or identify an experimental material.

## Identity and sources

Primary version identity: COMSOL AB, **COMSOL Multiphysics 6.3**, Structural Mechanics theory, [Linear Viscoelasticity](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.029.html#3441011), “Standard Linear Solid Model,” Figure 3-5. The [Viscoelasticity settings](https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_solid.07.016.html) distinguish Deviatoric, Volumetric and combined variants and identify the branch shear modulus in Pa and relaxation time in s. This is the ordinary single branch, without fractional derivatives, temperature shifts, geometric nonlinearity, imposed initial-stress offset, thermal strains or pore pressure.

The theory's actual equation images were visually read, not inferred from search snippets: `078` (branch spring/dashpot stresses, anchor3441067), `079` (auxiliary ODE, anchor3441073), `080` (dissipation, anchor3954540). Generalized Maxwell context states that the auxiliary dashpot strain is symmetric and isochoric; image `023` is Eq3-29 with an optional initial-stress offset, set to zero here. Images `008`–`010` establish bulk, deviatoric and total elastic stress. Images `170`–`172` are Eqs3-37–39 for optional local time integration, visually inspected independently.

[Source receipt](source-receipt.json) records exact private paths, URLs, sizes and SHA-256 for unchanged HTML and selected equation images. Private sources live in `/private/tmp/atlas-sls-comsol63/`; raw vendor manuals/images are not redistributed. Long-term persistence of this temporary private directory is not promised: exact public URLs and hashes permit reacquisition. The version is pinned by URL, not a claimed publication year absent from the inspected page. Downloads were checked by filename and existing inventories checked before acquisition; no matching local SLS source or executable was identified. Failed DNS acquisition and three nonessential404 guesses are retained in receipt history.

## Existing work and gaps

The earlier Maxwell and Burgers packets are different rheological networks, not prior SLS admission. This adds a complete ordinary single-branch source crosswalk and a v0.3 draft candidate, with an independent mathematical check. No calibration, specimen preparation, vendor numerical equivalence or measured-data validation is supplied by these theory pages. Finite strain, finite rotation, fractional order, volumetric relaxation and thermal shift models are excluded from this identity.

## Equations and schema crosswalk

Target: [schema v0.3](../../../schemas/model-v0.3.schema.json), [formulation contract](../../FORMULATION_CONTRACT.md). [candidate.json](candidate.json) is `schema_version: "0.3"`, `physical_time`/`ode`, 3D infinitesimal strain, fixed spatial Cartesian frame and zero spin, no objective rate, Mandel order `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`. Stress and strain are compression-positive; stress is observable `stress`, Cauchy, total for a dry uncoupled point. The source's stress tensor is tension-positive, as shown by `p=-tr(sigma)/3` and `p=-K tr(eps)` (images003/008). Simultaneously negating source stress, strain, branch stress and auxiliary strain leaves all linear equations unchanged. No rotation transport is inferred.

Let `eps` be total infinitesimal strain, `d=dev(eps)`, `gamma` the source's dashpot strain, `Ginf=G`, `G1` the branch spring stiffness and `tau=tau1`. Define the packet state **q as branch overstress in Pa**; this differs from the source symbol `q1`, which is a dimensionless spring strain.

| Source locator | Equation / quantity | Schema representation / units | Status / ambiguity |
| --- | --- | --- | --- |
| SLS image078 | sigma_q=2G1(d-gamma)=2eta1 gamma_dot | q=2G1(d-gamma), sym Pa | Exact state transformation, not symbol identity with source q1 |
| SLS image079 | tau gamma_dot+gamma=d | q_dot=2G1 dev(strain_rate)-q/tau | Derived by differentiating q for constant parameters |
| Parent elasticity010 and Eq3-29 image023 | Equilibrium spring plus branch stress | stress=K tr(eps)I+2Ginf dev(eps)+q | sigma0=0 and no other inelastic strains selected |
| Source strain kinematics | eps_dot is prescribed infinitesimal strain rate | eps_dot=strain_rate | Full persistent strain state recovers elastic bulk and equilibrium spring |
| SLS text | eta1=G1 tau; G0=Ginf+G1 | parameters K,Ginf,G1: Pa; tau: s | Positive parameters; no fit claimed |
| SLS image080 | Wv_dot=sigma_q:gamma_dot | D=q:q/(2G1 tau)>=0 | Independent energy balance below |
| Local integration170–172 | ODE and exact convolution; linear-strain segment update | Optional exact reference only | Does not prescribe Atlas's numerical method |

The [machine crosswalk](crosswalk.json) preserves these mappings and choices. There are two persistent symmetric spatial tensor states (12 scalars): eps dimensionless, q Pa. Both require explicit initial values and persist on restart. Example zero states are illustrative, not default preparation. Parameter examples are K=20MPa, Ginf=4MPa, G1=6MPa and tau=2s; these differ intentionally from vendor UI defaults and do not describe a material. Project bounds `[1e-12,1e30]` in declared SI units are numerical envelopes, not source empirical ranges. Strict physical domain is K>0, Ginf>0, G1>0, tau>0. Degenerate Maxwell/elastic limits are not included in this record.

Source gamma is isochoric, so physical q has trace zero. Initialization and evaluation use the explicit project roundoff gate `abs(trace(q))<=1e-10*(Ginf+G1)` Pa. Stress uses the stored q directly with no hidden projection. This gate is a numerical approximation of the exact subspace, not a source tolerance or an imposed tensor constraint solver. The ODE preserves exact trace zero and exponentially decays any admitted roundoff trace. Offsets inside the gate may contribute a correspondingly small volumetric overstress, explicitly limited by this tolerance.

Arbitrary finite eps and traceless q represent a finite-history state with gamma=dev(eps)-q/(2G1). For a relaxed state prescribe q=0; for an analytical instantaneous strain jump from zero prescribe q=2G1 dev(eps). A state at nonzero strain with q=0 means relaxed preparation, not instantaneous application. No independent initial total-stress offset is available. No source-imposed state-reset event is present.

## Temporal integration and transactions

These are rates per physical second. Equation inputs are required finite stage `time` (s) and `strain_rate` (1/s); advances require finite `start_time` and positive finite `duration` with representably later endpoint. The law is autonomous but the clock still belongs to the declared API. Continuous stage rates define loading history; control discontinuities must be split at interval boundaries. The source's optional exact local scheme assumes linearly varying strain within a segment and is not automatically equivalent to an arbitrary rate history or an Atlas RK update.

For constant rate R and interval h, q(h)=q(0)exp(-h/tau)+2G1 tau dev(R)[1-exp(-h/tau)], eps(h)=eps(0)+hR. At zero rate, eps and elastic bulk/equilibrium stresses remain fixed; q decays exponentially. A hold must advance physical time, not skip the update. An ideal strain impulse is outside a finite-rate ODE call; use an explicitly prepared post-jump state for the analytical relaxation study, or a finite-duration ramp. No caller may encode an impulse as a zero-duration advance.

Atlas lifecycle is a host contract, not a claimed vendor implementation: trial from committed state, commit the complete persistent state only on success, return complete incoming state on failure, and repeat/rollback/restart from the same committed state. Both derivatives use simultaneous stage values; there are no lagged parameters, incremental resets or transient solve variables. The source does not prescribe Atlas's adaptive tolerances, transaction interface, solver budget or algorithmic tangent. Constitutive strain-controlled ODE evaluation needs no local Newton solve. A stress-controlled material experiment needs a separate host equilibrium/control solve; those semantics are not encoded in this candidate. Small tau relative to caller intervals is a stiffness consideration for numerical qualification.

## Independent checks

`python3 docs/ingestion/sls-comsol63/check_algebra.py` runs without any Atlas import and reproduces the immutable [results](check-results.json): **10 groups passed**, including100 source gamma-to-overstress ODE identities,100 energy balances and100 deviatoric-subspace identities, constant-rate exact solution, shear relaxation bounds, elastic bulk, creep time, frequency storage/loss passivity, Mandel contraction and exact segment composition. Maximum differential identity discrepancy was2.3283064365386963e-10 Pa/s from floating arithmetic.

Free energy is psi=K/2(tr eps)^2+Ginf dev(eps):dev(eps)+q:q/(4G1). With exact deviatoric q, sigma:eps_dot-psi_dot=q:q/(2G1 tau)>=0, matching image080. For scalar deviatoric stress held constant, creep time is tau*(Ginf+G1)/Ginf, not tau; the bounded instantaneous/equilibrium shear moduli are Ginf+G1 and Ginf. These checks establish algebraic consequences, not measured predictive accuracy.

`python3 docs/ingestion/sls-comsol63/verify_packet.py --source` validates candidate with the installed Atlas validator, checks packet hashes, reproduces independent results, and verifies private source hashes if requested. `make_candidate.py` reproduces candidate bytes from a self-contained definition. No compiled artifacts were built or executed by this worker. No check failed; initial unavailable bs4 dependency was avoided using stdlib reading, without changing any scientific oracle.

## Handoff

Owned top-level files: README.md, source-receipt.json, crosswalk.json, candidate.json, make_candidate.py, check_algebra.py, check-results.json, verify_packet.py, manifest.json. Parent separately owns execution-v1/ and all model installation/admission changes. No shared engine/schema/CMake/catalogue edits or commits were made.

Source completeness: complete for the selected bounded ordinary deviatoric COMSOL6.3 law and variant; historical original publication and experimental identity outside scope. Executable status: candidate structurally/semantically validates on existing physical-time ODE capability; no new capability requested. Numerical verification: independent analytical checks passed; compiled qualification belongs to separate execution-v1. Scientific admission: pending independent equation/numerical review and coordinator integration; experimental validation absent. Smallest next action: freeze candidate and run the parent's prospective execution study, then commission separate-agent review of exact source decisions and retained evidence. Review may support bounded computational use without claiming experiment or first-publication provenance.
