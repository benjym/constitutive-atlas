# Post-ingestion constitutive verification

The existing **both-components-active** power-creep draft passes this bounded
history verification: 29 checks across 24 native integrations. No model or
solver change was needed. This supplements the prior 27 native and 27 Wasm
qualification requests and nine independent source-rate cases in
[execution-v1](../execution-v1/README.md).

The prospective [policy](policy.json), [independent references](reference.json),
script, model, source oracle and qualified binary hashes were frozen in
[freeze.json](freeze.json) before these compiled observations. The source oracle
uses ordinary Cartesian matrices and the source's creep strain-rate equation;
it does not evaluate the declarative model. Classical RK4 at 1024 and 2048 steps
per segment gives a maximum reference difference of 3.49e-9 Pa. This is a
step-refinement diagnostic, not a rigorous error bound.

The path uses noninteger exponents 1.5 and 2.2, general six-component loading,
reversed loading, volume loading and a final strain hold. All knot stresses agree
with the reference within 0.001983 Pa against the predeclared 0.06 Pa gate.
Explicit state/time restart at each segment midpoint, shifting the clock by
100 seconds, changing reference stress with the corresponding coefficient
transformation, and changing the observable time scale all pass the same gate.
Maximum invariance difference is 0.000173 Pa. Restart tests reuse the integrator's
0.1-second maximum step and happen to reproduce the baseline partition exactly;
they check explicit state continuity, not arbitrary adaptive checkpoint recovery.

For the hold, elastic stored energy
`psi = p^2/(2K) + (s:s)/(4G)` decreases by about 165.09 J/m3 in every variant.
The source gives `psi_dot = sigma:D - q*f`; hence `D=0`, `A_i>=0` implies
nonincreasing energy. This checks endpoint dissipation for these paths, not a
universal numerical stability guarantee. See [report.json](report.json) and
unaltered [raw requests and outputs](raw/).

Reproduce the independent reference in a fresh copy of this directory with
`python3 verify.py prepare`, then `python3 verify.py observe` after checking the
private binary path. Both modes refuse to overwrite their existing evidence.
The pinned prior execution manifest confirms the same native and Wasm artifact
identities; [prior-evidence-check.json](prior-evidence-check.json) records replay
of all its file hashes. No rebuild or additional browser work was required.

Source completeness: only the separately identified both-active specialization
is executable. The thresholded family still needs equality/event/source decisions.
Executable status: draft, working in the tested scope. Numerical verification:
passing at the specified strict settings; earlier loose-setting accuracy failures
remain preserved under execution-v1. Scientific admission: unchanged, not granted.
These illustrative parameters are not a material calibration. The next broader
step is independent scientific review or source closure for threshold switching,
not promotion based solely on these numerical checks.
