# Appendix I reconciliation and retained source conflicts

Source: Wu and Bauer (1994), [DOI](https://doi.org/10.1002/nag.1610181203), private PDF hash in [receipt](source-receipt.json). Appendix I: printed pp.859-861, PDF27-29. Every displayed component on p.860 was visually inspected. This note distinguishes literal printing, mathematical derivation, and unadopted correction candidates.

## Complete component audit

Use raw tensor vectors `v=(sigma11,sigma22,sigma33,sigma12,sigma13,sigma23)` and `d` in the same order. Appendix I explicitly displays tensor shears `D12,D13,D23`, with no doubled or orthonormal factors. Its p.861 norm definition confirms `G=diag(1,1,1,2,2,2)` and `p=sum(v[0:3])`, not one-third that sum. Eq.(21) implies

```
Lraw = c1*p*I6 + (c2/p)*v*(G*v)^T.
Lraw*d = raw(c1*p*D + c2*(sigma:D)*sigma/p).
```

Thus raw normal/shear coupling is generally not ordinarily symmetric. Instead `G*Lraw = Lraw^T*G`. For the raw order, `L14=2*c2*sigma11*sigma12/p`, while `L41=c2*sigma12*sigma11/p`. The paper's symmetry assertion immediately before the displayed coefficients cannot make these equal. Engineering shears or Mandel coordinates require different displayed vectors/matrices; no such reinterpretation repairs the two entry discrepancies simultaneously.

At the first 1800-pixel rendering, `L16` and `L24` were provisionally misread as additional conflicts. A 200-dpi component crop resolved them: `L16` contains `sigma11*sigma23`, and `L24` contains the factor `2`. Both agree. That preliminary count was corrected before handoff; no source bytes changed. The final diagnostic intentionally retains **only two** entry disagreements.

All 21 displayed upper entries were compared with the derived raw operator:

| Entry group | Result |
| --- | --- |
| `L11,L12,L13,L14` | Agree |
| `L15` | Conflict; see explicit expression below |
| `L16` | Agrees |
| `L22,L23` | Agree |
| `L24` | Agrees; the factor 2 is present |
| `L25,L26,L33,L34,L35,L36,L44,L45,L46` | Agree |
| `L55` | Conflict; different stress factor |
| `L56,L66` | Agree |

| Entry, p.860/PDF28 | Literal printed expression | Eq.(21)-derived raw expression |
| --- | --- | --- |
| `L15` | `2*c2*sigma11*sigma23/p` | `2*c2*sigma11*sigma13/p` |
| `L55` | `2*c2*sigma13*sigma11/p+c1*p` | `2*c2*sigma13*sigma13/p+c1*p` |

For `v=(11,7,5,2,3,4)`, `c1=-2,c2=-3,p=23`, printed versus derived values are respectively `-264/23` versus `-198/23`, and `-1256/23` versus `-1112/23`. Correcting those two upper entries still does not justify filling the lower triangle by ordinary symmetry.

The nonlinear matrix equation is `objective_raw = Lraw*d - N`. Each displayed `Ni` has a leading minus sign. Writing `a=sigma11,b=sigma22,c=sigma33,d=sigma12,e=sigma13,f=sigma23`, the six Cartesian square components are

```
sigma^2: (a*a+d*d+e*e, d*d+b*b+f*f, e*e+f*f+c*c,
          a*d+d*b+e*f, a*e+d*f+e*c, d*e+b*f+f*c).
```

For `s=dev(sigma)`, replace only `a,b,c` by `a-p/3,b-p/3,c-p/3`; shears remain unchanged. All six printed `Ni/norm(D)` equal `-(c3*sigma^2+c4*s^2)_i/p`. Therefore **all six nonlinear components agree**, including the cross shear products, and the complete `-N` contributes the positive nonlinear term of Eq.(21). Treating printed `N` as a positive nonlinear tensor would reverse this term incorrectly.

In Mandel coordinates `m=R*v`, where `R=diag(1,1,1,sqrt(2),sqrt(2),sqrt(2))`, the Eq.(21)-derived linear matrix is `c1*p*I+(c2/p)*m*m^T`, which is symmetric. Atlas further swaps the last two raw shear slots. This coordinate derivation explains a possible intended symmetry but is **not** evidence of author intent or an approved correction.

## Sign conflict remains

Reinspection of Eq.(1), p.834/PDF2, confirms the positive symmetric velocity gradient. The p.835/PDF3 prose gives negative elongative strains/rates and negative tensile stress. Section 3.3.1, p.846/PDF14, instead prescribes axial stretching `-1` for compression and positive `100 kPa` confinement. No single direct reading supplies consistent compression-positive stretch signs.

A research choice `stress_source=stress_Atlas`, `D_source=-D_Atlas` can follow that operational compression example; it must be labeled an inference. Because the nonlinear term contains `norm(D)`, changing the stretch sign cannot be implemented by simply negating the full rate: `H(sigma,-D)=-linear+nonlinear`. Flipping stress signs also requires tracking objective/ordinary output conventions. This packet selects no canonical map.

## Calibration and friction-angle conflicts remain

Eqs.(25)-(32), p.842/PDF10, were visually reinspected. At `vi=vf=0,Rf=3,Ei/sigma3=3`, printed Eqs.(26)-(29) give

```
(c1,c2,c3,c4) = (1,25/8,-25/8,225/16).
```

Substitution in the **printed** Eq.(25) matrix, minus its right-hand side, yields exact residuals

```
(25/12,-25/4,-225/4,-25/4).
```

The same printed matrix is solved by `(1,25/8,25/8,225/16)`, consistent with its second row and the `c2=c3` specialization Eq.(31). This is an algebraic candidate only; it does not establish a generally corrected Eq.(28), a physical parameter range or source authority. Table II's actual loose/dense coefficients have unequal `c2,c3`; they must not be forcibly specialized.

Eq.(33), p.843/PDF11, visibly prints `arcsin((Rf+1)/(Rf-1))`. Its argument is greater than one for every `Rf>1`. A Mohr-circle geometric construction with positive compressive principal stresses would give radius/center `(Rf-1)/(Rf+1)` from `center*sin(phi)=radius`. This explains a reciprocal candidate; it does not authorize changing the source formula. At `Rf=3`, the printed argument is `2`, while the geometric candidate is `1/2`.

The bounded lookup on 2026-10-31 opened the DOI (tool reported inaccessible) and searched publisher corrections for the exact DOI. Publisher article/PDF and abstract results were found, but no correction text was inspected or adopted. The original source is complete enough to identify these contradictions; absence of an erratum in this small search is not evidence that none exists.
