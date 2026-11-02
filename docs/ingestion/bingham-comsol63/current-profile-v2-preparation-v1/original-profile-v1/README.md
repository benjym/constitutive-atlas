# Bingham public reader-profile draft v1

Task PROFILE-bingham-comsol63-v1. Source specialist `/root/bingham_source`; 2 November 2026. Own only this new isolated directory. No shared profile, constitutive definition, source receipt, build, compiled artifact or git state was changed.

`profile.json` is the ready-to-integrate editorial object for `bingham-comsol63-mises-perfect-zero-spin-ode`. `profile.mjs` exports that keyed entry using the current public-profile data syntax. The coordinator installs the entry into the shared `web/model-profile-data.mjs` after reconciling the actual qualified route. Neither draft installs itself or grants executable availability. `reading-profile.json` omits executable exploration instructions and explicitly describes public laboratory unavailability; it is the alternative while the runnable route remains pending.

The public prose starts with elasticity, a fixed threshold, permanent shear flow, creep and partial stress relaxation. It contains no approval badges, curation history, ledger milestones, numerical budgets or unsupported claims of calibration. The three experiment names and button/control labels match the inspected `web/bingham-laboratory.mjs`, and their semantics match `web/bingham-atlas-contract.mjs`: hold all strains, hold all stresses, or supply a constant six-component strain rate. Stress-hold values are established by the initial elastic strain, not an invented stress-amplitude control. The reset instruction points to the complete existing example rather than duplicating material default values in editorial content. Parameters remain exact `K`, `G`, `sigma_y`, `eta`; state labels remain exact `eps`, `eps_vp`, `alpha`.

## Source crosswalk

| Public explanation | Readable source and local evidence |
| --- | --- |
| Fixed yield threshold; rate proportional to excess stress | COMSOL6.3 theory039 Bingham images076–078; source-v1 README and candidate |
| Von Mises flow changes shape without volume change | theory039 images016/022/057; trace of deviator is zero |
| α retains history through reversals | theory039 images059/060 and nonnegative multiplier; source-v1 analytical reduction |
| Relaxation tends toward σy; hold time scale η/(3G) | source-derived radial ODE in source-v1 README; not an imported finite-step algorithm |
| Creep above yield; elastic response below/at yield | same source rate law at constant stress |
| K/G elasticity and strain subtraction | theory029 introduction and images008–010 |
| No hardening/thermal effects | interface024 Perfectly plastic, No kinematic hardening, Thermal Effects None |
| Fixed frame, compression-positive total stress and Mandel storage | explicit candidate v0.3 contract and simultaneous source-sign mapping in source-v1 |
| Actual control labels, full initial context and single-segment limitation | current isolated `web/bingham-laboratory.mjs` and `web/bingham-atlas-contract.mjs` |

Primary citations are ordinary HTTPS links to the readable COMSOL theory, interface settings and elasticity page. No raw source images or vendor text are redistributed. Source receipt hashes remain in the existing source packet. `provenance.json` pins the inspected exact model, control files, shared profile content contract and renderer/data inputs.

## Structural checks and handoff

JSON parses; profile module passes `node --check`; parameter names/order match the exact candidate; all state labels exist; all declared local provenance paths exist; reference links use HTTPS. These are content checks only. No material execution or browser qualification was performed by this specialist.

Before installing the runnable object, the parent must confirm the exact route exposes these three modes and the reset example at E4/E7. Then run the normal profile-coverage and renderer checks, inspect the actual catalogue/dialog/laboratory prose and parameter table, and verify the same assets during authorized live delivery. If the packaged controller labels change, reconcile the exploration prose against that exact file. Keep source-backed behaviour and conditional reading profile available while execution qualification remains pending.
