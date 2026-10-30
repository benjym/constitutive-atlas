# SANISAND: finite products at infinite hardening

**Derived algebra investigation; independent review pending.** This extends the [original-paper equation draft](sanisand-2004-original.md) by a one-sided mathematical limit. It is not an original printed equation, a finite-step integrator or a selection of reversal events. The [separate typed fragment](../../catalogue/source-audits/sanisand-2004-hardening-limit.json) preserves the pinned source and all unchanged expressions. Native compilation and executable tests remain held following the latest Cortex report; all checks here use Python.

## Rearrangement on a fixed smooth branch

Let `d=(alpha-alpha_in):n` be reversal distance, `b=alpha_b-alpha`, and define

```text
Hbar = (2/3)*p*b0*(b:n)
E = 2*G*(B-C*tr(n^3))-K*D*(n:r)
A = 2*G*(n:de)-K*d_ev*(n:r)
```

The symbols `A` and `E` here are auxiliary scalars, distinct from the fabric-dependent dilatancy factor `Ad`. `Hbar`, `E` and `A` have pressure units (strain increments are dimensionless). The numerator uses the explicit dimensionally consistent correction to printed Eq. (20), as documented in the original dossier. With original Eqs. (23)–(24), `h=b0/d` and `Kp=Hbar/d`. For **positive** `d`, exact algebra gives

```text
q = A/(Hbar+d*E)
L = d*q
positive_part(L) = d*positive_part(q)
positive_part(L)*h = b0*positive_part(q)
```

Therefore the products used in the state equations are

```text
d_epsilon_p = d*positive_part(q)*R
d_alpha = (2/3)*b0*positive_part(q)*b
d_z = -cz*positive_part(-tr(d_epsilon_p))*(zmax*n+z)
d_sigma = Ce:d_epsilon - d*positive_part(q)*(2*G*Rdev+K*D*I)
```

No divergent `h` or `Kp` is evaluated. Signed softening at positive distance is retained; `Hbar` is not forced positive. The scaling is algebraic, with no finite cap, epsilon denominator, distance floor or pressure regularization.

## The one-sided zero-distance limit

For fixed on-cone state, direction, parameters and strain increment, if `Hbar>0`, the limit `d -> 0+` is

```text
q -> A/Hbar
d_epsilon_p -> 0
d_sigma -> Ce:d_epsilon
d_z -> 0
d_alpha -> b*positive_part(A)/(p*(b:n))
```

Backstress can have a finite increment even though plastic strain tends to zero. Substituting zero plastic multiplier before forming its product with infinite hardening would incorrectly erase that increment.

For outward loading, this finite backstress rate maintains first-order yield consistency. With `N=n-(n:r)*I/3`, `N:Ce:d_epsilon=A`, and the limit gives `p*n:d_alpha=A`, hence `df=0`. For negative `A`, the positive part suppresses history evolution and the stress follows the elastic unloading branch. This is a directional branch statement, not a claim of a unique derivative at `A=0`.

The limit removes dependence on `h0` at the zero-distance point because `b0` cancels. It does not remove the elastic stiffness dependence through `A`, and it is not a statement about an entire finite loading history. Rescaling stress and `p_at` together rescales stress increments while leaving dimensionless history increments unchanged.

## Explicit limits of the investigation

- At zero distance with `Hbar<=0`, reject the state. Simultaneous zero limits can depend on the approaching state path and need further analysis; no universal value is assigned.
- Reject negative distance rather than inventing a reversal reset. The publication's reset rule and the engine's event scope still need reconciliation.
- Reject `Hbar+d*E=0`; this rearrangement does not resolve a true singular loading denominator.
- Evaluate on the yield cone only. Elastic-interior integration, first-yield location and off-surface normals remain open.
- Keep initialization, trial/commit isolation, event logs, rollback, finite-step derivatives and mixed controls separate from this instantaneous identity.

The helper's domain guards are an audit scope, not the complete physical state/parameter domain. A fully executable formulation and independent review remain required under SAN-01/03/05/06.

## Evidence

Four [Python-only test groups](../../tests/test_sanisand_limit.py) pass: 120 positive-distance comparisons with the original finite expressions under loading and unloading; exact-zero consistency and independence from a hardening cap; one-sided convergence and overflow avoidance down to distance `1e-305`; and rejection of negative-distance, negative-numerator zero-distance and simultaneous-zero cases. Zero-limit tests also check pressure-unit covariance and elastic unloading. The [investigation record](../../catalogue/investigations/sanisand-hardening-limit-v1.json) pins fragment/helper/test hashes and the execution log. No native/Wasm, external-code, trajectory or experimental agreement is claimed.

A subsequent, separately authorized [standalone native check](../../catalogue/investigations/sanisand-native-algebra-v1.json) passed 12 cases spanning three directions, zero/positive reversal distance and both loading signs. It checked 2,280 double/AD values and 6,840 AD strain columns against Python values and central differences. [Prepare the fixture](../../tools/prepare_sanisand_native.py) without compilation, then compile/run it as separate steps. This tests the same draft equations across two execution paths; it supplies no independent equation review, state derivative or finite-step tangent.
