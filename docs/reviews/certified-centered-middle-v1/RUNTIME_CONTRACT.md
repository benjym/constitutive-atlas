# Proposed runtime contract — not implemented

Use the provisional name `principal_centered_mid_gt(A,w)` for the Boolean
predicate `3*lambda_middle(A)-trace(A)>w`. A is a six-component symmetric
Mandel tensor and w a scalar with identical physical dimensions. Both inputs
must have finite binary64 primals; w must be nonnegative. Negative zero is
zero. Equality returns false, including repeated spectra and hydrostatic zero.
Malformed shape, negative w, nonfinite operands and nonfinite Jet seeds are
evaluation failures, never a false or true physical answer.

This is a value-only Boolean for typed predicates and declared constraints.
It supplies no derivative of a Boolean or unique tangent at branch boundaries.
All seeds of every tensor and scalar operand must be checked before returning,
even though no derivative output is exposed. Preserve sticky failure flags,
caller output/state on failure, short-circuit/lazy branch semantics and
same-instance recovery. Test real 38-column seeded values rather than storing
zero derivative placeholders alone.

The operation concerns the exact real matrix encoded by its argument values.
Construct the centered tensor, trace, determinant and polynomial terms in exact
dyadic/radical arithmetic before any multiplication, subtraction or scaling can
overflow or lose bits. Reuse existing exact numerical infrastructure only after
separate qualification; do not form 3*A or a rounded threshold in binary64 and
then call an exact sign routine. Do not convert allocation/arithmetic failure
into a physical answer. No material ID is examined.

Dimensional inference must accept only `(sym, scalar)` with identical units and
return bool. Cover interpreter, normal generated C++/Wasm, double and real Jet
contexts, initial checks, residual domain, solution constraints, branch
expressions and permitted history consumers. Unused nine-model catalogue/header
bytes must remain unchanged. Archive all hash-pinned shared sources before edits.

The intended private Tresca branch is:

```
select(principal_range_le(trial_dev,width),0,
  select(principal_centered_mid_gt(trial_dev,width),1,
    select(principal_centered_mid_gt(-trial_dev,width),2,3)))
```

This applies the original strict mathematical inequalities; it is not a
non-strict equality workaround or a new material model. A future private record
must retain source identity, full sigma6/ep6 state, equations, parameters,
initial/solution constraints and all budgets. Width expressions such as `2*k`
can still overflow before reaching this primitive. Keep that explicit and do
not narrow source parameter domains to obtain a pass.

Freeze runtime acceptance before native/Wasm observations. Require exact
agreement with all 1,160 frozen design cases, equality neighbors, repeated
positive-root multiplicities, nonzero radical determinant terms and extremes;
malformed, finite-input, seed, sticky failure, no-output-on-failure and recovery
checks; type rejection and all generated contexts. Build one explicit serial
target at a time with `--parallel 1`, native then Wasm. Runtime qualification is
separate from a distinct private material qualification using all original
219 requests/all 38 columns, 12 continuous history steps and 29 laboratory
requests with unchanged gates. Preserve each earlier failed assessment.

No public model installation, UI work, deployment or scientific admission is
part of this capability task.
