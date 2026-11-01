# Required loading boundary: retained failed native conformance study

Task **AUDIT-declared-loading-boundary-v1**, coordinator, 1 November 2026. This is a synthetic common-engine study, not a model admission or constitutive comparison.

## Requirement and prospective policy

The [v0.3 formulation contract](../../../docs/FORMULATION_CONTRACT.md#explicit-input-declarations) says all declared inputs are required even when an equation does not reference them. A loading input declared `finite` therefore cannot contain NaN or either infinity merely because its value is unused. This interface requirement is separate from the executed-AST rule: unselected invalid *calculations* remain lazy and must not execute.

Three explicit v0.3 fixtures cover incremental residual, strain-path rate and physical-time ODE profiles. Their equations deliberately ignore loading, and stress is the only persistent state. They are verification fixtures, not added physical formulations. Their initialization/state semantics follow the current contract. [Preparation failures](preparation-failure.txt) retain four historical-template/profile mistakes corrected before any successful generation or build. [Python observations](python-observations.json) reject all54individual nonfinite loading inputs and recover immediately with finite loading.

[Protocol](protocol.json), all378literal expected rows, generated header, production source identities, frozen runtime headers and probe were [hash-frozen before building](pre-build-freeze.json). Expected rejection follows the declared finite-input contract; it was not selected after native observations. The native probe uses the production generator and frozen production evaluator/integrator headers, with no material-specific handwritten kernel. The persisted assessor was written after observation to reproduce the initial exact row comparison; the expected rows and acceptance policy remained unchanged.

## Result

**FAILED:126of378native rows disagree with the frozen policy.** Each disagreement is an invalid loading component accepted by a direct generated evaluator route:

| Route | Invalid requests | Unexpected acceptance |
| --- | ---: | ---: |
| Residual normal/check-only | 36 | 36 |
| Strain-path-rate normal/check-only | 36 | 36 |
| Timed normal/check-only/observable | 54 | 54 |
| Public legacy/timed integrators | 54 | 0 |
| Timed invalid-clock controls | 9 | 0 |

Every invalid request is followed by its own finite recovery:189recovery requests pass. All caller-owned input bytes remain unchanged in all378rows. Public constant-rate/constant-state fixture results retain the original stress state on rejection and recovery. This does not establish arbitrary nonlinear solver rollback or clock behavior beyond the recorded controls; existing transaction evidence remains separately scoped.

The generated C++ evaluator binds loading as `de`/`strain_rate` without an unconditional finite check. Executed-node wrappers do not inspect a symbol absent from the evaluated AST. Python's `evaluation_environment` preflights all six v0.3 components. Public integrators independently reject these nonfinite loading tensors, so this evidence establishes a low-level evaluator conformance mismatch, **not demonstrated acceptance through the browser or public integrators**. Scratch output on rejection remains unspecified.

One isolated Release native target built serially with `--parallel 1`, strict floating flags and no interruption. [Execution receipt](native/execution-receipt.json) pins the actual executable and commands; frozen inputs were checked unchanged afterward. Raw ordered [CSV](native/observed.csv), stderr and configure/build logs are retained. No Wasm build, public model change or deployment ran. NaN payload identity is not an output claim.

## Replay and next repair

Run from the repository:

```sh
python3 -B catalogue/investigations/declared-loading-boundary-v1/assess.py
```

The saved-only assessor verifies frozen inputs and compares every ordered row; successful replay prints the **failed** assessment, without building or executing the native artifact. It exits successfully when reconstruction succeeds; inspect `outcome`, not its exit status, for conformance acceptance.

Next claim a distinct generic repair: enforce the declared v0.3 finite loading boundary before derived/domain/check-only/observable routing. Preserve legacy acceptance unless a separately reviewed contract requires changing it. Specify primal-versus-Jet derivative scope explicitly rather than silently extending this double-input study. Preserve lazy internal expressions and scratch semantics. Freeze a new artifact/source/control qualification before observations, and check all54Python cases, direct evaluator routes, public rejection/recovery, existing model defaults and serial native/Wasm parity. No old failed study is relabelled or overwritten. Parent expression/transaction tasks remain open until their remaining scope is audited.
