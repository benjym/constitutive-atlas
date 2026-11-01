# Independent monotonic continuous reference

This is a project research choice, not a scientific signature on D01–D08 or a replacement for the original loading-process rule. Source: Dafalias & Manzari (2004), [exact publication](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29). The private supplied PDF hash and visually inspected pages are in `source-reading.json`; no full text or image is redistributed.

## Equations and provenance

The oracle uses full symmetric 3×3 Cartesian matrices and ordinary matrix multiplication/contractions. It imports neither the Atlas evaluator nor the candidate residuals. Only serialization converts to Mandel `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`. Stress is effective Cauchy stress; stress and strain are compression positive. The path parameter is strain amplitude, not time. Kinematics are infinitesimal, fixed spatial frame, zero spin.

- Eq.3 p623: current-void-ratio pressure-dependent G and K.
- Eq.8 p624 / Table2 p628: critical void ratio and state parameter.
- Eqs.13–17 pp627–628: yield cone, unit normal, rational Lode interpolation and state-dependent backstress surfaces. The subtraction of m lies outside g.
- Eqs.18–19 p628: nonassociated plastic flow, including the **matrix** square of n and cubic trace. No componentwise square is substituted.
- Eq.21 p629: uneliminated elastic/plastic stress relation.
- Eqs.22–24 pp629,631: hardening and fixed loading-process anchor; Eqs.25–27 p631: dilatancy and fabric.
- Appendix Eqs.28–30 p633: independent triaxial reduction used by `algebra_checks.py`.

For positive distance `d=(alpha-alpha_in):n`, write `b=alpha_b-alpha`, `Hbar=(2/3)p*b0*(b:n)`, `E=2G*(B-C*tr(n³))-K*D*(n:r)` and `A=2G*(n:V)`. V is the prescribed deviatoric strain direction, with trace zero. Set `q=A/(Hbar+d*E)`. The finite products are `L=d*max(q,0)` and `Lh=b0*max(q,0)`. The oracle integrates

```
dsigma/dt = 2G V - L*(2G Rdev + K D I)
dalpha/dt = (2/3)*b0*max(q,0)*(alpha_b-alpha)
dfabric/dt = -cz*max(-L*D,0)*(zmax*n+fabric).
```

At `d=0,Hbar>0` this is the regular one-sided limit: stress is instantaneously elastic, plastic strain and fabric rates vanish, and backstress has a finite generally nonzero rate. It does not multiply a numerically zero L by infinite h. No hardening cap, pressure floor, state projection or anchor reset is used. `d<0`, zero loading denominator and unsupported zero-distance branches reject.

The disclosed missing K in printed Eq.20 has no numerical effect on this constant-volume corpus because `trace(V)=0`. These trajectories cannot independently adjudicate that missing term in mixed-volume loading. Elastic entry and plastic continuation are separate phases: from `sigma=pI`, zero histories and constant e, exact first yield is `t_y=p*sqrt(2/3)*m/(2G*norm(V))`. The reference integrates only the subsequent plastic leg, retaining the initial point and the exact entry point.

## Numerical choices and intended comparison

All 27 manufactured initial states and directions are exact decimal inputs in `inputs.json`. They cover three densities, three pressures and compression, extension and general shear with all three off-diagonal components. They use Table1 constants and the explicit normalization p_at=100000 Pa. They do not recreate published specimens or Wichtmann experiments. Void ratio stays constant under the stated total-volume constraint; alpha_in remains exactly zero. Every output retains all 25 persistent components plus all six total-strain components.

The continuous oracle is Decimal Dormand–Prince5(4) with an exact rational tableau, component scaling by initial pressure for stress and unity for histories. RK trial stages use the explicitly declared normalized off-cone continuation. No projection onto the yield surface hides drift: independent saved-state yield residuals must meet the frozen adequacy gate, and tightening local tolerances must produce adequate full-trajectory refinement. This validates a bounded numerical reference empirically, not a rigorous global error bound. It differs from the candidate's finite-step backward-Euler method.

The prospective policy freezes three tolerances and two precisions before any reference run. Arithmetic agreement at the same integration tolerance is separate from truncation refinement. Eighteen points per path include initial, first yield and sixteen plastic samples. A saved pass requires every case and full-state sample; failure is retained rather than dropped. Source triaxial/rotation/regular-entry checks and corrupted-corpus challenges complement these checks.

No candidate/backend acceptance budget is selected from these results. A later separately identified study must freeze literal binary64 candidate inputs, rounding policy, complete histories, convergence/refinement, supported rejection and transaction scopes, and all derivative claims. This corpus does not close mixed-volume entry, general prepared anchors, reversal, controls, rollback, derivatives, native/Wasm/browser integration or scientific admission. It is a reusable independent reference for the constant-volume monotonic portion of the SANISAND proof.
