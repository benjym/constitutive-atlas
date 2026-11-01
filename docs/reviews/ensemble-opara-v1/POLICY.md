# OPARA single-experiment explorer — prospective checks

Scope frozen before compiled ensemble responses on 2026-11-01. No model law,
source normalization or historical evidence changes. Three existing exact runtime
definitions: linear-elastic, drucker-prager, modified-cam-clay. Use effective
Mandel compression-positive state, explicit parameters, source isotropic stress
103720 Pa, source e=.416, temporary gamma=0, assumed MCC pc=200000 Pa.
Defaults are illustrative, not calibrated or independently approved model/data pairs.

Data: pinned curated OPARA-TXCD-100 and its existing CC BY 4.0 source declaration;
retain all 1438 measured observations for context. Replay acquired prefix through
axial strain <=.01 (95 rows, last .00992), never sort/deduplicate/interpolate.
Impose source axial engineering strain relative to row zero, direct author
membrane-corrected radial effective stress, equal radial stresses and zero shear
strains. Volume and q are compared outputs. The membrane correction depends on
measured volume; this is conditional replay, not independent prediction.
No physical-time or finite-strain claim. No hidden preparation or endpoint insertion.

Default 15 requests: baseline + two changes for each of two parameters, per model.
Elastic E=24/30/36 MPa, nu=.20/.25/.30; DP M=.96/1.2/1.44,
Md=.16/.2/.24; MCC M=.96/1.2/1.44, kappa=.032/.04/.048. One-at-a-time,
not Cartesian. Other inputs fixed at exact definition defaults; p_ref is fixed.
MCC pc editable as an explicit unmeasured preparation assumption. New fields and
ranges must pass exact model bounds and existing engine initialization/domain gates.

Verification before delivery:
- Source hash and curated-index row/ID consistency; packaged data retain direct
  radial channel and exact source order and count. No loss through plot encoder.
- Pure request isolation, deterministic IDs, five runs per model, named-to-flat
  state/parameter order, input errors, source initial consistency, queue cancellation,
  stale suppression, timeout and failure retention; export/import validates exact
  catalogue/experiment/configuration/request/result bindings before fresh replay.
- Existing recorded document/response validation at worker and main boundary.
  Legacy engine ABI is allowed only with explicit effective-stress model binding;
  verify atlas_describe equals supplied catalogue before each call.
- Independent isotropic elastic solution at all 95 endpoints for five elastic
  requests: sigma_a=sigma_a0+E*eps_a+2*nu*(sigma_r-sigma_r0),
  eps_v=(1-2*nu)*eps_a+2*(1+nu)*(1-2*nu)*(sigma_r-sigma_r0)/E.
  Stress tolerance .05 Pa + 1e-7*abs(reference); strain tolerance 1e-9 +
  1e-7*abs(reference). All five must complete with exact requested observation order.
- For DP/MCC retain every completion, stopped prefix and rejection; do not adjust
  model/solver settings to force completion. No independent equation verification
  claim for these existing model laws from this explorer.
- Queue serial, 30 seconds per job; cancellation terminates active worker and
  marks unstarted jobs cancelled. Timeout is a separate outcome; next job proceeds.
- Actual browser: navigate, default run, visibility/selection, edit-stale, cancellation,
  export/import fresh replay and narrow viewport. Preserve failures and screenshots.

A shared current full website package may be blocked by unrelated stale engines
or concurrent delivery tasks. Qualify an isolated preview using matching existing
engine/catalogue bytes and report that limitation explicitly; do not rebuild shared
native/Wasm targets or imply live delivery. No push/deploy in this assignment.
