# Kelvin–Voigt main laboratory interface v1

WEB-kelvin-voigt-comsol63-v1; owner kelvin_interface; scoped new components only. The coordinator retains shared routing, packaging, scientific approval, builds, actual browser and delivery ownership.

The proposed component uses the common `atlas_run_schedule` Wasm transport in a per-run worker. No constitutive kernel is implemented here. Independent closed-form equations in the package checker are test oracles only. The exact model pin is the source-v1 candidate SHA256 `080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da`.

All six initial strains and six incoming rates are explicit. Default creep starts with zero strain and nonzero deviatoric incoming rate, which defines a nonzero stress subsequently held. Creep approaches `tau D_initial` with exponential strain evolution. Constant rate and strain hold remain separate modes. A hold immediately sheds viscous stress and maintains the elastic stress; no exponential hold relaxation is claimed. The wire protocol calls this strain hold `relaxation`, matching the generic schedule API. The common schedule result envelope remains schema_version0.2; this does not change the model's explicit v0.3 formulation.

The table exposes six strains, six total stresses and event side for each physical time; both duplicate initial/start points remain visible. Each of six Mandel components is selectable in stress and strain plots. Controls display Pa, s, inverse seconds, compression-positive Mandel conventions and the small-strain fixed-frame restriction. Links expose source, readable review, checklist, approval and exact definition; no experimental overlay or validation is asserted.

Import strictly rejects duplicate keys, overflow and inexact integer JSON, verifies exact controls/request/identity, then replays and compares the full result. Input changes, reset, imported reads and outgoing selection invalidate the prior generation; worker termination plus generation/active guards prevent stale publication. The component deliberately adds no global model-selector listener. Parent routing must deactivate it before activating another profile.

## Reproducible checks

- `node --test tests/test_kelvin_voigt_contract.mjs` — five pure transport tests passed; complete output retained in contract-tests.log. Synthetic result fixtures test shape/identity and are explicitly not numerical evidence.
- `node --check web/kelvin-voigt-laboratory.mjs`, same for worker and package checker — syntax passes.
- `node tools/test_kelvin_voigt_package.mjs <site>` — **not executed by this worker**. Coordinator-owned compiled handoff required. Frozen acceptance is360 full state/stress comparisons over three modes, all asset identity checks, exact replay and persistent-engine invalid-request recovery. Frozen budgets are3e-8 strain and1Pa stress, before execution, not broad accuracy bounds.

`freeze.json` pins five proposed files before any compiled or browser observation. No compiled/native/Wasm execution, build, shared edit, commit or admission action occurred here. No failed executable check has been discarded. Required next steps: independent interface review, coordinator guarded package integration, compiled package checker, actual browser qualification including all profile transitions and stale callbacks, then exact release/live checks.
