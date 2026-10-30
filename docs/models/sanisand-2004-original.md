# SANISAND-2004: original-paper extraction

Status: **equation transcription draft; independent review pending**. This is a source dossier, not an executable formulation or a validated integration algorithm. Source: Dafalias and Manzari (2004), *Simple Plasticity Sand Model Accounting for Fabric Change Effects*, pp. 622–634, [DOI](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29). The user-supplied 13-page PDF is pinned in the [receipt](../../catalogue/source-audits/original-papers-2026-10-31.json). PDF page 1 is printed page 622. Full text was read; equation pages 2, 5–8, 10 and 12 were also rendered and visually inspected. This is project-authored extraction, with independent scientific review still pending.

## Conventions and elastic response

Use effective stress and compression-positive stress/strain. Define `p=tr(sigma)/3`, `s=dev(sigma)`, `r=s/p`, volumetric increment `d_ev=tr(d_epsilon)` and deviatoric increment `de=dev(d_epsilon)`. Tensor contractions below are Cartesian contractions; conversion to Atlas Mandel coordinates must preserve them. This dossier does not extend the paper to finite rotations.

Equation (3), p. 623, gives

```text
G = G0 * p_at * (2.97-e)^2/(1+e) * sqrt(p/p_at)
K = 2*(1+nu)/(3*(1-2*nu)) * G
```

The paper explicitly uses **current** void ratio `e`. Its incremental elasticity is hypoelastic. The pinned OpenSees implementation instead uses initial void ratio in this expression; its audit cannot substitute for this original formulation. `p_at` is an atmospheric-pressure normalization in the same units as stress. Stress, `G`, `K` and `Kp` have pressure units; the remaining material constants below are dimensionless. The real-valued interior requires `p>0`, `e>-1`, and nonsingular Poisson ratio; physical/calibration restrictions remain to be finalized.

Equation (8), p. 624, defines the critical-state curve `ec=e0-lambda_c*(p/p_at)^xi`; use `psi=e-ec`. The published `e0` is the critical-state intercept, distinct from a specimen's initial void ratio.

## Yield surface and state-dependent surfaces

Equations (13)–(17), pp. 627–628:

```text
f = norm(s-p*alpha) - sqrt(2/3)*p*m
n = (r-alpha)/(sqrt(2/3)*m)                 # on f=0
cos3theta = sqrt(6)*tr(n^3)
g = 2*c / ((1+c)-(1-c)*cos3theta)
alpha_b = sqrt(2/3)*(g*M*exp(-nb*psi)-m)*n
alpha_d = sqrt(2/3)*(g*M*exp( nd*psi)-m)*n
alpha_c = sqrt(2/3)*(g*M-m)*n
```

`alpha` is a deviatoric backstress-ratio tensor; `n:n=1` and `tr(n)=0` on the yield surface. Normalizing `r-alpha` off the surface is an additional implementation extension requiring an explicit policy. The yield normal in stress space is `n-(n:r)*I/3`. The subtraction of `m` is outside `g` in every surface. This original rational Lode function differs from PM4Sand3D's fourth-root interpolation; keep their identities separate.

## Flow, hardening and fabric

Equations (18)–(19), p. 628:

```text
B = 1 + (3/2)*(1-c)/c*g*cos3theta
C = 3*sqrt(3/2)*(1-c)/c*g
Rdev = B*n-C*(n^2-I/3)
R = Rdev+D*I/3
d_epsilon_p = positive_part(L)*R
```

Here `n^2` is the symmetric matrix square, not a componentwise square. Equations (22)–(27), pp. 629, 631:

```text
b0 = G0*h0*(1-ch*e)*(p/p_at)^(-1/2)         # Eq. (6), p. 623
h = b0/((alpha-alpha_in):n)
Kp = (2/3)*p*h*(alpha_b-alpha):n
d_alpha = positive_part(L)*(2/3)*h*(alpha_b-alpha)
Ad = A0*(1+positive_part(z:n))
D = Ad*(alpha_d-alpha):n
d_z = -cz*positive_part(-d_ev_p)*(zmax*n+z)
```

`d_ev_p=tr(d_epsilon_p)`. Fabric evolves during plastic dilation. `Kp` may be positive, negative or zero; forcing it positive changes the formulation. The paper defines `alpha_in` at initiation of a loading process and calls for updating it when the denominator of Eq. (24) becomes negative, referring to Dafalias (1986). It does not specify Atlas parent-increment versus substep transactions. At initiation the ideal hardening is infinite; a finite replacement such as OpenSees' guard is a numerical variant requiring separate identification.

