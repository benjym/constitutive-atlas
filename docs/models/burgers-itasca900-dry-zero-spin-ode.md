# Burgers — approved continuous material-point model

**Approved by explicit user instruction on 1 November 2026**, for the bounded dry, small-strain, fixed-frame zero-spin scope. The [approval registry](../../catalogue/approved-models.json) and [admission record](../admission/burgers-approved-v1/approval.json) bind approval to exact model SHA-256 `1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c`.

The Itasca 9.0.184 continuous Burgers subsystem combines Kelvin and Maxwell deviatoric response with elastic volume change. It stores compression-positive total stress and Kelvin strain in Mandel components. The native physical-time CLI and Wasm ABI support the [qualified timed schedules](../ingestion/burgers-itasca900/integration-v1/requests.json). The [run guide](../BURGERS_TIMED.md) provides serial build commands and creep, relaxation, mixed and strain-reversal/hold examples. Parameters are illustrative, without experimental calibration.

The [separate-agent scientific review](../reviews/burgers-scientific-v1/README.md) approves the bounded formulation and saved numerical evidence with no blocking findings. Its two low findings remain recorded: separately enforcing Kelvin-strain refinement and stale pre-integration metadata. Actual saved errors improve for both stress and Kelvin strain. Approval does not claim either follow-up has changed the original assessor or model.

The executable definition retains its historical draft label and pre-integration description to preserve exact reviewed/tested bytes. This dossier and registry provide current project approval; the original source, integration and review packets remain historical checkpoints. User approval supplies no inferred human scientific signature. Experimental validation is unassessed.

The approved envelope excludes arbitrary parameters/tolerances, independently accurate instantaneous output rates, unconditional discrete dissipation, broader control qualification, finite rotations, coupled pore pressure, plasticity, contacts, FE/MPM host qualification and the vendor centered update. The current browser laboratory has no timed-loading controls for this model. No release or deployment is authorized by this admission.

Three exact original source pages are durably retained in ignored private workspace storage; the [retention receipt](../admission/burgers-approved-v1/source-retention.json) records their hashes. They are excluded from public artifacts.
