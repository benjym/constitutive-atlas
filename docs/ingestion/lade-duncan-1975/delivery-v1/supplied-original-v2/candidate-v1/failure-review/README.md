# Independent native-failure review v1

Task REVIEW-lade-duncan-native-failure-v1; separate reviewer run `/root/lade_source_review`, 2026-11-01. Owned output is only this `failure-review/` directory. This run did not author the candidate, frozen policies, independent scalar reference or native studies. It read those artifacts, inspected frozen generic runtime source and ran Python interpreter/exact-rational probes only. No compiled artifact was executed, no generic file changed, and no E5/model acceptance is supplied.

## Verdict

Candidate `lade-duncan-1975-local-eq19-be-v1`, SHA-256 `5d02250d99a70bf0dbb0783e098ccb8738544b5e04de876f0d295057036ec8c1`, remains numerically unqualified. The frozen native refinement study fails: 24 requests, seven successful, seventeen unsuccessful. Successful build and endpoint residual checks do not override that failure.

The reported parent-reentry diagnosis is independently reproduced for all six finest-refinement plastic cases. Last committed states satisfy ordinary equation/domain evaluation but violate the strict parent `initial_checks: h>=f`. Even zero-increment preparation rejects them. The frozen native solver can accept a sufficiently small residual for the algebraic history equation without enforcing that strict reentry predicate on the accepted endpoint. This is a concrete lifecycle/representation mismatch, not unavailable source, a missing minimum primitive or proof that the original constitutive equations lack a solution.

This establishes the next-call blocker for those six retained states. It does not prove that all seventeen failed trajectories have only this cause, nor that removing it will make the remaining frozen reference/refinement gates pass.

## Candidate fidelity and scope

The candidate is an explicitly bounded numerical realization of the readable original1975 source. It retains the full elasticity, nonassociated flow and local Eq19 work evolution, rather than a criterion-only model or the1977 curved-surface extension. I checked the following against the independently reviewed source crosswalk and the actual definition:

- Stress is normalized by pa. `E=Kur*pa*smin**n` and `a=M*pa*smin**l` therefore use current sigma3/pa consistently. The source's Pa^-2 flow factor becomes dimensionless `gamma=(dwp/pa)/(3*gbar)`, multiplying the dimensionless fixed-κ2 gradient. No κ2-composition derivative was substituted for that flow gradient.
- `smin` uses the already-reviewed lazy minimum expression with cluster-average Clarke derivative at exact ties. That is an explicit numerical choice and has unresolved broader near-tie/path qualification; the retained diagnostic is independently reproduced without a spectral exception. It should not be relabeled a missing scalar spectral capability.
- Endpoint coefficients and `dwp=a*max(f-h_n,0)/den**2` are the declared backward-Euler local Eq19 rule. This is consistent with the policy, with newly reached stress level measured above committed history already at least ft. It is not the globally algebraic changing-pressure Wp curve, and it introduces no da term.
- The total Cauchy-stress binding is explicitly restricted to uncoupled zero-pore-pressure mechanical interpretation, fixed-frame infinitesimal kinematics and the two Table1 example sets. Under that restriction it is a disclosed Atlas embedding, not an assertion that the paper prescribes general total/effective decomposition or a fluid law. Do not expand it to undrained/coupled behavior or arbitrary mixed parameter sets merely because broad parameter bounds validate numerically.
- `h-max(h_n,f)=0` has the intended exact-arithmetic source history meaning. `initial_checks h>=f` is a necessary representation invariant for this direct h encoding, since otherwise `max(f-h_n,0)` can manufacture plastic work on a hold. Rejecting f>k1 is the disclosed pre-failure boundary, not post-failure continuation.

No new equation-fidelity defect is identified by this scoped review. This is not an all-nine-item scientific approval: arbitrary3D loading, history reversals, derivatives, rollback/restart, Wasm and browser delivery remain unqualified.

The independent scalar triaxial reference was read. Its stress-ratio derivative, fixed-κ2 axial/radial normals, threshold split and constant-pressure hyperbola work agree algebraically with the source. Eight reference convergence results pass their frozen policy; I did not rerun the reference script and overwrite its evidence. Agreement of coarse/fine quadrature is bounded numerical convergence, not experimental validation or a proof of every untested reference path.

## Reproduced evidence

`check_failure.py` verifies all27 files in the immutable native-source manifest and all24 raw response hashes. It reproduces the candidate hash, request/success counts and failed study status; reads the last raw point independently of the coordinator's onset summary; then evaluates the exact definition and calls existing Python `prepare_increment` on that point with zero loading. `failure-results.json` retains full details.

| Example / target | Last h−f | Prior native scaled residual | Zero preparation |
| --- | ---: | ---: | --- |
| Dense /0.001 |−7.105427357601002e−15|1.778583311826639e−15|Rejected |
| Dense /0.002 |−1.4210854715202004e−14|2.534426872388222e−15|Rejected |
| Dense /0.005 |−7.105427357601002e−15|2.9846651783292756e−15|Rejected |
| Loose /0.001 |−5.867200059128663e−9|1.7779394118571707e−10|Rejected |
| Loose /0.002 |−7.105427357601002e−15|5.145518027615796e−15|Rejected |
| Loose /0.005 |−7.105427357601002e−15|5.596510178551611e−15|Rejected |

