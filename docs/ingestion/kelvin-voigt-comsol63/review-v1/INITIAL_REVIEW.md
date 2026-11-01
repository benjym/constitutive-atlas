# Independent Kelvin–Voigt review — initial findings

Reviewer: `/root/kelvin_scientific_review`, a separate agent run that did not author the transcription, numerical study or interface. Date: 2026-11-02. Task: REVIEW-kelvin-voigt-comsol63-v1. Status: **pending backend evidence; no model approval issued**.

Exact candidate: `models/research/kelvin-voigt/kelvin-voigt-comsol63-deviatoric-zero-spin-ode.json`, SHA256 `080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da`.

## Source and equation audit

Read retained original COMSOL6.3 theory HTML and settings HTML, the complete source-v1 packet/crosswalk/reference scripts and exact candidate. Visually inspected the privately enlarged equation images074 (Eq3-36),010 (elasticity),075 (dashpot dissipation) and003 (pressure sign); original file hashes independently match all11 receipt entries. The source specifies an ordinary spring/dashpot parallel element, deviatoric viscous stress `2η D_d=2Gτ D_d`, no auxiliary strain DOFs, and additive elastic stress `K tr(ε) I+2G dev(ε)`. Settings explicitly permit deviatoric viscosity and tau in seconds. It is distinct from generalized Kelvin chains, SLS, Maxwell and Burgers.

The model faithfully specializes to isotropic, dry, fixed-frame, infinitesimal-strain behavior with no inelastic strain or initial stress offset. Joint negation of source stress, strain and rate preserves coefficients/work under compression-positive Atlas conventions. Mandel ordering and engineering shear factors are consistent. Pa, seconds, inverse seconds and dimensionless strain give Pa stress and Pa/s dissipation. Finite rotations/strain, volumetric viscosity, temperature/fractional/coupled effects and experimental validation are expressly excluded.

Only total strain is persistent: epsdot=D. No fictitious branch memory is introduced. All six initial strains/rates are explicit; initial stress additionally depends on incoming rate. Positive K,G,tau represent a passive specialization, while machine bounds1e-12–1e30 are disclosed as representational bounds rather than a qualified material envelope. Source-complete does not mean compiled, approved or delivered.

## Independent check

Reviewer-owned `independent_check.py` imports neither the source-worker oracle nor generated kernels. It independently assembles the Cartesian Lamé spring/dashpot relation, converts shear transport explicitly, and compares the common Python interpreter in80new deterministic all-six cases. It also checks epsdot=D and the free-energy/dashpot-power identity. Saved `independent-check-results.json` reports480stress components, maximum stress error1.1641532182693481e-10Pa and maximum energy residual2.8421709430404007e-13Pa/s. All11 original receipt hashes/sizes match. This is equation/interpreter evidence, not backend qualification.

Reproduction: `python3 -B docs/ingestion/kelvin-voigt-comsol63/review-v1/independent_check.py`.

## Interface and prospective numerical study

Read the exact Kelvin contract, worker, laboratory component, package checker and five pure transport tests. Independently reran `node --test tests/test_kelvin_voigt_contract.mjs`:5/5pass. The worker delegates to the shared engine, validates supplied byte identities and embedded catalogue, and exposes no handwritten material kernel. The three modes distinguish all-stress hold/creep, finite constant strain rate and zero strain rate/hold. The default creep captures a finite incoming stress defined by zero strain and the explicit deviatoric six-rate vector; it does not fabricate a strain impulse. A rate jump changes viscous stress immediately at continuous strain; a zero-rate hold maintains the elastic stress rather than Maxwell-like exponential stress relaxation.

Full state/stress samples, units, source/review/approval links, explicit initial history, export/import/replay, invalid-input rejection and generation-based cancellation are implemented. The audit does not substitute for an actual browser test. Read execution-v1 PLAN/reference/study/cases/freeze: independent Cartesian and integrating-factor references, predeclared all-six3e-8strain/1Pa schedule gates, tighter algebraic gates, coarse/fine convergence, hold/reversal/rate-jump, derivative/passive covariance, actual-endpoint restart, failure rollback/prefix and persistent-module recovery are appropriate for the bounded scope. Passive basis covariance does not establish finite-rotation objectivity.

## Pending items and limitations

No blocking source, equation, convention, state, rights or prospective-policy defect was found. Native/Wasm raw observations, assessor outputs and exact toolchain/runtime closure have not yet been supplied. Integration transaction behavior and backend delivery cannot pass based on unobserved execution. Approval remains pending those artifacts. Actual packaged browser and live delivery remain separate E7/E8 responsibilities.

Original vendor documents/images remain private; the public packet contains project transcription, references and mathematical analysis. No vendor binaries were executed or redistributed. No experimental calibration, FE-host verification or broad parameter-region accuracy is inferred.

An earlier attempt to create reviewer files failed with “No space left on device” before any file was created. Read-only checks continued in memory. After coordinator space recovery the reproducible script/results above were retained; no scientific failure or original evidence was discarded.
