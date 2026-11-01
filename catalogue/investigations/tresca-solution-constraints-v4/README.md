# Tresca: separate physical constraints, v4

This private candidate passes the complete original one-step/restart corpus and continuous own-committed-state history on native C++ and Wasm. It is not installed in the public catalogue and has no scientific admission.

The v2 pressure-split equations, residual domain, parameters, initialization and source hyperlinks are preserved. Only record identity/description and `solution_constraints: ["principal_range_le(sigma,2*k)"]` differ. Shared generic schema/compiler/solver support enforces this constraint at physical-state boundaries while retaining the raw residual extension. No model-specific solver branch is introduced.

Each backend passes all 219 original requests: 194 acceptances, 25 intended rejections, 2,328 value comparisons and 27,816 derivative comparisons covering all 38 columns. All 12 continuous history increments accept and satisfy the independent exact source-membership checks for actual parents and commits. Original assessors, references, tolerances and input wires are retained unchanged. Maximum normalized value error is about 1.17e-10 and derivative error 4.14e-14, within original gates.

Additional compiled checks distinguish raw evaluation from physical admissibility, reject malformed layouts, check 48 nonfinite primal inputs and 1,368 nonfinite state derivative seeds per backend, verify recovery/full rollback and exercise compatibility with a legacy model struct.

`prospective-freeze.json` binds inputs, assessors, generated and shared source bytes before builds. `source-pins.json` binds current implementation sources. Native and Wasm each used one serial explicit target, `atlas_tresca_solution_constraints --parallel 1`, native first. Process logs, complete response streams and binary hashes are retained; local binaries are not distributed here. The generated header has the same retained branch-counter instrumentation as preceding studies; `generated-original/` retains normal output.

Reopen saved evidence without compiling or running material code:

```sh
python3 catalogue/investigations/tresca-solution-constraints-v4/verify.py
python3 -B -m unittest tests.test_solution_constraints tests.test_tresca_solution_constraints -q
```

Earlier v1, continuous-history v1 and feasible-domain v3 failures remain unchanged and unqualified. This is a distinct candidate and prospective study, not a revised verdict on those experiments. Next: a bounded private laboratory/mixed-control qualification, followed by independent source/formulation review before public activation. No deployment is included.
