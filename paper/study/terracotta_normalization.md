# Mesoscopic normalization audit of the Figure 1 transcription

Status: paper-side derivation from the pinned declarative equations; assisted numerical check, independent review pending. This is not an assertion that the journal establishes an identifiable nine-parameter calibration problem. Scope is the simplified Figure 1 draft in `models/research/terracotta-2024-fig1.json`, not Appendix B or another Terracotta variant. Exact definition identity is recorded in `model_annotations.json`.

Let k be a positive constant. Apply the coordinated transformation

\[
T_m^*=kT_m,\quad \alpha^*=k\alpha,\quad \gamma^*=k\gamma,
\quad \eta^*=\eta/k,\quad \Gamma^*=k^2\Gamma.
\]

All elastic strains, solid fraction, physical time, imposed rates and other coefficients remain unchanged. The mesoscopic initial state must be transformed too. If the initial state is zero temperature, it remains zero.

The temperature equation transforms covariantly: its right-hand side is multiplied by k, exactly as its left-hand side. The transport coefficients a, b and c each acquire 1/k, so their products with temperature remain unchanged. Viscous pressure/shear terms and mesoscopic pressure are unchanged:

\[
\frac{\alpha^* T_m^*}{\Gamma^*}=\frac{\alpha T_m}{\Gamma},\quad
\frac{\gamma^* T_m^*}{\Gamma^*}=\frac{\gamma T_m}{\Gamma},\quad
\frac{(T_m^*)^2}{\Gamma^*}=\frac{T_m^2}{\Gamma}.
\]

The material equations can therefore use \(S=T_m/\sqrt{\Gamma}\) and the invariant combinations

\[
A=\alpha/\sqrt{\Gamma},\quad C=\gamma/\sqrt{\Gamma},\quad H=\eta\sqrt{\Gamma},
\qquad \dot S=A D_v^2+C D_s^2-HS^2.
\]

This identifies one scaling redundancy among four declared rheological entries when mesoscopic temperature has no independently fixed measurement convention. Six other declared coefficients plus at most three independent rheological combinations gives an upper bound of nine material combinations. It does not prove that all nine can be identified, that a particular experiment supplies them, or that no other parameter dependencies exist. Fixing Gamma alone is a convention only if the other entries and temperature coordinates are interpreted consistently; changing Gamma alone while holding them fixed changes the response.

The role count in the annotation classifies alpha, gamma and eta after choosing a normalization and lists Gamma separately, with this qualification. The independent-material-dimension value remains unknown. Parameter guardrails may restrict admissible k; they do not remove the mathematical redundancy from the underlying equations. Numerical temperature scales and tolerances also need consistent transformation for a trajectory-level numerical comparison.

`analysis/terracotta_normalization.py` provides only the paper transformation. `tests/test_representation.py` evaluates the actual atlas interpreter at two nonzero-temperature states, positive/negative signed shear states, three prescribed rates and three k values. It checks RHS covariance, every algebraic stress observable and the invariant coefficients. A separate check confirms that changing Gamma alone changes pressure. This tests an equation-level identity; it does not verify a new integration algorithm, author-code equivalence or experimental validity.

The survey implication is practical: distinguish declared entries, normalization choices, independent material combinations, actually fitted quantities and initial-state nuisance quantities. A parameter-count leaderboard would miss this distinction.
