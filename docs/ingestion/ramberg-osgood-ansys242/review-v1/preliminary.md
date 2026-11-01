# Actual independent review — preliminary, 2 November 2026

Reviewer run `/root/ramberg_review`, separately dispatched by author/coordinator `/root-power-successor-ramberg-20261102`; neither candidate nor source packet was authored by this run. Candidate inspected: `models/ramberg-osgood-ansys242.json`, SHA-256 `c949cb14269846ec46a7e8f25718e17e8c8eab394b6ee09204f029e1ca15a3e2`. This is a preliminary technical assessment, not an accepted approval record.

## source_provenance

Read private primary HTML and visually inspected the rendered equation contact sheet, including the governing tensor, pressure/deviator definitions, parameter-domain graphics, equivalent relation, and energy graphic. HTML title, section and footer agree with ANSYS Material Reference Release 2024 R2 §4.17. Independently rehashed all 41 source receipt entries successfully. Source is a vendor release variant, not attribution of this exact implementation to the original 1943 formulation.

## equation_fidelity

The full source tensor relation maps exactly to candidate compliance after simultaneous reversal of source stress and strain. The pressure sign changes consistently. Candidate uses q²/sigma0² raised to (n−1)/2, equal to the source factor for nonzero q; explicit zero branch gives the correct origin value. Candidate includes no irreversible state or yield switch. Alpha is dimensionless; nonlinear uniaxial offset is alpha sigma0/E. The inspected printed energy graphic repeats equivalent stress squared in its volumetric energy term. A hydrostatic state disproves that energy expression. The candidate appropriately excludes energy rather than silently implementing a correction.

## conventions_dimensions

Every term in `compliance_stress−E*epsilon` has stress units. Mandel tensor contraction and simultaneous compression-positive sign conversion preserve source invariants. The candidate is fixed-frame small-strain total-stress mechanical scope, with no inferred pore pressure, temperature or finite-rotation capability. Stress and strain use full six-component storage.

## initialization_domain

The explicit default is hydrostatic100kPa and consistent strain `(1−2nu)*100kPa/E` on each normal component. Complete sigma/epsilon input plus initial compliance check prevents residual-offset initialization. Strict E>0, sigma0>0, alpha>0, n>1 and −1<nu<0.5 suffice for the positive elastic domain. UI min0 for alpha and min1 for n are boundary hints only; domain rejection must remain exposed and tested. Fractional n origin derivative implementation requires compiled evidence, because the source composed map is differentiable while an incautious expression evaluation need not be.

## integration_transactions

The total static relation plus accumulated epsilon increment gives reversible, endpoint-dependent response. No physical time is present. Holds retain state; closed strain cycles return stress. Full trial/commit/rollback and invalid-state recovery remain pending exposed-interface evidence; the source does not prescribe those project engine transactions.

## independent_numerical_evidence

Reviewer `spotchecks.py` independently reconstructs tensor compliance and checks the source equivalent scalar relation in96 deterministic full-tensor states across n1.5/2.5/5/8 and nu−.2/.25/.45. The volumetric, transverse deviatoric and radial deviatoric compliance eigenvalues are positive. No production DSL, atlas solver or author oracle is imported. This complements source-worker checks but does not substitute for frozen compiled verification. The predeclared plan uses an independent monotone scalar inverse and explicit tolerances; compiled reports remain pending.

## backend_delivery

Pending native/Wasm and actual browser interface qualification. No acceptance is issued in their absence.

## applicability_claims

Candidate accurately identifies reversible nonlinear elasticity and excludes irreversible plasticity, hysteresis, energy, temperature coupling, host finite elements, finite deformation and experimental claims. Source physically recommends monotonic proportional metallic loading; mathematical unloading/reversal verification must not be described as physical cyclic validation.

## reproducibility_rights

Private copyrighted source remains excluded from public artifacts. Public receipt, original hash/locator and independent original algebra permit audit without redistributing vendor artwork. Frozen candidate hash matches inspected bytes. Final tool/report/package hashes and reproduction instructions remain to review after handoff.

## Current findings

No preliminary source/transcription blocker. Review is pending, with no accepted registry record, until native/Wasm, transactions, origin/fractional exponent tangent and actual interface evidence are supplied. No build or compiled artifact was executed by this reviewer.
