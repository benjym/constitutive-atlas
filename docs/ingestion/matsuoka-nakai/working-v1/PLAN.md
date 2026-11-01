# Frozen pre-native numerical plan, working-v1

Date 2026-11-01. No compiled material response has been observed for this identity.

Select original full one-a clay with Appendix V, fixed spatial zero-spin infinitesimal host. Endpoint backward Euler of differential stress, density compatibility and constant-reference void balance. Auxiliary smp is determined by smp²=adj(S)/I2(S), positive definite, and stored for Newton warm start. This identity does not reduce the law to a criterion or substitute the associated-only predecessor. No shared compiler/solver change is needed.

Independent reference: reference.py uses Cartesian eigendecomposition, principal formulas and augmented compliance candidate solves, then RK4; no Atlas imports. Source A8 intermediates are not required: Table1 projection yields Ycs of Eqs18/A10 directly. Appendix V selected to eliminate negative AF. Single-a clay only; two-a sand is a separate variant. Source specimen preparation/experimental reproduction remains open and does not prevent synthetic-state numerical qualification.

Freeze before native observation:

1. Normal schema/semantic validation, explicit initialization, generated catalogue of only this model.
2. Independent regular-state residual fixtures for elastic, AF, AF+IC, IC-only and softening, including a rotated non-diagonal case and repeated positive principal values; residual scaled error <=2e-8. Zero residual <=2e-12; invalid principal stress and inconsistent auxiliary initialization reject. No hydro exclusion.
3. Native zero/hold, hydro compression/unload/reload, deviatoric triaxial compression/extension, simple shear, non-diagonal general tensor paths. Default parameters: Table2 clay. All success claims require full 16-component results and source SPD/auxiliary consistency. Failed numerical calls and partial trajectories retained.
4. Finite-path comparison with independent RK4 (256/512/1024 reference subdivisions; last two endpoints stress difference /p_ref <=2e-6 and scalar difference <=2e-7). Native BE paths caller grids 32/64/128: finest stress endpoint /p_ref within3e-3 and rho/e within3e-4; refinement must decrease endpoint error (unless <=1e-7 scaled). Tangent beta1.5 is nonclassical at isotropy: no full-update tangent claim.
5. Exact hydro NC analytical pressure p=p0 exp(epsilon_v/Cc), unload p=p0 exp(epsilon_v/Ce), e=e_initial-(1+e_ref)epsilon_v; finest error /p_ref <=3e-3, e absolute <=1e-10. No experimental admission inferred.
6. Transactions: repeated trials exact; nonfinite/invalid initial state, inconsistent smp and deliberately over-budget updates reject without changing all supplied state; subsequent valid recovery passes. At least one rotated constitutive residual fixture; no global finite-spin assertion.
7. Keep all historical packet files/hash pins unchanged. Native builds serial, one explicit CMake target --parallel1 in a private output directory. Initial setup failures are retained; any changed material/numerical policy after failed observations has a separate candidate identity and report, not a modified gate.

The standard solver residual tolerance is 2e-10. Use explicit max_depth14/max_iterations45/max_substeps20000 unless an independently identified diagnostic overrides them. BE internal substepping controls nonlinear solvability, not truncation error; caller-grid refinement supplies accuracy evidence.
