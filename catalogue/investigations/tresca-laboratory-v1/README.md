# Private Tresca laboratory qualification, v1

**Qualification failed on both native and Wasm.** This is a bounded laboratory study of the unchanged private [v4 solution-constrained candidate](../tresca-solution-constraints-v4/README.md), not an installed public model or a scientific admission.

The prospectively frozen corpus has 29 API requests and recovery after every request. It covers all five laboratory protocols with isotropic and nonzero plastic-history initial states, loading/reversal/hold paths, a deliberately unattainable stress target, legacy total-scope rejection and malformed or inadmissible requests. Full sigma6/ep6, cumulative strain6, exact control wires, response scope and unavailable pore pressure are checked. The driver includes the exact production `cpp/main.cpp` and headers; the candidate goes through ordinary generation with no model-specific kernel or scope override.

Before compilation, the independent standard-library Fraction recurrence produced 12 reference paths and 510 exact Hooke-law component certificates. It checks yield clipping, normality direction, plastic incompressibility and mixed-control constraints. Laboratory accuracy gates are explicit in `policy.json`, including the existing outer controller's stress tolerance. They are distinct from the previous one-step/derivative study; no earlier gate or assessment changes.

Each backend completed all 29 requests with 29 successful same-instance recoveries. There are 1,710 state/strain comparisons and 95 exact actual-commit yield-membership checks, agreeing with the independently implemented Sturm check. Maximum stress error is about 1.99e-7 Pa and strain/plastic error about 2.04e-10, within the frozen budgets. All returned physical points are admissible. Scope, rejection and deliberately failed stress-control prefix checks pass.

The single unexpected failure is `isotropic-0`: axial strain control with zero lateral strain stops at step 7, retaining seven points instead of nine. The other ten expected-success paths finish, including all mixed-control paths. The unattainable stress request correctly stops at step 4 with four points. The saved assessor returns false for the whole qualification; partial accuracy and software passes do not override the missing path.

The separate post-observation `reversal-diagnostic.json` uses the actual saved parent, not an idealized reference parent. Its q=-16 Pa state plus axial increment 1/128 has exact trial q=+16 Pa and zero plastic increment. The exact solution exists, and its nearest binary64 state satisfies the source constraint. The saved API output lacks the failed iterate and diagnostics, so this does not prove why the Newton solve rejected. See [the next bounded diagnostic](NEXT_REVERSAL_DIAGNOSTIC.md).

Each backend used one explicit serial build target, native first: `atlas_tresca_laboratory --parallel 1`. `prospective-freeze.json` predates both builds and binds the inputs, references, policy, assessor, generated files and frozen sources. All configure/build/execution processes return zero; material qualification still fails. Full response streams, process logs and artifact hashes are retained. No additional material runs or builds were used for the algebraic diagnostic.

Reopen saved evidence without compilation or material execution:

```sh
python3 -B catalogue/investigations/tresca-laboratory-v1/verify.py
python3 -B -m unittest tests.test_tresca_laboratory -q
```

The bounded related regression suite ran 23 tests with five existing optional skips and zero failures. This proves saved evidence and corruption checks, not a passing laboratory qualification. No shared implementation, public catalogue, website, experimental data or scientific status changed. No push or deployment occurred.
