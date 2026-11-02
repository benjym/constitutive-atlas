# Notation correction to the retained failure diagnosis

The opening scalar reduction in `execution-v2-failure-review-v1/REPORT.md` contains a prefactor typo. With `N=(2/3,-1/3,-1/3,0,0,0)`, the correct stress is **s = N z**, not `s = (3/2) N z`. Thus `N:N=2/3`, `q=|z|`, and `sigma_xx=(2/3)z` for the trace-free channel-0 cases. The flow is `eps_vp_prime=(3/2)N sign(z) (|z|-Y)+/eta`.

The retained script, source ODE, reference conversions, numerical values, estimator reconstruction and diagnosis already use this correct convention. They are unchanged. The original report is preserved with its original artifact hash; this erratum supersedes only the incorrect stress prefactor in its opening explanatory sentence.
