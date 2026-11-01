# Prospective staged v3 review

Task `REVIEW-lade-domain-control-v1`. Independent source/algebra/static-code review before compiled observations. This review did not author the candidate, controller or acceptance policy. No compiled execution, shared edits, E4 acceptance or E5 approval. Exact inputs are listed in the prospective receipt once the prebuild correction is frozen.

## Disposition

The v3 approach is defensible for the proposed isolated numerical study. It explicitly changes elastic sampling and adds a generic opt-in controller under a new identity while retaining the source differential equations and earlier failures. The source hydrostatic delayed-extinction counterexample to v2 is removed in exact arithmetic by the left-point elastic sampling; full-vs-two-half estimation alone is not the reason. Passing the prospective experiments remains necessary. This is permission to assess evidence from a bounded study, not scientific admission or proof of all 3D boundary behavior.

The requested prebuild preflight correction is present: positive-stress metric accepts only total/effective stress scopes, rejecting none and unspecified. Current candidate scope total is unaffected. Reserved trial counts are now retained in opt-in integrate diagnostics and their maximum in opt-in settings; six-setting legacy JSON has no new fields.

## Model and source checks

Candidate SHA256 `2665b192d3e25b163227037ef7c9f08d2a86e26563a2af8e70a29a91260a45fe` retains endpoint Eq19 plastic work and fixed-kappa2 source potential gradient. E instead uses the committed previous least pressure, and stress residual is divided by its positive dimensionless pressure sminprev. This preserves the exact zero set and gives residual termination relative to previous physical least pressure after the usual Pa state scaling. Previous stress uses the same explicit lazy tie branches, avoiding ordinary repeated-min primal rejection. Signed q/H history and explicit exact-zero branch remain disclosed. The smooth-interior first-order split argument and limits appear in `LEFT_POINT_ASSESSMENT.md`.

For the proportional SPD witness, write S=p*A with fixed positive A having eigenvalues (1.1,1,.9), and de=A*d(epsilon). Source nu=0 and f=trace(A)^3/det(A)=300/11<33 ensure no plastic increment for either Table1 set. Since minimum pressure is .9*p,

    du/d(epsilon)=Kur*(.9)^n*u^n,  u=p/pa.

Thus all hydrostatic reference formulas and the arbitrary-substep FE lifetime proof apply with Kur replaced by Kur*(.9)^n. Consistent rotation does not change the scalar reduction, source history or plastic work. This is a genuinely non-diagonal 3D tensor check, but still a fixed proportional direction; it does not establish general plastic/rotating-eigenvector event fidelity.

`check_left_reference.py` independently constructs a rational orthogonal 3D rotation, 80-decimal-digit source references for hydrostatic and proportional-SPD loading, both Table1 sets and initial pressures 60000,1e-6,1e-12,1e-24 Pa. It checks eight rotated known-endpoint candidate residuals against independently constructed left-elastic endpoints. These are source continuous references and discrete endpoint checks kept separate; no candidate advance is run. The proof applies to exact accepted positive endpoints; finite residual errors, numeric range and nonlinear solver limits need the frozen compiled tests.

## Controller, API and lifecycle

The staged controller retains the old implicit route exactly when increment_tolerance=0. New full, first-half and second-half solves receive separate trial states; the second half alone starts from the first half. Only the actual two-half endpoint is accepted, with no extrapolation. A strict positive least pressure is checked for parent/full/half/two. The Mandel Frobenius stress difference divided by their minimum least pressure is covariant and conservatively bounds spectral-norm/least-eigenvalue errors. It is stronger than a maximum-pressure-normalized stress comparison and supplies no pressure floor. The remaining state differences retain original static scales.

The caller's incoming state remains the returned state unless the whole requested update succeeds. An exhausted second recursive branch therefore does not leak the committed prefix into the returned material state. Diagnostics may correctly retain attempted/accepted-prefix work on a failed call; this must not be described as consumed physical load. Preparation uses the original parent once before recursion. Exact zero q aliases remain solutions of each zero halfstep; the prospective zero-hold checks must verify actual full raw state equality.

The corrected generic setting validator rejects negative/nonfinite path tolerance, inconsistent positive metric with disabled tolerance, and nonbinary native CSV metric flags. Six/eight setting lengths are explicit. Rate routes reject the new opt-in, and timed CLI options are separately rejected; physical-time capability is not claimed. The metric's first-persistent-six-component-sigma requirement is an explicit limited layout contract, not a universal inferred tensor convention. Generic integration later needs equivalent preflight in every exposed host route.

Trial reservations of three implicit solves per attempted macrostep bound attempts by 3*max_substeps even when a short-circuit executes fewer solves. Accepted halves retain the existing separate substep cap; maximum depth and per-solve iteration/backtracking limits still apply. The frozen 120-second study timeout is a failed request, not an exemption. Neither the relative estimator nor budget exhaustion is itself a general exact event certificate.

## Prospective policy assessment

The corrected policy specifies the unchanged 24 triaxial requests and existing independent error/refinement bounds; both source parameter sets; interior hydrostatic refinement; crossings down to1.0001 times critical strain with four external partitions; three very small pressure scales; rotated proportional SPD source-reference cases; corrected lifecycle checks and exact forced rollback/recovery; literal old large-unload backend regression; native/Wasm status and state gates; and disabled-controller regression. These directly challenge the known defects. The .99-critical source error is report-only by explicit prior policy, so it cannot later be claimed as a quantified tolerance pass. All finite budget/timeouts and unexpected failures must remain failures.

General 3D source-boundary fidelity is a bounded numerical qualification claim, not an exact theorem from the hydro/proportional proof. More complex changing directions, plastic coupling and arbitrary boundary tangencies remain limitations. Any newly observed failure requires preserved evidence and a new diagnosis/identity as appropriate. Do not change tolerances, remove an old backend mismatch or advertise a narrower model as completion of the assigned full target.
