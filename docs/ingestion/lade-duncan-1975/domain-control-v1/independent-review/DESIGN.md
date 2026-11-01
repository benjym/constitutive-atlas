# Independent design challenge: implicit domain control

Task `REVIEW-lade-domain-control-v1`. This is an initial requirements/algebra review, pending the coordinator's exact proposal, prospective policy and staged implementation. No compiled execution, shared mutation or E5 approval. The earlier candidate-v2 studies and failures retain their identities.

## Initial verdict

Generic opt-in implicit step doubling can improve path accuracy and detect large domain-crossing requests. Relative stress control is essential near zero pressure. It does not, by itself, guarantee rejection of a finite source-domain event at any fixed nonzero tolerance. It must not be described as exact domain-event enforcement. A bounded prospective study can establish reliability over its stated cases; full-law admission requires an explicit policy for event uncertainty and unresolved boundary proximity rather than silently completing a path beyond the source event.

## Exact-root counterexample

On the source Table1 hydrostatic elastic branch, u=p/pa satisfies du/depsilon=Kur*u^n with n=.8 or .86 and zero plastic work. For unloading macro length L define t=Kur*L*u_parent^(n-1). An exact full BE solve gives normalized endpoint a from a+t*a^n=1. Two exact half solves give first c from c+(t/2)*c^n=1 and final b from b+(t/2)*b^n=c. The estimator |a-b|/min(a,b) depends only on t and n.

Choose any small fixed t satisfying a proposed relative tolerance and accept the two-half result. Each macrostep multiplies pressure by b and u^(1-n) by b^(1-n). The total positive numerical strain length over infinitely many such accepted steps, divided by the exact source critical length, is

    R = (1-n)*t / (1-b^(1-n)) > 1.

The inequality follows also from monotone unloading: endpoint BE underestimates the magnitude of the elastic pressure rate throughout each half interval, so it delays extinction. Any target strictly between 1 and R is crossed after finitely many accepted exact-root steps while pressure remains positive. Finite state budgets may reject some such paths, but budget exhaustion is not a consistent mathematical event detector; changing the budget changes that behavior.

The pure Python script `check_extinction.py` solves monotone scalar roots and constructs six finite witnesses using both source exponents and tolerances 1e-2,1e-3,1e-4. At tolerance1e-3 the n=.8 witness passes 347 macrosteps and reaches 1.007234 times source critical strain; n=.86 passes509 and reaches1.007522. q and work stay constant, so static history/work bounds cannot identify these crossings. These are scalar algebra witnesses, not execution of the proposed controller. A prescribed fixed dyadic partition may follow different steps, but the proposed error criterion cannot universally rule out these accepted paths.

A second independent concern is nonlinear termination: an absolute stress residual floor may let full and both half solves return the same nearly zero parent state. Their estimated difference is then exactly zero. Relative solution comparison does not certify relative nonlinear solve accuracy or that a nonzero supplied load was resolved. Reusing that state can falsely complete arbitrary remaining load. Qualified solves need an independently checked local equation defect at relevant stress/monitor scale; merely tightening a global absolute tolerance cannot remove the scale issue uniformly.

## Full 3D metric requirements

A Frobenius/Mandel difference divided by maximum principal pressure or an ordinary static stress scale can hide loss of the least principal pressure. For positive-definite stress, a conservative covariant metric is

    ||S_full-S_two||_2 / min(lambda_min(S_parent),lambda_min(S_full),lambda_min(S_half),lambda_min(S_two)).

Require every denominator pressure strictly positive and finite. No additive pressure floor. This bounds least-eigenvalue error by Weyl's inequality, preserves basis covariance and does not differentiate an arbitrary eigenvector at a tie. A suitably defined whitened tensor norm can reduce conservatism, but its reference stress and domain need exact specification. Comparing only sorted eigenvalues misses rotation of a stress tensor; comparing only eigenvector-labelled components is unstable at ties. Diagonal hydrostatic and extreme anisotropy with a decreasing least eigenvalue must be separate tests. Such a metric is an opt-in positive-stress-domain policy, not a universal default for all Atlas models.

Both trial trajectories must use the same immutable parent preparation and persistent-state semantics. Accept the actual two-half endpoint without Richardson extrapolation, which could break physical state constraints. Apply ordinary domain/solution checks at parent, midpoint and endpoint, and commit only after the entire caller increment succeeds. Keep provisional full/half solves separate from accepted-step counters, impose explicit work/iteration/depth limits, and restore every incoming slot exactly on exhaustion/failure. Zero increment should bypass path subdivision and preserve signed carrier aliases exactly.

## Stronger alternatives and required contract

A generic event interface can separate the scientific boundary from its representation: an opt-in scalar domain-distance coordinate, source-derived directional evolution or an equivalent transformed-state residual, and a defined reject/partial-stop result. A Boolean endpoint domain predicate alone cannot locate a boundary hidden by endpoint BE's positive root. Merely sampling that same predicate at more positive BE endpoints does not solve the problem.

For the hydrostatic witness the distance coordinate v=(p/pa)^(1-n) obeys the exact linear relation dv/depsilon=(1-n)*Kur; its finite zero event is visible without a pressure floor. This is a useful exact reference for a generic coordinate/monitor facility, not permission to insert a hydrostatic-only handwritten model kernel. An admissible transformed model must derive its general 3D evolution from the source, preserve history/work and covariance, and be separately identified/reviewed. A monitor based on only a first derivative needs a curvature/error bound before being called a guaranteed event predictor; arbitrary nonlinear paths can turn or touch a boundary between samples.

For a rigorous no-false-completion claim, use validated local error enclosures or a source-derived bounded domain-distance evolution and reject whenever the whole requested path cannot be certified inside the domain. A practical adaptive controller may instead have a declared event-location uncertainty; then requests within that unresolved bracket must fail/return partial, not count as completed source paths. The uncertainty, reference tests and budget dependence must be frozen before observations. Native/Wasm status agreement requires handling this uncertainty consistently, not relying on which backend first runs out of Newton iterations.

## Prospective qualification requirements

Retain all original triaxial reference/error/refinement tolerances and failed studies. Freeze explicit path-accuracy and domain-control policies before compiling. Include both Table1 sets; source analytic interior pressures at multiple initial scales; hydrostatic approaches and crossings at1.25critical plus slight overruns1.01,1.001 and an uncertainty-dependent sequence; varied caller partitioning; extreme principal-pressure anisotropy with nonzero shear; rotated/tied stress cases; exact zero holds; forced-work-limit rollback and valid retry. Keep nonlinear residual sufficiency distinct from full-versus-two-half path error. Record consumed increment fractions, accepted states, trial work and stopping reasons. No pressure cutoff, clipping, generic positivity regularization, postfailure continuation, removed failed backend request or post-observation tolerance change.

The immediate next review step is the exact proposal and staged code. This note is not approval of an implementation or a finding that all numerical realizations are impossible.
