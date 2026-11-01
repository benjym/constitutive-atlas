# Drucker–Prager independent agent review v1

Verdict: **accepted within the exact bounded scope below**. Reviewer run `/root/drucker_prager_agent_review` is separate from coordinating/implementation run `/root`; historical transcription and evidence author run IDs are unknown. Starting HEAD was `9055458b3d9ea3400f41633a0300a67e438c199b`. No model bytes, status, shared code or approval registry changed. No build or compiled backend was executed.

## Scope

Exact legacy v0.1 `models/drucker-prager.json`, SHA-256 `b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877`: constant isotropic elasticity, uncapped ideal-cone, nonassociated perfect plasticity; fixed Cartesian zero-spin infinitesimal 3D material point, compression-positive Mandel stress/strain. Effective Cauchy stress is the Atlas host interpretation; it supplies no poromechanics law. Acceptance covers the explicit-state single-increment requests, load/unload/reversal examples, parameter boundaries, expected rejections and rollback/recovery in the frozen 83-case deck, and the exact retained native CLI/Release Wasm interfaces. Local package/UI evidence is historical bounded observation, not current package or hosted release qualification. Parameters/protocols are exactly those requests; equations are assessed symbolically, without claiming numerical convergence for every value in the parameter boxes.

## Source provenance and equation fidelity — DP-01

I read the retained original OpenSees implementation and documentation, verified their two SHA-256 values against `docs/ingestion/drucker-prager/source-receipts.json`, and read the linked primary Itasca page. Original private paths were `/private/tmp/atlas-dp-source-review-v3/DruckerPrager.cpp` and `OpenSees-DP.html`; raw files are not redistributed. OpenSees commit is `8a0273db3e2f5a14c05924a179c1e439500c852c`. Documentation originals are mutable but the acquired bytes are identified. This is not a review of the original 1952 article or full vendor algorithms.

OpenSees HTML yield equation and rhoBar table, and C++ lines 395–408, 492–496, 615–638, 705–715 support the selected smooth specialization. With zero backstress/hardening, its norm is sqrt(2/3)q, I1=-3p under paired sign reversal. Multiplying by sqrt(3/2) gives M=3sqrt(3/2)rho, Md=3sqrt(3/2)rhoBar, c=sigmaY. Atlas gamma=sqrt(2/3) times the source shear multiplier; this reconciles both pressure and deviatoric corrections. Omitting hardening/backstress and the separate tensile surface is explicit and accepted only as the selected ideal-cone specialization.