All prior native residuals are below the frozen2e−10 solver tolerance. Every zero-preparation probe raises `ValueError: inadmissible parent state`, and every rejected input remains unchanged. Ordinary model domain/evaluation passes. In the loose0.001 case, bypassing the initial predicate would expose a zero-input residual norm about3.45e−9 and a newly computed plastic work increment about2.19e−7Pa. Thus simply deleting/tolerancing the predicate is not an equality-preserving fix. Five ulp-scale examples likewise have small spurious positive work; their smallness does not justify silently changing the declared invariant or hold gate.

Frozen source confirms the mechanism: the generated evaluator guards `h>=f` only when `check_initial` is true. Native `integrate` calls `domain(...,true)` for the incoming parent. `implicit_step` accepts on residual convergence plus `solution_admissible`; candidate-v1 declares no `solution_constraints`, and the endpoint is not rechecked as a future initial parent. Python preparation independently enforces the same exact initial predicate. This is a distinction between residual convergence and valid reentry, not a claim that the rejected next step ran to nonlinear convergence and then failed.

## Why a strict all-trial constraint alone is insufficient

The existing generic solution-constraint mechanism can encode the physical inequality, but the solver checks it at every trial, not only on commit. Adding it to a new identity strengthens acceptance without relaxing any gate; it is not established as a successful remedy.

For fixed radial pressure and triaxial compression, let r=sigma1/sigma3. Then

```
f(r)=(r+2)^3/r = r^2+6r+12+8/r
f''(r)=2+16/r^3 >0
```

Starting on the active history manifold `h=f(r)`, the linearized history equation gives `delta_h=f'(r)*delta_r`. Strict convexity implies `h+delta_h < f(r+delta_r)` for every nonzero finite tangent displacement that remains at positive r. Every finite backtrack of that direction violates the trial constraint. The exact-rational witness starts at r=3, h=125/3, derivative100/9; all twelve dyadic backtracks in the retained probe fail strict feasibility. Threshold crossings can similarly encounter a max-branch feasibility obstacle. This is a directional counterexample, not a new compiled-run result or proof that every constrained algorithm fails.

An exact commit/reentry check in the common lifecycle would correctly prevent publishing unusable endpoints, but by itself can turn acceptance into rejection without creating a convergent route. A legitimate generic solution would need an explicit equality-preserving algebraic-history treatment, feasible nonlinear step method or equivalent representation, with its own prospective study and transaction checks. No h projection, epsilon allowance, skipped check or post-hoc gate relaxation is justified here.

## Smallest viable new-study route

The coordinator's proposed explicit carrier representation is algebraically defensible and can be attempted model-locally under a **new candidate/study identity**:

```
H   = max(ft, f(S)   + max(q,0))
H_n = max(ft, f(S_n) + max(q_n,0))
drive = max(f(S)-H_n,0)
q equation: q-max(H_n-f(S),0)=0
```

Here q is a signed numerical history carrier, not the physical maximum. H is the decoded physical history. Nonpositive q values are explicitly many-to-one encodings of zero excess. In exact arithmetic at a solved nonzero increment, `q=max(H_n-f,0)` and hence `H=max(H_n,f)` since H_n>=ft. The original source maximum-history update follows. For every finite signed encoding, decoded H>=f is structural, so an approximate carrier residual cannot create the direct-encoding reentry defect merely by undercutting current f. Initial isotropic canonical q=ft−27 corresponds to the same source prepared example.

This is an explicit change of state representation, not silent clipping of physical H or overwriting candidate-v1's failed state. It requires clearly named serialized carrier semantics, decoded physical history in evidence/UI, and fresh hash bindings. It does not guarantee finite-precision history monotonicity, Newton convergence or path qualification in advance.

A concrete caveat must be retained: at f=45,ft=40,q=−0.001, decoded H=45 but the canonical carrier equation on zero input targets q=0. Physical history is unchanged while raw persistent state changes. The existing hold policy checks all persistent state, so this is not automatically a passing representation. An explicitly frozen zero-mechanical-increment branch preserving q_n is source-neutral representation handling and could satisfy that gate; its numerical behavior must be tested. Do not weaken the hold metric or silently exclude solver-returned signed encodings after observing a failure.

The smallest next action is therefore a coordinator-owned new candidate using a fully declared carrier/zero-hold contract, followed by the unchanged triaxial reference bounds and required-success/refinement gates. Preserve candidate-v1 and all its failures. Before compiled observation, freeze signed/canonical state cases, threshold and prior-maximum crossing, constant-f and varying-pressure paths, unloading/reloading, physical-H monotonicity/error bounds, full raw-state zero hold, repeat/retry, restart and failed-step rollback/recovery. Native/Wasm builds remain separate serial coordinator handoffs. A generic runtime change is needed only if this concrete new representation study exposes an actual remaining capability gap.

## Handoff

Source remains readable and complete at the available-article level. Candidate-v1/native study remains failed. No E4 complete, Wasm, E5 approval, public atlas, browser, live delivery or new experimental validation is claimed.

Reproduce only the read-only Python challenge from the repository root:

```
python3 -B docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/candidate-v1/failure-review/check_failure.py
```

`review-receipt.json` binds this report, probe/results, exact candidate/policies/references/native reports, raw response bindings and inspected runtime inputs. No original evidence was overwritten.
