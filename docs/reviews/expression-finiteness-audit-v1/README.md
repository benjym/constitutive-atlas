# Executed-expression finiteness contract audit

Task: AUDIT-expression-finiteness-contract. Independent source-only review, 31 October 2026. Scoped to the coordinator's proposed generic Python executed-node wrapper and C++ `expression_or_mark` wrapper. No shared edits, generated code execution, native/Wasm builds, model admission or experimental validation.

## Decision

The proposed design is suitable for a prospective runtime study subject to the constraints below. It closes the specific class where an executed nonfinite AST child becomes a finite parent, boolean predicate, min/max result or selected value. Actual production implementation and compiled behavior remain unverified by this packet.

An executed AST node must produce a finite binary64 scalar, boolean, or six-component Mandel tensor; C++ Jet scalars require finite primal and all 38 derivative columns. Tensor checks include all six components and every Jet column, including components a consuming function would otherwise ignore. The wrapper is not a new dimensional or shape inference system. Names must retain their established symbol types; malformed external inputs still need frontend validation. Python booleans are legitimate predicate values but must not pass as tensor numeric components.

Python recursion must return through the checked public wrapper at every child, including Name and Constant. Arithmetic/domain exceptions reject the expression rather than being converted to an arbitrary finite value. A Sym must have exactly six components of finite accepted real numeric types. C++ must wrap every emitted node while retaining the exact returned type: a boolean stays boolean and Sym/Jet stay intact. Return by value; returning a reference to an expression temporary would dangle. The helper sets a shared flag false on failure and never sets it true. The root caller must inspect that flag even if the final output is finite.

`select` is lazy: evaluate condition, then exactly one branch. Invalid unselected branches must neither reject nor set the flag. `min` and `max` are eager: both arguments execute, and either invalid argument rejects regardless of which value is chosen. Arithmetic operands may be evaluated in different orders in C++; sticky failure is order independent. Flag mutation must remain inside called helper function bodies, whose executions cannot interleave under C++20; do not substitute unsequenced inline assignments into sibling operands. Do not introduce short-circuit early exits that change the stated eager contract.

## Important boundaries

1. This is **AST-result finiteness**, not a claim that every internal floating-point instruction is finite or that the exact mathematical expression lies in an admitted model domain. `apow` deliberately skips inactive derivative contributions; trace uses compensated/exact internals; functions may recover finite results internally. Do not infer a stricter primitive-internal rule from this contract.
2. Finite underflow to zero, finite subnormal values and signed zero remain allowed. Finite AD columns do not prove smoothness or derivative correctness. Existing `sqrt(0)` derivative conventions and negative-base power seed shortcuts remain separate numerical policies.
3. A valid primal can have nonfinite AD columns, including columns irrelevant to a later comparison or branch. Every executed child Jet must reject in that situation before the boolean destroys derivative information. Cover each of 38 columns independently.
4. Rejection is a status contract. Existing low-level out buffers are scratch and may contain finite or partial values after failure. Public solver/history rollback must be tested separately; a wrapper is not transactional storage.
5. Scale and observable-scale functions have a sticky flag and must return nonfinite scale output after any executed failure. Do not accept a finite `min`, predicate or reciprocal scale merely because the final expression is positive. Reset guards, initial/domain checks, derived fields, equation outputs, observable outputs, physical time and previous-state Names all need the same route.
6. The existing history interpreter preflights executed subexpressions and may reevaluate pure expressions. After the shared wrapper lands this is redundant but should preserve outcomes and lazy branches. Do not claim it proves single evaluation or eliminate historical code without a separate change.
7. This intentionally changes interpreter acceptance of previously masked invalid calculations. Scientific references using the interpreter must retain their original source identity and frozen observations. A newly passing engine does not retroactively replace a failed study or verify constitutive equations.

## Decisive prospective runtime corpus

Use the exact expression identifiers in `checks.json` as independently specified semantic witnesses. For `h=1e308`, `t=1e-308`, finite components `a=(h,-h,0,0,0,0)`, include product/sum/division/power/norm/dot overflow inside predicates; `exp(-h*h)`; `1/(h*h)`; eager min/max with invalid first and second argument; invalid square-root, logarithm, exponential and zero division; a tensor whose otherwise unused shear is invalid; and NaN/infinity Name operands. Include direct invalid leaf and output routes as well as hidden invalid children.

Controls must include both lazy branches and nested lazy selects with invalid unselected siblings, finite min/max, underflow, smallest positive subnormal, signed zero, boolean predicate and full finite Sym. Include all six tensor components and all 38 derivative columns, each independently poisoned, in generated double/Jet contexts. A selected valid primal with overflowing derivative, followed by min/max/comparison/zero multiplication masking, must fail; the same invalid calculation in an unselected branch must pass. Values with NaN, +infinity and -infinity all matter.

Run witnesses through each distinct generated entry point: domain, initial checks, derived, equations, observables, state scales, observable scales and reset guard/value. Test reset update values both when their guard fires and when it does not. Cover previous/current state, loading and physical-time input Names. Require rejection status, preserved caller-owned input bytes and immediate valid recovery. Use a distinct solver study for committed state/history rollback.

The standalone oracle is intentionally bounded; it does not prove production implementation correctness, C++ type compatibility, generated context routing, native/Wasm parity, integration behavior or source equation accuracy.

## Reproduce

```sh
python3 -B docs/reviews/expression-finiteness-audit-v1/check_contract.py
```

Observed: 31 expression assertions and nine malformed-value assertions pass. The oracle imports only Python standard library and contains its own bounded AST evaluator. `reviewed-inputs.json` records inspected source identities; those sources are expected to evolve under the coordinator. This packet is not a runtime source gate.