The [Itasca primary page](https://docs.itascacg.com/itasca930/common/models/drucker/doc/modeldrucker.html), read 2026-11-01, identifies itself as 9.4.29 despite the 930 URL. Equations 9/12 and 17–23 give a shear potential and radial return; its apex section sets zero deviatoric stress at the apex. With paired signs, q=sqrt(3)tau gives M=sqrt(3)q_phi, Md=sqrt(3)q_psi, c=sqrt(3)k_phi, gamma=lambda_s/sqrt(3). Its separate tension algorithm is excluded. This mutable supporting comparison is not an executed benchmark or immutable version claim.

## Conventions and dimensions

Mandel order is [xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]. The Euclidean dot is tensor contraction; the OpenSees physical shear norm's factor 2 and engineering strain factor 1/2 reconcile with it. Pa-valued E,K,G,c,p_ref,sigma and dimensionless nu,M,Md,e,gamma make every stress residual term Pa. Complementarity uses dimensionless f/p_ref; p_ref is a numerical scale, not strength. E>0 and -1<nu<1/2 ensure positive K,G within declared boxes. Atlas c is a q-axis intercept, not directly Mohr–Coulomb cohesion. Exponential void bookkeeping does not establish finite-strain kinematics.

## Initialization and domain — DP-02 / DP-05

Supply sigma/e explicitly; fill gamma=0 in the full eight-slot legacy API layout. The v0.3 crosswalk is documentation only, not evidence that legacy APIs reject omitted state. The 100kPa isotropic stress and e=.7 are illustrative, not specimen preparation. Persistent state is six-component sigma and scalar e; the third field gamma is temporary. Parameter boxes and current domain enforce 0<=Md<=M, e>0 and numerical gamma>-1e-9; initial f/p_ref<=1e-8 is a numerical tolerance, not exact complementarity or projection.

OpenSees documents 0<=rhoBar<=rho. The corrected guard implements this after positive normalization. On smooth yield, plastic work is gamma*((M-Md)p+c). For M>0, the cone implies p>=-c/M, giving minimum gamma*c*Md/M>=0; M=Md=0 is J2. Old Md>M parameters give the independently reproduced -70Pa witness. That old admission defect is preserved, not relabeled as a present failure. The guard alone does not guarantee universal physical admissibility or convergence. e is uncoupled project bookkeeping, updated as (1+e_n)exp(-tr(de))-1; its e>0 guard can reject otherwise solvable stress updates.

## Apex derivation — DP-03

I independently eliminated the smooth backward-Euler equation: s is coaxial with s_trial, q=q_trial-3Ggamma and p=p_trial+K Md gamma. The scalar candidate is gamma=f_trial/(3G+K M Md). When it would make q negative and M Md>0, the apex solution has p=-c/M, q=0 and gamma=(-c/M-p_trial)/(K Md). The admissibility threshold gamma>=q_trial/(3G) is precisely the norm-subgradient condition: the necessary deviatoric flow s_trial/(2Ggamma) has norm no greater than sqrt(3/2). This yields the model min correction, without extending a negative radial factor. At q_trial=0, s_trial=0; selecting p_ref as denominator is harmless algebra, not a stress floor. Md=0 with trial pressure beyond the tensile apex cannot correct pressure and must fail transactionally. Frictionless M=Md=0 and associated Md=M are included in the frozen tests.

## Integration transactions — DP-04 / DP-05

Static review of the frozen and current `cpp/include/atlas/solver.hpp` shows implicit_step copies parent state, resets transients before each solve and holds the committed `_n` fixed. Recursive success commits intermediate persistent sigma/e; only the final internal gamma is returned. integrate initializes result.state to incoming state and writes trial only on complete success. The saved infeasible-tension request includes successful tentative fractions before overall failure, yet returns the exact full input layout; rollback is stronger evidence than a failure before work. The same persistent Wasm module processes subsequent valid requests; native recovery requests are separate CLI processes. UI Reset restores examples and succeeds.

There is no physical clock or hold relaxation. Zero increment solves with unchanged persistent state and gamma=0. For the accepted residual law sigma/e are sufficient constitutive restart information; gamma_n is unused and reset. Independent oracle replay with deliberately changed incoming gamma leaves the update identical. Native checkpoint serialization, persistent native-process recovery, interrupted-run restart, arbitrary loading-history replay and a general host restart facility are not claimed. Only the represented loading/reversal and temporary reset cases are numerically qualified. No globally smooth tangent through yield/apex branches or FE convergence qualification is inferred.

## Independent numerical evidence

`check_review.py` was newly written by this reviewing run. It parses each frozen request and derives its own scalar elastic/smooth/apex return from invariants, reconstructing all six stresses and void ratio. It does not import/evaluate the model DSL or production oracle. All successful native and Release Wasm outputs and stored expectations agree with this independent oracle at the original 1e-4Pa stress, 1e-9 state and 1e-9 relative budgets. Every successful frozen request reports one internal solve, so its gamma can be compared directly. Six expected failure cases check nonzero native exit, ok=false and exact incoming full state. Additional checks cover normalized source yield, shear work, negative-work witness, nonnegative corrected-domain work, proper tensor covariance and gamma independence. Backend parity alone is not used as the equation oracle. This independent analytic construction supplies the equation-level check; no experimental data were assessed.

Native saved-response reassessment reproduces its report byte-for-byte. Web manifest hashes pass, but the original direct `verify.py` command fails against the evolved root at frozen `catalogue/manifest.json`. This failure is retained in results.json. I reconstructed every frozen file in a temporary tree, selecting exact content-addressed archives and two historical git blobs from commit `235b59a79ef18eb753a2c94a80cfa71d7bb40c00` (build_web.py/index.html), checked every hash, and replayed the unchanged collector and saved responses. Its 83-case report reproduces byte-for-byte. Results list each historical resolution. This is legitimate historical reproduction, not a claim that the root still has the old package closure. The source ingestion checker pins the old pre-domain definition and was deliberately not run as a current-model gate.

## Backend delivery and applicability — DP-04 / DP-06

Accepted interface evidence is the frozen native build and Release Wasm outputs, their exact engine/catalogue hashes and pre-observation freeze. Saved UI text/screenshots support a local 100-increment example, displayed guard/source links, invalid input rejection/export disabling and Reset recovery. No new browser session or compiled run was performed in this review. Static declarations, analytical checks and frozen results establish the bounded law/interface scope; a new current release needs its own prospective build/package/browser checks.

Retain all prior failures: old v1 shear/apex integration failure; pre-guard negative-work witness; native attempt1 configuration failure before observations; Debug Wasm first-call out-of-bounds trap; premature missing-.nojekyll package check; native study's 15 preexisting sibling-binding archive failures; original direct web replay failure caused by changed root files. Release success does not fix Debug. Passing expected infeasible Md0 tension rejection is not a successful physical response. Old v1/v2 and source reconciliation retain their exact historical model hashes.

Exclude arbitrary parameter/path coverage, global nonlinear convergence, finite strain/spin transport, hardening/backstress, separate tensile cap, full OpenSees/Itasca equivalence, FE/MPM host admission, generic update tangents, experimental validation/calibration and hosted/current release status. These exclusions make no new model identity and do not silently substitute a different law.

## Reproducibility and rights

Run from the repository root:

```
python3 -B docs/reviews/drucker-prager-agent-v1/check_review.py --repo . --output /private/tmp/dp-agent-review-results.json
```

Optionally add `--private-sources /private/tmp/atlas-dp-source-review-v3` (or durable private location) to recheck original acquisitions. The durable alternative is `--private-sources .local/private-sources/drucker-prager`. No raw source is bundled. OpenSees code was only read, never executed; vendor content is linked and hashed rather than redistributed. Coordinator subsequently retained both exact originals under ignored `.local/private-sources/drucker-prager/`; I verified the durable bytes against both acquisition and additive retention receipts. The Itasca page has no retained raw original/hash, and this new dated web reading does not manufacture one. The exact artifact manifest binds this report, checker, results, model, original receipts, policy, source crosswalks, frozen case deck, saved raw/report outputs and retained failure records. It records actual historical evidence rather than rehashing it as a fresh experiment.

All DP-01–06 decisions above pass within the stated scope. Smallest next action: coordinator integrate the accepted review/approval with the exact model hash, keep the original private source retention intact, and perform separately scoped current release qualification before claiming delivery. No additional scientific sign-off is required by this review.
