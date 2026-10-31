# Mohr–Coulomb gap classifier v2: source-only research candidate

This distinct candidate retains the selected [Sysala–Cermak arXiv v3](https://arxiv.org/abs/1508.07435v3) H=0 backward-Euler law and strict elastic threshold. Parent [v1](../mc-declarative-design-v1/README.md) remains failed on four rounded apex holds. v2 rearranges only the classifier arithmetic using x=t1−t2 and y=t2−t3:

```
g_la=(x+2y)/(2G(3−d))
g_ra=(2x+y)/(2G(3+d))
gamma_a=(Ftrial−(1+s/3)x−(1−s/3)y)/(4Kds)
```

These are exact source identities. At hydrostatic raw spectrum x=y=0, the apex root shares the exact computed yield residual, giving gamma_a=Ftrial/(4Kds). The strict Ftrial<=0 elastic test, source interval/equality rules, ordinary return expressions, independent certificate inputs, selected-gap policy and acceptance bounds are unchanged. No eigenvalue merging, stress clipping, failure retry or numerical elastic zone is used. The exact JSON changes are two gap aliases, three guard expressions and a distinct model ID.

The revised policy/model were frozen before source-only observations in prospective-policy.json. `python3 -B check.py` passes all25 diagonal/rotated return cases and their zero-increment holds, nine invalid parameter rejections, exact14 source certificates and three generated/copied-source replay files. Maximum value-error/allowance is0.000278. check.stdout/check.stderr retain the original result. The reused assessor identifies its implementation as source-checks-v1; candidate identity is established by its policy/model pins. The independent audit separately proves exhaustive exact branch coverage and reviews actual generated lazy ordering and grouped reconstruction.

model.json is the complete v0.3 six-component stress-only research record; the same bytes are installed under models/research/, outside the public nine-model manifest. Initial and returned stress allow F<=256eps*max(h,|extrema|) as roundoff validation only. Strict scalar sine/denominator and selected-gap checks can reject unresolved mathematically valid inputs. The effective-stress interpretation is an explicit host specialization, without pore-pressure coupling.

These constructed rational-source certificates are converted to binary64 parameters and Mandel tensors under a bounded source-only stress tolerance. They are not high-precision references for every actual stored tensor, full tensor derivatives, experimental agreement or general-domain verification. All38 directional columns, parameter sensitivity, one-sided boundaries, extreme scales, KKT/subgradient checks and accepted-state rollback require a separately frozen model study before native/Wasm execution. No compiled observations, website promotion or scientific admission.
