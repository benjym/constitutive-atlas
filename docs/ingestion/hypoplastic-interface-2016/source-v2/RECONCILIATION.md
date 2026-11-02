# Selected realization and correction history

Proposed source identity: **Stutz–Mašín–Wuttke (2016) fully rough HvWE interface, inherited original von Wolffersdorff (1996) host, source-reconciled, fixed local zero-spin restriction**. This identifies every selected constitutive mechanism; it is distinct from literal substitution of the inconsistent journal print. It omits no source-supported fully rough material mechanism. No intergranular strain, viscosity, thermal law, opening/contact algorithm or roughness degradation is added.

The original 2016 author thesis is visually readable; the original 1996 host is visually readable. Publisher-pagination 2016 mirror text corroborates the reduction and inheritance statements, but exact2016 journal/accepted visual receipt remains missing. The table in README is an explicit source/version crosswalk. Source completeness of this disclosed realization is a decision for independent review; this document is not approval.

## Complete host, extension-positive source convention

Let T be compression-negative effective stress and D extension-positive stretching. Use the reduced embedding/weighted contraction in README. The four stress entries are [Tn,Tp,Tx,Tz], not four entries of an arbitrary unrestricted tensor. I=[1,1,0,0]. All products below are scalar contractions, dyads or vector operations except the specified trace-free cubic.

```text
s = tr_r(T) < 0
That = T/s
Z = That - I/3
z2 = Z:Z
u = sqrt(3*z2)
c = -sqrt(6)*tr_r((Z dot_r Z) dot_r Z)/(z2^(3/2))   [z2>0]
F = sqrt(u^2/8 + (2-u^2)/(2+sqrt(2)*u*c)) - u/(2*sqrt(2))
a = sqrt(3)*(3-sin(phi_c))/(2*sqrt(2)*sin(phi_c))
rho = exp[-(-s/hs)^n]
ed = ed0*rho; ec = ec0*rho; ei = ei0*rho
fd = ((e-ed)/(ec-ed))^alpha
fe = (ec/e)^beta
B = 3+a^2-sqrt(3)*a*((ei0-ed0)/(ec0-ed0))^alpha
fb = (hs/n)*((1+ei)/ei)*(ei0/ec0)^beta*(-s/hs)^(1-n)/B
fs = fb*fe
Tdot = fs/(That:That) * [F^2*D + a^2*(That:D)*That
                         + fd*a*F*(That+Z)*sqrt(D:D)]
edot = (1+e)*tr_r(D)
```

This is original1996 Eqs2,40–46 evaluated using the2016 reduction; `fs` is stress-valued and appears exactly once. The thesis combined fs expression equals `fb*fe` because `ei/ec=ei0/ec0`. L0 and N0 are dimensionless; D and normD have units inverse path/time and Tdot stress per path/time. `hs` has stress units; the remaining host parameters are dimensionless, with phi_c expressed in angular units. Thickness ds is an interface geometric input in length units, not a ninth host material constant.

At z2=0, original1996 AppendixC establishes F=1. Direct evaluation of c is undefined there; implement an explicitly justified isotropic branch using the limit, not an arbitrary epsilon/clamp or invented Lode direction. At z2>0 the original expression applies on its real regular domain. The trace-free cubic agrees with Cartesian trace exactly by the independent check; intermediate reduced products do not generally embed as matrix products.

The selected fixed-local, zero-spin restriction sets source Jaumann objective rate equal to the component rate. It does not claim arbitrary frame transport or finite rotation. The four-state subspace is invariant under this host and the selected D; Tp evolves as an independent stress even when its stretching entry is zero. A compression-positive Atlas binding must convert both T and D: sigma=-T, D_A=-D. Then sigmaDot has positive linear terms and a **negative** norm term, and edot=-(1+e)tr(D_A). Normalized That and Z do not change under stress reversal.

## Loading and preparation contract

The2016 reduced stretching vector is [Dn,0,gammaXdot/2,gammaZdot/2]. Two shear modes and coupled normal response are retained. The paper describes slip/thickness via tan(gamma_i)=u_i/ds; a small-angle engineering-slip convention cannot silently replace that relation. For constant ds, exact differentiation yields gammaIdot=(uIdot/ds)/(1+(u_i/ds)^2). Whether controls supply these angles, infinitesimal engineering shear or host velocity-gradient components must be part of the exact candidate identity. The source does not supply an all-purpose finite-kinematic transport/contact host.

Initial Tn,Tp,Tx,Tz and e must be supplied with units, stress sign, basis, thickness and control context. Section4.1 suggests initializing Tp before first shear, potentially via a Jaky estimate; it does not uniquely prescribe a specimen. Zero in-plane stretching does not imply a frozen Tp. The contextual evolving-Tp interpretation is supported by the continuation paragraph and state initialization despite the earlier word “constant”. This reconciliation must be reviewed explicitly.

A regular numerical study must select positive hs,n,e, ordered limiting void ratios ei0>ec0>ed0>0, nonzero admissible compression, nonnegative density-power base (typically e>ed), nonzero B, real F and finite factors; the literature's physically selected domain is not a universal fitted parameter box. Source parameters alone do not establish tensile contact/opening or outside-domain extensions. No reset upon reversal is present. Control holds require finite factors before applying zero D. Normal mixed controls, trial/commit/rollback, error budgets and restart are numerical host choices, described separately in README; no specific integrator is inferred from the constitutive source.

## Correction history retained

Before primary1996 visual inspection, the worker incorrectly suggested that `a*(F*That+Z)` might be the usual inherited nonlinear factor and treated density evolution as unavailable. Those were false blockers. Primary1996 Eq40 confirms `a*F*(That+Z)`; Eq2 explicitly supplies density continuity. The corrected README records the supported expressions. No old historical packet or source evidence was rewritten. The duplicated fs/fd print and missing pressure minus are real, dimensionally/physically incompatible with the named inherited source, and remain disclosed repairs rather than erased observations.

The failed optional Python rendering attempt (`import fitz`, unavailable) was replaced with installed Poppler pdftoppm; it produced no output artifact. No compiled constitutive result was observed.
