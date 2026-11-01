# Signed trial consistency correction

The first source packet and candidate remain exact historical evidence. Their
physical radial-return derivation is valid, but the original declarative
residual did not enforce its positive-radial-direction assumption. The
[independent review](../../reviews/j2-scientific-v1/README.md) found two roots:
at p_ref=100000 Pa, K=1e7 Pa, G=3e6 Pa, sigma_y=2000 Pa, H=1e6 Pa, zero parent,
and de=(0.001,-0.0005,-0.0005,0,0,0), both the physical stress
(1800,-900,-900,0,0,0), gamma=alpha=0.0007 and reversed stress
(-2250,1125,1125,0,0,0), gamma=alpha=0.001375 satisfy the original residual.
The reversed root has negative plastic work. Passing v1 numerical cases only
showed which root the generic solver selected; they did not validate uniqueness.

[Candidate v2](candidate-v03-v2.json) keeps the stress and history equations and
replaces the complementarity argument with
`c=(q_trial-3G gamma-sigma_y-H alpha)/p_ref`. Current-state `yield_scaled`
remains the initial admissibility check. This is the source's signed scalar
consistency equation, before taking the norm of the corrected stress. No
physical bound, calibration, numerical tolerance or source is changed.

Since alpha=alpha_n+gamma, put Y_n=sigma_y+H alpha_n>0 and D=3G+H>0.
Fischer–Burmeister gives gamma>=0, c<=0 and gamma*c=0. Thus the unique solution
is gamma=max(0,(q_trial-Y_n)/D). If plastic, q_trial-3G gamma equals
sigma_y+H alpha>0, so the radial factor is positive and the current-state yield
condition and associated flow follow. If q_trial=0, gamma=0 and the safe
denominator branch is inactive physically. The old reversed root now has a
nonzero complementarity residual and is rejected analytically and by a unit test.

Original candidate/model bytes, source closure, passing numerical reports and
the blocking review stay retained. The v1 live-model binding is preserved in a
content-addressed snapshot and its changed execution inputs have an archive map.
The separate [v2 study](execution-v2/PLAN.md) retains the original physical
budgets and adds the review witness plus actual propagated-history restart
checks. Its scientific judgment is a separate review identity.
