# SANISAND-2004: fixed-memory backward-Euler research material

Status: **executable research draft; independent review pending**. The [26-component definition](../../models/research/sanisand-2004-fixed-memory-be.json) runs through the existing model compiler and common C++ solver, without model-specific engine code. It remains outside the public catalogue. It implements an initial monotonic branch with fixed `alpha_in`; it does not implement SANISAND reversals or satisfy the complete six-model admission gate.

The continuous equations come from [Dafalias and Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29), extracted in the [original-paper dossier](sanisand-2004-original.md). Parameter defaults are the Table 1 Toyoura values, with the explicitly chosen audit normalization `p_at=100000 Pa`. The isotropic initial stress `100000 I Pa`, current `e=0.7`, and zero histories are project demonstration initialization, not a recreated source experiment. Parameter bounds in this research definition are software audit bounds, not a complete physical/calibration domain.

## Finite product residuals

Retain 25 persistent components: `sigma[6], e, alpha[6], fabric[6], alpha_in[6]`. Add a dimensionless transient multiplier `gamma`. For an endpoint state, write

```text
d = (alpha-alpha_in):n
b0 = G0*h0*(1-ch*e)*(p/p_at)^(-1/2)
gamma = Delta_lambda*h_endpoint
Delta_lambda = gamma*d/b0
```

At finite positive `d`, this exactly rearranges `h=b0/d`; no hardening cap or epsilon denominator is used. The endpoint residuals are

```text
sigma-sigma_n = 2*G*dev(Delta_epsilon)+K*tr(Delta_epsilon)*I
                -Delta_lambda*(2*G*Rdev+K*D*I)
alpha-alpha_n = (2/3)*gamma*(alpha_b-alpha)
fabric-fabric_n = -cz*max(-Delta_lambda*D,0)*(zmax*n+fabric)
e = (1+e_n)*exp(-tr(Delta_epsilon))-1
alpha_in = alpha_in_n
```

`G,K,alpha_b,D,Rdev` use the endpoint state and original continuous expressions. The exponential void-ratio update exactly integrates the project's constant-solid-volume closure for a straight total-strain increment; this closure is an explicit inference, not a numbered source equation. The other equations are project backward-Euler discretization choices.

With `F=(norm(s-p*alpha)-sqrt(2/3)*p*m)/p_at`, the multiplier residual is `sqrt(gamma^2+F^2)-gamma+F=0`, encoding `gamma>=0`, `F<=0`, `gamma*F=0`. On the supported branch (`b0>0,d>0`), this selects the same active surface as complementarity in `Delta_lambda`. At `d=0`, the finite-product equations remain evaluable, but general singular-state uniqueness/admissibility is not established by this experiment. The [regular one-sided continuous limit](sanisand-2004-hardening-limit.md) is separate evidence. Do not infer that every zero-distance or simultaneous-zero state is solved.

Off the cone, the research definition uses `n=(r-alpha)/norm(r-alpha)` where the norm is positive, and `n=0` at the cone centre. This is an explicit project extension for elastic prediction and nonlinear iterations. `Rdev=dev(B*n-C*tensor_square(n))` matches the published flow on the unit-normal cone and avoids an artificial trace at the zero-normal fallback. No claim is made for a unique derivative at the centre. The model uses current `e` elasticity, not the pinned OpenSees implementation's frozen initial density factor. The stress residual uses the uneliminated elastic/plastic relation, so the printed Eq. (20) numerator omission is not copied into a loading-index formula.

The shared solver supplies AD residual Jacobians, its existing elastic predictor, damped Newton steps, recursive cutbacks and transient resets. It uses its existing scaled residual tolerance `2e-10`; no integration defaults changed. A residual Jacobian is not an exposed algorithmic tangent. A solved backward-Euler step alone supplies no truncation-error bound.

## Memory and transaction boundaries

