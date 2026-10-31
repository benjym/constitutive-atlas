# IGS97: original-paper reconciliation

**Draft source reconciliation; independent review pending.** Niemunis and Herle (1997), *Hypoplastic model for cohesionless soils with elastic strain range*, pp. 279–299, [DOI](https://doi.org/10.1002/%28SICI%291099-1484%28199710%292%3A4%3C279%3A%3AAID-CFM29%3E3.0.CO%3B2-8). The [receipt](../../catalogue/source-audits/original-papers-2026-10-31.json) pins the user-supplied 21-page original. PDF page 1 is printed p. 279. This review covers pp. 280–281, 285–292 and Appendices A–C, pp. 295–297. Equation pages 287, 289, 292, 295 and 297 were rendered and visually inspected. Remaining introductory/simulation pages have not received complete equation-level review.

## Overlay and sign conversion

The source uses tension-positive Cauchy stress `T`, stretching `D` and history `delta` (p. 280). For Atlas compression-positive variables, negate all three tensors; the normalized-history projection remains unchanged. The host nonlinear stress-rate tensor changes sign. Mandel coordinates preserve Euclidean tensor contractions when physical shear components are multiplied by `sqrt(2)`.

Equations (7)–(8), pp. 285–286, define `rho=norm(delta)/R` and `eta=delta/norm(delta)` for nonzero history, with `eta=0` at zero history. In the physical ball `rho<=1`, Eq. (14), p. 287, contracts to the two stress-rate branches already documented in the [implemented dossier](hypoplastic-sand-igs97.md). Its positive projection branch contains both `(1-mT)*(L:eta)` and the nonlinear tensor `N`; its nonpositive branch contains `(mR-mT)*(L:eta)` and no `N`. Equation (15) gives `delta'=D-rho^beta_r*eta*(eta:D)` for positive projection and `delta'=D` otherwise. These branches agree with the current declarative equations within the physical history ball.

Equations (10)–(13), pp. 286–287, give the limiting checks: saturated aligned loading recovers the host response, saturated reversal multiplies the linear host stiffness by `mR`, saturated orthogonal loading multiplies it by `mT`, and zero history gives `mR*L` in every direction. The source specifies `mR>mT>1` and later `chi>1`; Atlas permits some limiting values outside those stated strict inequalities for exploration. Those input bounds do not constitute original-paper parameter recommendations.

## The original host is a specialization

Appendix A has **seven host parameters**, not an independent density exponent `beta`. Its Eq. (29), p. 295, supplies the combined stiffness factor directly:

```text
fb_fe = hs/n * (1+ei)/e * (3*p/hs)^(1-n)
        / [3+a^2-a*sqrt(3)*((ei0-ed0)/(ec0-ed0))^alpha]
```

Equations (23)–(28), (30)–(31) give the linear/nonlinear tensors, normalized stress, Lode shape and pressure-dependent limiting densities. Atlas's current eight-parameter host instead multiplies

```text
(ei0/ec0)^beta * (1+ei)/ei * (ec/e)^beta.
```

Since `ei/ec=ei0/ec0`, this equals `(1+ei)/e` **at beta=1**. Thus the original host can be represented by that specialization; the current default `beta=1.05` is a different host choice. This is a variant distinction, not an error in the general overlay. Preserve the original seven-parameter calibration when reproducing this paper; do not insert an arbitrary beta or relabel current defaults as Table I.

Table I, p. 292, describes Hochstetten sand:

| phi | hs | n | ec0 | ed0 | ei0 | alpha |
| --- | --- | --- | --- | --- | --- | --- |
| 33 degrees | 1000 MPa | 0.25 | 0.95 | 0.55 | 1.05 | 0.25 |

| R | mR | mT | beta_r | chi |
| --- | --- | --- | --- | --- |
| 0.0001 | 5 | 2 | 0.50 | 6 |

The Fig. 16 comparison starts at isotropic effective stress `-100 kPa I` and void ratio `0.695`, with constant-volume plane-strain compression after different recent strain histories. These are not the Atlas illustrative defaults and are not a Wichtmann calibration. Fully specified preparation paths are still needed before trajectory reproduction.

## Integration, transactions and physical time

Section 5, pp. 288–289, recommends automatic increment control, especially near sharp reversals, discusses an explicit Euler update, and advises correcting history overshoot rather than relying on the evolution equation to remove it in later steps. Atlas uses adaptive midpoint integration, caps `rho` at one, admits a 1% numerical overshoot band and does not project history. Consequently agreement of instantaneous equations does not imply agreement with the paper's finite-step procedure. Section 5 also recommends increments smaller than `0.2R` immediately after reversal and, for positive history projection, Eq.(17) gives `delta_epsilon_max=mu*R/(1-rho**beta_r)` with proposed `mu=0.2`. These are source numerical recommendations, not additional constitutive equations or the Atlas midpoint acceptance criterion. The precise projection algorithm and all example increments are not fully specified here.

The paper warns against updating state during equilibrium iterations because this may create artificial reversals (p. 289). A common solver therefore needs committed history, isolated trial evaluations and rollback; repeated equilibrium guesses must not accumulate history. Source recommendations must be represented separately from material equations and tested through solver transactions.

Appendix C, p. 297, gives the objective history rate `delta_circle=delta_dot-W*delta+delta*W`. Appendix A, Eq. (32), p. 296, gives the corresponding stress transport. The present Atlas zero-spin scope omits those spin terms consistently but does not implement finite-rotation transport. A bounded parallel source audit identified a printed conflict: Section 5, p.289/PDF11, writes the explicit-update spin contribution as `(-W*T+T*W)*delta_t`, while Appendix A Eq.(32), p.296/PDF18, gives `T_dot=T_circle+W*T-T*W`. Appendix C history transport agrees with the latter objective-rate convention. Both cannot be treated as identical ordinary-rate formulas. A future finite-rotation declaration must resolve this source conflict and transport history and stress consistently; zero-spin calculations are unaffected.

Section 7, p. 291, discusses erasing history after a resting period and mentions a possible decay law as an idea. No calibrated time-dependent evolution is supplied; the authors use an explicit reset for their resting-period idealization. Do not add automatic decay to this rate-independent identity or interpret the normalized path coordinate as elapsed seconds. A reset should be a declared preparation event, not an unannounced side effect of a zero-strain step.

## Reproducible equation comparison

The [Python-only verifier](../../tools/verify_igs_original.py) independently constructs the original fourth-order Cartesian host and overlay operators before contraction. It does not import the existing VW96 oracle and does not run a native solver. The [v1 report](../../catalogue/investigations/igs-original-rates-v1.json) records **576 passing instantaneous comparisons** against the current DSL interpreter, using Table I with `beta=1`, three pressures, two stress shapes, two densities, four history magnitudes, six stretching directions and both signs. Stress tolerance is `1e-7 Pa + 2e-11*abs(reference)`; dimensionless tolerance is `1e-14 + 2e-11*abs(reference)`. All tolerances were declared before execution.

This verifies the equation/sign specialization over that grid. It does not establish native/Wasm parity, trajectory convergence, external-code agreement, finite-rotation behavior, experimental accuracy or independent authorship. The original host specialization, strict source parameter domain, preparation/reset semantics, overshoot policy and independent scientific review remain admission work under REV-04/REV-05.
