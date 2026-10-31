# Generated context v1 — retained failed study

Native and Wasm produce identical complete observations. All10820 material rows and18 history rows are present. Each backend has exactly two policy mismatches: trace-observable-scale-dev/extreme and trace-state-scale-dev/extreme. All other rows match the frozen independent expectations, including full38-column failure/recovery and history rollback. The study remains **failed**; original source, fixtures, expectations and protocol are unchanged.

The two scale cases use r=1e308. Exact trace is -r, and the computed first deviator component is r-(-r/3), about1.333e308, which is finite. The subsequent norm overflows and its unchecked comparison selects the finite scale1. The frozen expected NaN scales therefore do not describe dev-result overflow at these inputs. This also documents a separate unmarked norm-overflow/predicate limitation; no norm repair is claimed.

A distinct v2 repeats the complete corpus with DBL_MAX for those two inputs and increases only the corresponding parameter upper bounds. DBL_MAX-(-DBL_MAX/3) overflows, directly exercising the intended checked dev-result rejection. No gate is relaxed and this failed study is not replaced. Full solver-level transactions and scientific admission remain open.

Re-audit with `PYTHONPATH=. python3 -B catalogue/investigations/trace-generated-context-v1/assess.py`; expected exit1 reproduces the negative result. No binary is required.