The original paper, p. 631 after Eq. (24), updates `alpha_in` when `(alpha-alpha_in):n` becomes negative and refers to [Dafalias (1986)](https://doi.org/10.1061/%28ASCE%290733-9399%281986%29112%3A9%28966%29). The 1986 paper's publisher metadata was located, but its full rules have not been obtained or reviewed. The supplied downloads contain the 2004 paper, not that 1986 source.

The pinned OpenSees [`integrate()`](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/ManzariDafalias.cpp#L858) instead tests `(alpha_n-alpha_in_n):(Ce*Delta_epsilon)` before internal integration. This is a parent prediction, not evaluation of the current source cone normal. Existing [parent reset support](../PARENT_INCREMENT_RESETS.md) can represent that explicit algorithmic scope, but it does not settle the original model's event rule.

This research material therefore freezes `alpha_in` and requires nonnegative `d`. It contains no reset object. It is restricted to the initial loading branch; reversal can fail, and any successful reversed calculation would not establish correct reversal physics. No canonical policy has been silently selected. The original trajectory investigation did not exercise failed-step rollback; the subsequent transaction investigation below supplies that material-specific evidence. The memory event contract, first-yield splitting, nonsmooth derivatives and rollback-specific material cases remain SAN-03/05 work. The separate [exact elastic-entry reference](sanisand-2004-elastic-entry.md) is not yet wired into this residual update.

The model's domain additionally requires positive `p`, `0<e<2.97`, `1-ch*e>0` and nonnegative `gamma`; initialization requires `F<=1e-8`. The current definition explicitly requires `abs(trace(alpha))`, `abs(trace(fabric))` and `abs(trace(alpha_in))` to be at most `1e-12`. This dimensionless audit tolerance is a project numerical choice. It rejects invalid input without projecting or modifying it, and applies at solver trial states as well as parents. No pressure floor or low-pressure dilatancy correction is used.

## Execution evidence

One standalone C++20 `-O0` compilation with Apple clang 21.0.0 and a separately executed native probe completed normally. Three straight constant-volume paths (triaxial compression, extension, and general Mandel shear) run to total strains defined in the [probe](../../tests/native/sanisand_fixed_memory.cpp), each with 16, 32 and 64 caller increments. All **336 increments** succeed with one accepted internal substep each. All exercise positive plastic multiplier/history evolution.

The [manifest](../../catalogue/investigations/sanisand-fixed-memory-be-v1/manifest.json) pins model, compiler/engine sources, generated header, binary, and retained compressed full trajectories. A [Python verifier](../../tools/verify_sanisand_fixed_memory.py) re-evaluates every native state with the interpreted equations, checks residuals, nonnegative multipliers, fixed memory and deviatoric history, and checks endpoint refinement. Largest scaled residual: `1.5356e-10`, below the existing `2e-10` solver threshold. Successive endpoint-change ratios under step halving are approximately `0.532`, `0.518` and `0.523`, consistent with first-order convergence on these paths. This is convergence evidence, not an independent reference solution or full integration error estimate.

Four [Python test groups](../../tests/test_sanisand_fixed_memory.py) additionally check capacity/public-catalogue exclusion, zero-increment interior equilibrium, and first-order consistency with the separately transcribed original continuous rates for compression, extension and general shear. Substituting a forward continuous-rate increment into the new endpoint residual gives an error decreasing quadratically as the increment halves. Tampered or incomplete native evidence is rejected. The complete current SANISAND Python suite passes 19 groups.

Reproduce without automatic compilation:

```sh
python3 tools/verify_sanisand_fixed_memory.py prepare /private/tmp/atlas-sanisand-residual-small
c++ -std=c++20 -O0 -Icpp/include -I/private/tmp/atlas-sanisand-residual-small/generated /private/tmp/atlas-sanisand-residual-small/probe.cpp -o /private/tmp/atlas-sanisand-residual-small/probe
/private/tmp/atlas-sanisand-residual-small/probe > /private/tmp/atlas-sanisand-residual-small/output.json
python3 tools/verify_sanisand_fixed_memory.py verify /private/tmp/atlas-sanisand-residual-small/output.json --output /private/tmp/atlas-sanisand-residual-small/verification.json
```

Preparation, compilation and execution are separate operations for gradual native testing. Full OpenSees compilation remains deferred. No Wasm, experimental agreement, independently reviewed trajectory, reversal, material tangent or public website execution is claimed. SAN-01/03/05/06 and the broader roadmap remain open.

## Subsequent domain and transaction verification

The [transaction record](../../catalogue/investigations/sanisand-transactions-v1/manifest.json) pins the strengthened definition, [native harness](../../tests/native/sanisand_transactions.cpp), compiler/engine sources, generated header, binary and complete input/output states. Three nondeviatoric-history cases fail before any Newton iteration. A 16-increment preload prepares a plastically loaded state; the harness then assigns a nonzero, deviatoric frozen anchor inside the existing audit domain for explicit memory-restoration coverage. This assignment is manufactured test preparation, not a proposed physical reversal rule. Successful nonzero and zero trials read this parent independently.

A large isotropic expansion requests an inadmissible full endpoint under the declared void-ratio/hardening domain. The actual solver accepts two internal substeps before ultimately failing after 15 rejected attempts and 278 Newton iterations. The returned state equals the complete original parent, including nonzero reversal memory and the previous transient multiplier. A subsequent repeat of the earlier successful trial returns exactly equal numeric state values. These observations verify rollback and isolation; they do not prove the physical failure location or that the requested path is valid up to that location.

An earlier compression fixture failed before accepting internal work, so it did not establish late rollback; its failed harness assertion is retained in the new manifest. Both small compilations and executions completed normally. The retained successful matrix has seven cases. Six fixed-memory Python groups now pass, and all SANISAND Python groups total 21. The earlier 336 native trajectory results remain immutable historical evidence; Python re-evaluation confirms those states satisfy the new trace conditions, but that native matrix was not rebuilt for this change.

Prepare with `python3 tools/verify_sanisand_fixed_memory.py prepare-transactions /private/tmp/atlas-sanisand-transactions-small`; compile `probe.cpp` with the same include paths as above, then run separately. Validate its JSON output with `python3 tools/verify_sanisand_fixed_memory.py verify-transactions OUTPUT.json --output REPORT.json`. Preparation and verification never invoke a compiler or executable. Reversal reset, located events, mixed controls, Wasm and complete-update tangents remain unverified.
