# SANISAND-2004 capability analysis

This is SAN-02 planning evidence grounded in the [source brief](models/sanisand-2004.md) and the current Atlas implementation. The [original-paper dossier](models/sanisand-2004-original.md) and typed algebra fragment now map the continuous equations; initialization, singular limits, domains and independent review remain incomplete. This is still a provisional gap analysis, not permission to close SAN-01 or promote an unreviewed variant. The [machine-readable probe report](../catalogue/investigations/sanisand-capabilities-v3.json) records synthetic capacity/type observations; it does not execute SANISAND.

## Current engine versus required representation

| Requirement | Current capability | Gap / proposed next action |
| --- | --- | --- |
| 25 persistent scalar components; 26 with a residual multiplier | Semantic validation now allows 32; `Jet` allocates 32 state derivatives plus six control derivatives | [Capacity checks](STATE_CAPACITY.md) exercise a 32-state, six-control joint solve, all 38 AD columns and schema/ABI overflow rejection. The proposed layout fits without deleting memory. |
| Stress plus several deviatoric tensors | Six-component Mandel `sym`, scalar fields, `dev`, `trace`, `dot`, `norm`, `cube_trace` | Existing operators cover much of the algebra. [Engineering-shear conversions](models/sanisand-2004-conventions.md) now have Cartesian work and full tangent-action tests. Deviatoric constraints still need model-level admission checks. |
| Symmetric tensor square | [`tensor_square(sym) -> sym`](TENSOR_SQUARE.md) now passes Cartesian, AD and Python/native/Wasm checks; arbitrary multiplication remains rejected | The demonstrated algebraic gap is resolved. Output dimensions double. History semantics remain unresolved. |
| Reversal memory | [Experimental parent-increment resets](PARENT_INCREMENT_RESETS.md) now read an immutable committed snapshot and freeze selection through internal solves | This explicit scope is verified synthetically. Canonical SANISAND selection, source reconciliation, initialization and any need for located events remain open. |
| Elastic/plastic switches and finite singular limits | Residual complementarity, rate laws, branch expressions and domain rejection exist | Decide rate versus residual formulation after source extraction. Specify zero normals, reversal hardening limits and derivative choices; do not silently borrow external cutoffs. |
| Pressure/state-dependent elasticity | Units, scalar powers and parameterized tensor expressions exist | No demonstrated algebraic extension required. Distinguish evolving void ratio from an implementation's frozen initial value. |
| Failure and accepted-substep transactions | Failed increments return the original state; trial solves start from a supplied snapshot | Extend transactions to any future discrete memory and event log, not only numerical state. |
| Reference comparison | Native/Wasm common engine and evidence envelopes exist | Pin source variant, initialization, integration/projection options and tolerances before comparing curves. |

The natural 25-component layout is `sigma[6], e[1], alpha[6], fabric[6], alpha_in[6]`. It now fits the 32-component bound, including a residual multiplier. Historical v1/v2 probes recorded rejection at 25/26; v3 accepts 24, 25, 26 and 32, and rejects 33. These probes isolate representational capacity without presenting placeholder equations as a constitutive model.

## History semantics to settle in SAN-03

The current recursive legacy integrator passes the most recent accepted substep as `_n`. A rejected branch restarts from its own input state; the top-level result rolls back on failure. That is adequate for continuous state equations, but it does not establish whether a reversal reset belongs to a user increment, an accepted substep or a located physical event.

The pinned external implementation resets reversal memory before calling its integration scheme. Matching that behavior per parent call is different from re-running its guard at every internal half step. Neither choice should be mistaken for a universally partition-independent physical rule. The original publication and controlled reversal tests must resolve the intended formulation.

Before writing a schema extension, specify:

1. **Guard inputs:** committed parent state, current accepted substep, trial endpoint or loading direction; state which quantities are frozen during Newton and error-estimator probes.
2. **Guard boundary:** behavior at zero, tolerance units/scales, loading/unloading sign, repeated detection prevention and simultaneous-event ordering.
3. **Reset transaction:** memory assigned from the appropriate pre-event snapshot; rejected probes must not mutate it. Define whether a reset occurs before continuous integration or at a located event.
4. **Subdivision:** parent-versus-substep semantics, event-location tolerance if needed, and retry behavior when a cutback straddles reversal.
5. **Rollback and differentiation:** restore all state and logs on failure; hold discrete choices fixed within a smooth Newton branch and state how branch-boundary derivatives are handled.

Do not approximate this contract with an external script changing parameters between otherwise stateless model calls. The accepted constitutive definition and common engine must own its memory semantics.

## Verification required for the minimal extensions

For state capacity, exercise an actual 26-component fixture through Python, generated native code and Wasm, including the highest state derivative column and all six mixed-control columns. Reject a definition exceeding the chosen bound before indexing AD storage. Compare existing five-model numerical references and protocol results within their already declared tolerances.

For tensor square, compare ordinary Cartesian matrix products with Mandel conversion for diagonal and fully sheared tensors; check dimensions, off-diagonal factors, oblique rotations and finite-difference/AD derivatives. A scalar squared norm is not a valid substitute.

For history transactions, use a small synthetic history model whose exact resets are known. Exercise reversal at a step boundary and inside an increment, failed/rejected probes, recursive cutback, repeated outer control trials, multiple reversals and exact rollback. Compare one prescribed path under different user partitions according to the declared semantics. These tests must run before SANISAND is used to justify the extension that it depends on.

## Reproduction and status

```sh
python3 tools/inspect_sanisand_capabilities.py --output /tmp/sanisand-capabilities.json
```

The report includes observed acceptance/rejection messages and hashes of the relevant Atlas sources. It is a capability investigation, not a numerical-evidence envelope or independent review. The probe makes no runtime/schema changes. Its v3 observation follows the capacity expansion; v1/v2 remain historical evidence of the earlier capacity and algebra gaps. SAN-01–04 remain open until the source and contracts are complete and the demonstrated extensions pass their acceptance checks.

## Selected reference-function execution

The [conventions and state-function audit](models/sanisand-2004-conventions.md) now maps source storage, pressure units and the exact selected corrections. Its [87-case report](../catalogue/investigations/sanisand-source-functions-v1.json) checks unchanged source methods in a private minimal adapter against Cartesian algebra. The low-pressure dilatancy correction is numerically unit-dependent; current void ratio is ignored by elasticity; hardening uses a signed denominator outside its singular guard. These observations constrain variant selection and reference parameters. They do not establish full integrator behavior or close original-paper extraction, canonical history/initialization, transcription or independent review.

## Derived infinite-hardening products

The [finite-product investigation](models/sanisand-2004-hardening-limit.md) represents the one-sided regular zero-distance limit using existing scalar/tensor expressions; no infinity literal, cap or new DSL operator is needed for that branch. The [separate draft](../catalogue/source-audits/sanisand-2004-hardening-limit.json) is Python-verified. Simultaneous-zero limits, general initialization, first yield, reversal events and finite-step integration remain unresolved; this result does not close SAN-01/03/05.

## Common-solver residual research execution

The [fixed-memory research material](models/sanisand-2004-fixed-memory-be.md) now demonstrates a 26-component backward-Euler formulation using existing DSL and AD solver features. The rearranged `gamma=Delta_lambda*h` products avoid separate division by reversal distance on the tested initial loading branch. A small native build passes 336 increments with interpreted residual and first-order refinement evidence. Memory remains fixed; the original cone-normal reset rule is not replaced by the external parent trial-direction rule. This advances SAN-05 but closes neither reversal/event semantics nor full material admission.
