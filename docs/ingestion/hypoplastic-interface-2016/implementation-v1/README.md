# Fully rough HvWE declarative implementation v1

Candidate: [hvwe2016-reconciled-fixed-local.json](../../../../models/research/interface2016/hvwe2016-reconciled-fixed-local.json). Exact raw-byte SHA-256 `8ab12775390be5f5aa8f7db7a37da0990d444a343d037bd35fa36e3b5bdbc7ce`.

This is the complete source-reconciled fully rough HvWE interface with inherited original VW96 host, restricted to a fixed local basis with zero spin. [CONTRACT.md](CONTRACT.md) defines the prescribed source-angle controls, illustrative preparation, domains and transactions. [source-v2](../source-v2/README.md) preserves print reconciliation and the exact2016 visual receipt gap; [source-review-v1](../source-review-v1/REPORT.md) independently accepts the disclosed realization for implementation. This is not E5 scientific approval or experimental validation.

State layout is **sigma_normal,sigma_plane,tau_x,tau_z,e**, first four Pa; void ratio dimensionless. Source names sigma_n/p map to the first two state names. The DSL reserves names ending `_n`; its reserved identifier `zn` also required a descriptive replacement. Both rejected pre-execution candidates and validation failures are retained. No equation or acceptance policy was changed in response.

Controls in generated flat order are **gamma_x,gamma_z,normal_strain**, all dimensionless. They are source shear angles and normal compression strain, not slip lengths. No ds adapter or CNL/CNS implementation is included. All values and their derivatives are declared; stress has Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. The stress embedding duplicates the evolving in-plane stress and has zero yz shear. The exact isotropic F=1 branch uses lazy select; nonzero deviator evaluates the algebraically equivalent tanpsi*cos3theta product directly, without epsilon or clamps.

Parameters in flat order are p_ref,phi_c,hs,n,ed0,ec0,ei0,alpha,beta. p_ref is a numerical stress scale; the other eight are the inherited host material parameters. phi_c is radians, hs/p_ref Pa, the rest dimensionless. Original1996 TableI supplies the Hochstetten material example; initial stress and void ratio here are explicitly illustrative, not an interface experiment or source preparation reproduction.

## Frozen independent evidence

[policy.json](policy.json), SHA-256 `bd8ee5fc47aff6dfd064ccd04b6be9fb1bf838afd3f695e5b0b74eec0d167928`, was frozen before candidate observations. A separate source reviewer accepted its bounded study scope. [reference.py](reference.py) imports no Atlas/model code: it forms full ordinary Cartesian matrices in the original extension-positive convention, evaluates the host and reverses stress signs. Classical RK4 uses128/256/512 fixed steps per segment. [references.json](references.json) retains every endpoint and refinement difference. All10 cases converge; maximum last refinement difference is4.93e-12 in the frozen stress/void scales, below2e-8. Cases cover hold, normal compression/extension, each shear direction, simultaneous shear/normal, reversal, unequal initial stresses/nonzero shears, exact and near isotropy. They share the one declared material example; no broad parameter-box claim follows.

The independent source and candidate use different algebraic evaluation routes for the Lode factor. Exact rational reduction checks remain source-v2 evidence; interpreter/native/Wasm agreement alone is not independent source verification.

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/implementation-v1/reference.py
python3 -B docs/ingestion/hypoplastic-interface-2016/implementation-v1/qualify_python.py
```

The prospective Python qualifier checks all five states and six stress components, instantaneous rates, repeatability, exact hold, zero-progress identity, complete JSON restart, domain/prevalidation rejection and low-trial-budget rollback/recovery. Its saved report, when present, binds exact candidate, policy, reference and qualifier bytes. Do not overwrite reviewed reports: reproduce in an isolated copy of this packet.

## Coordinator backend/package handoff

[backend-requests.json](backend-requests.json) contains59 requests, model index0. It is compatible with existing NorSand generic transports without modifications:22 complete-path requests (11 increments twice),22 restart half-advances,13 rejection cases, recovery and zero progress. `state_from` chains use actual committed outputs. Failed-call sentinel protection is asserted by the transports. [backend-expectations.json](backend-expectations.json) independently maps every ID to source-reference states and all8 observables (stress6,pressure,void). Endpoint acceptance is2e-6 scaled:0.2Pa for each stress/pressure and2e-6 for void ratio; it was not fitted to compiled results.

Restart half-step expected values are obtained using the same independent RK4 method at256 half-segment steps, matching512 steps per original segment. No additional material/reference campaign was introduced. Repeat pairs must match exactly. Recovery must exactly match the corresponding normal x-shear baseline. Invalid flat layouts/controls/parameter/state and the numerical trial budget must fail and preserve output sentinels.

Coordinator-only commands after its serial build:

```sh
python3 -B docs/ingestion/norsand-1993/e2-v3/run_native_requests_v2.py LIBRARY docs/ingestion/hypoplastic-interface-2016/implementation-v1/backend-requests.json OUTPUT_NATIVE.json
node docs/ingestion/norsand-1993/e2-v3/run_wasm_requests_v2.mjs MODULE WASM docs/ingestion/hypoplastic-interface-2016/implementation-v1/backend-requests.json OUTPUT_WASM.json
python3 -B docs/ingestion/hypoplastic-interface-2016/implementation-v1/check_backend_results.py OUTPUT_NATIVE.json OUTPUT_WASM.json --output OUTPUT_CHECK.json
```

[generated/path_catalogue.json](generated/path_catalogue.json), path_models.hpp and path_api.cpp are generic generated source/metadata, not compiled evidence. The catalogue's model_sha256 is canonical-JSON hash and differs intentionally from the raw definition-byte hash above. [example.json](example.json) supplies the concrete illustrative simultaneous-shear/normal path. [package-cases.json](package-cases.json) supplies11 independent start/end cases with samples1 for the main-laboratory worker; the coordinator copies/pins these into execution-v1. The public example must retain its fixed-frame/source-angle/illustrative-material limitations.

No handwritten kernel, shared/schema/compiler/runtime edit, build, compiled call, browser action or commit was performed. Coordinator-owned native/Wasm and separate exact-candidate E5 review remain required. The parent owns atlas/profile/browser/release integration.
