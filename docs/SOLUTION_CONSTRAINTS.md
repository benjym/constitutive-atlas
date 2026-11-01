# Physical solution constraints

A v0.3 incremental residual model may declare `solution_constraints`, a nonempty array of Boolean DSL expressions. These describe admissible physical states separately from the mathematical domain in which residuals can be evaluated.

```json
"solution_constraints": ["principal_range_le(sigma,2*k)"]
```

Expressions may use material parameters, current persistent state fields and the identity tensor `I`. They must type-check as dimensionally consistent Booleans. Previous state, loading, increment, time, temporary solve unknowns and derived aliases are unavailable. Write the expression directly in terms of persistent fields and parameters. Rate laws and physical-time profiles currently reject this feature.

`domain` continues to define residual evaluation, including raw double and automatic differentiation calls. `initial_checks` continues to describe declared preparation checks. Neither implicitly becomes a solution constraint. Model authors must identify each contract from the source and declare it explicitly.

Python initialization and increment preparation reject inadmissible physical states. Generated C++ bindings validate state and parameter layouts, finiteness and parameter bounds before evaluating constraints. The solver checks its initial/reset iterate, backtracking candidates, converged state and final commit. Failed integration preserves the incoming full state. Observation and generated initialization calls also enforce the constraint. Raw residual and Jacobian calls remain available wherever the residual domain permits them, even outside the physical solution set.

This is a feasible-iterate Newton policy. It can reject a solve whose mathematical root exists if the current iteration cannot find a feasible descent path. It does not project or repair states, relax constraints with a tolerance, change the integration budget, or supply an independent equation verification.

Models without the feature retain their behavior. For the existing nine-model catalogue, generated header and catalogue bytes are unchanged. A dependent callback adapter supports older generated model structs without a constraint member.

The first compiled qualification is the private [Tresca v4 study](../catalogue/investigations/tresca-solution-constraints-v4/README.md). Passing its fixed numerical gates does not establish experimental validity or scientific admission. Laboratory controls and public activation require their own qualification.