Equations (20)–(21), p. 629, express the loading index and stress increment. **The printed numerator in Eq. (20) is `2*G*(n:de)-(n:r)*d_ev`, without `K` in its second term.** Direct substitution of `dp=K*(d_ev-positive_part(L)*D)` into the preceding stress-loading expression requires `K` there and restores pressure units. The following is that derived, dimensionally consistent form, not a verbatim transcription of the printed equation; independent review must resolve the apparent omission:

```text
L = (2*G*(n:de)-K*d_ev*(n:r)) /
    (Kp+2*G*(B-C*tr(n^3))-K*D*(n:r))
d_sigma = 2*G*de+K*d_ev*I
          -positive_part(L)*(2*G*Rdev+K*D*I)
```

These continuous incremental relations do not prescribe a finite-step return mapping. Elastic interior detection, first yield, zero denominators, reversal location, cutbacks and rollback need a separate numerical contract. No pressure floor, low-pressure correction, hardening cap, integration tolerance or time-step rule is adopted from the OpenSees variant here. Constant-solid-volume closure `d_e=-(1+e)*d_ev` is a project kinematic inference, not a numbered equation in this paper.

## Parameter and benchmark identity

Table 1, p. 626, supplies this Toyoura example:

| G0 | nu | M | c | lambda_c | e0 | xi | m |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 125 | 0.05 | 1.25 | 0.712 | 0.019 | 0.934 | 0.7 | 0.01 |

| h0 | ch | nb | A0 | nd | zmax | cz |
| --- | --- | --- | --- | --- | --- | --- |
| 7.05 | 0.968 | 1.1 | 0.704 | 3.5 | 4 | 600 |

Figure 3 explicitly uses `zmax=5`, rather than Table 1's `4`. Record this override in any reproduced case. The Appendix, p. 633, gives the triaxial mapping `D=sqrt(2/3)*d` and `Kp=(2/3)*p*H`; the factors preserve the same `h0` and `ch` in the triaxial and multiaxial forms. These provide independent algebraic reduction targets before trajectory comparisons.

Figures 5–9 compare Toyoura tests from Verdugo and Ishihara (1996), with initial void ratios 0.735, 0.833 and 0.907 and differing pressure paths. Figure 10 uses a different cyclic dataset and specimen preparation; it must have its own benchmark identity. None is a Wichtmann calibration. Figure 11 contrasts `zmax=4` with zero. Plot images are not digitized experimental data or numerical reference trajectories.

## Remaining admission work

- Independently review this transcription and reconcile every term with the pinned implementation audit.
- Specify physical domains, specimen preparation, initial `alpha`, `z`, `alpha_in`, pressure normalization and singular limits.
- Resolve finite-increment event scope, yield entry, reversal and algorithmic derivatives; retain explicit variant boundaries.
- Implement declaratively and verify tensor identities and triaxial reductions before source-matched reference histories and experiments.

SAN-01 remains open for initialization/domain completion; SAN-02–07 are not closed by source acquisition. See the [main brief](sanisand-2004.md) and [integration audit](sanisand-2004-integration.md).

## Typed algebra investigation

The [33-term declarative fragment](../../catalogue/source-audits/sanisand-2004-original-equations.json) now represents these continuous equations in the existing tensor DSL, including source locators and the explicit Eq. (20) correction. Its [Python evaluator](../../tools/inspect_sanisand_original.py) checks source identity, tensor shapes and SI dimensions. It evaluates only on the yield cone with finite positive reversal distance and nonsingular loading denominator; this audit domain is not a complete physical domain. `p_at=100000 Pa` is the chosen audit normalization, not a claim that the paper fixes atmospheric pressure to that value.

Five [Python test groups](../../tests/test_sanisand_original.py) verify triaxial flow/surface reductions, current-density elasticity, 40 general Cartesian matrix-square/cubic-invariant and active yield-consistency cases, pressure-unit covariance, dilation/fabric switching, elastic unloading, signed softening and unresolved-state rejection. The [investigation record](../../catalogue/investigations/sanisand-original-algebra-v1.json) pins the fragment, helper and test hashes. No finite-increment algorithm, initial-memory rule, external-reference agreement, native/Wasm execution or independent scientific review is claimed. SAN-05 has a typed algebra draft; it remains open for a complete executable definition.

The subsequent [finite-hardening-product derivation](sanisand-2004-hardening-limit.md) supplies a candidate one-sided zero-distance limit on a regular branch, with a separate typed fragment and Python evidence. It preserves this finite-distance draft unchanged. It does not settle general initialization, simultaneous-zero limits or reversal-event policy.

The subsequent [exact elastic-entry reference](sanisand-2004-elastic-entry.md) derives straight-path elastic evolution and brackets first yield under explicit audit-domain and numerical-event policies. It advances the elastic-interior gap without specifying initialization, plastic continuation or reversal memory.
