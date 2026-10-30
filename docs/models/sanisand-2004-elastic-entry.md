# SANISAND-2004: exact elastic path and first-yield reference

Status: **research reference; independent review pending**. This advances SAN-03/05 but is not an admitted material or a plastic time integrator. The [helper](../../tools/sanisand_elastic_entry.py) is a Python research oracle, separate from production model execution. Source elasticity is Eq. (3), p. 623, of [Dafalias and Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29), mapped in the [original-paper dossier](sanisand-2004-original.md). The closure `de=-(1+e)*d_ev` is an explicit project inference from constant solid volume. The equations below are project derivations, not an algorithm prescribed by the publication.

## Exact elastic solution along a straight strain path

Use compression-positive Mandel components, zero spin, fixed backstress and fabric, and a path `epsilon(t)=epsilon_initial+t*Delta_epsilon`, `0<=t<=1`. Write `v=tr(Delta_epsilon)`, `x=t*v`, `y0=1+e_initial`, `a=2*(1+nu)/(3*(1-2*nu))` and `u=sqrt(p/p_at)`. Source Eq. (3) gives

```text
f(e) = (2.97-e)^2/(1+e)
e(x) = y0*exp(-x)-1
du/dx = a*G0*f(e(x))/2
J(x) = (3.97^2/y0)*(exp(x)-1)-2*3.97*x+y0*(1-exp(-x))
u(x) = u_initial+a*G0*J(x)/2
p(x) = p_at*u(x)^2
```

This uses current void ratio throughout, rather than holding the initial density factor fixed. At `x=0`, take `J(x)/x=f(e_initial)`. To avoid cancellation for small volume changes, evaluate `exprel(x)=expm1(x)/x` with its continuous value at zero. Near the zero-stiffness density, the direct expression for `J/x` also cancels; the helper instead uses `d=2.97-e_initial` and

```text
J/x = d^2/y0*exprel(x)
      +2*d*(exprel(x)-1)
      +y0*(exprel(x)+exprel(-x)-2)
```

The last two small differences use their Taylor series for `abs(x)<0.1`. Twenty terms suffice for this numerical switch; it is an evaluation choice, not a material regularization.

The mean shear modulus over the path fraction is

```text
G_average = p_at*G0*(u_initial+u(x))*(J/x)/2
sigma(t) = sigma_initial
           +(p(x)-p_initial)*I
           +2*t*G_average*dev(Delta_epsilon)
```

Compute the pressure difference as `p_at*Delta_u*(2*u_initial+Delta_u)` to avoid subtracting nearly equal pressures. At zero volume change, pressure and void ratio are constant and this reduces to exact linear deviatoric elasticity. Arbitrary partitioning along the same straight strain direction composes to the same solution. This does not claim path independence for different strain directions.

## First-yield bracket

The original cone is `norm(s/p-alpha)=sqrt(2/3)*m`. For `v!=0`, elastic evolution obeys

```text
k = 2*dev(Delta_epsilon)/(a*v)
r(t) = k+(s_initial-k*p_initial)/p(t)
```

Within the declared domain, `p(t)` is monotonic because `dp/dx=K>0`. Thus `r(t)` traverses a straight segment in tensor space without reversing. At `v=0`, `r(t)` is affine in `t`. The cone interior at fixed `alpha` is a convex ball in `r` space. Starting inside, an inside endpoint cannot hide an intervening outward crossing; an outside endpoint has a unique outward crossing. An initially on-cone unloading path can enter the interior and later cross the opposite side, which the locator handles.

`first_yield` returns `None` if the complete path remains elastic, or a lower/upper fraction bracket. It bisects the exact elastic path until the bracket width is at most the configurable `fraction_tolerance` (default `1e-12`); exhaustion rejects the search. Each endpoint includes stress, void ratio and dimensionless cone residual. A clearly exterior initial state is rejected. An initially on/just outside cone state with outward direction returns an initial event only within `yield_tolerance*radius` (default `1e-12*radius`); its residual is retained. A slightly exterior inward state is rejected because an elastic lower bracket would require an explicit projection policy. No projection occurs. The tolerances and event policy are project numerical choices.

The audit domain requires positive pressure, `0<e<2.97`, `G0>0`, `p_at>0`, `-1<nu<0.5`, finite inputs and a deviatoric backstress. The void-ratio bound deliberately excludes the zero-stiffness point and is not a proposed universal physical domain. The helper requires the **entire elastic predictor** to remain in this domain. If it leaves the domain after a possible earlier yield event, the current helper rejects rather than searching through an undefined predictor; a production locator needs a separately specified domain-boundary event. Inputs remain unchanged on success or failure.

## Evidence and remaining work

Six [test groups](../../tests/test_sanisand_elastic_entry.py) cover zero/tiny volume changes and near-zero stiffness, independent Cartesian-rate RK4 refinement, composition, oblique rotational covariance, pressure-unit scaling, an analytical constant-volume yield fraction, mixed-volume yield bracketing, unloading through the opposite cone side, initial outward/stationary cases, invalid domains and exhausted-search rejection. The [record](../../catalogue/investigations/sanisand-elastic-entry-v1.json) pins source/helper/test hashes and the passing 15-group combined SANISAND run.

The RK4 oracle independently integrates the same source elasticity; it is not independent scientific authorship or external trajectory validation. This work supplies no initial `alpha`/`z`/`alpha_in` policy, reversal reset, plastic continuation, mixed control solve, event derivative, rollback implementation, native/Wasm evidence or experimental comparison. The complete formulation must still use the common engine rather than importing this research helper as a model-specific production escape hatch.
