# Clay2005 independent finite isotropic references

Prospectively frozen source-only study, REF-clay2005-isotropic-finite-v1. This packet supplies five monotonic, equal-diagonal strain-path endpoints from the same illustrative 100 kPa / e=0.8 state. It does not evaluate Atlas, the retained source oracle, an integrator or compiled code, and makes no preparation, experiment, public-laboratory or admission claim.

## Source and sign crosswalk

[Mašín (2005), A hypoplastic constitutive model for clays](https://doi.org/10.1002/nag.416); [accepted manuscript](https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf), 26 pages, 718767 bytes, SHA256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`. We rely on the previously reviewed Appendix C Eqs73–85 (PDF pp24–25), p10 Eqs38/40/41, Table I and the additive [PLUS correction](../rate-study-v2/SOURCE_CORRECTION.md), [independent audit](../rate-review-v1/README.md), and [contract crosswalk](../compiled-plan-v3/README.md). These retained receipts are pinned by hash in the freeze. No new PDF inspection is claimed; final-publisher equation equivalence remains unverified. No private PDF/full text or supplied author code is bundled or executed.

Source tension-positive T and stretching D map to compression-positive stress sigma and strain E as T=-sigma, D=-E. Restrict sigma=pI, E=dI and zero spin. Then H=I/3, Hdev=0, F=1, Q=3+a², Y=Yi=sqrt(3)a/Q, m=-(a/Q)I and unit m=-I/sqrt(3). Appendix C's stiffness action gives L:I=(3c1+c2a²)I=QI. The source nonlinear action N=L:(-Y unit m), with ||D||=sqrt(3)|d|, therefore gives

    p_dot = fs Q (d - fd Yi |d|),     e_dot = -3(1+e)d.

This independently tracks both stress signs. It agrees with the printed PLUS unloading bracket of p10 Eq38, not the superseded extraction error. The retained Cartesian oracle was read only to inspect the reviewed source crosswalk; none of its functions were imported or executed.

Appendix C coefficients are a=sqrt(3)(3-sin(phi))/(2sqrt(2)sin(phi)); alpha=ln(((lambda-kappa)/(lambda+kappa))*Q/(a sqrt(3)))/ln2; Delta=Q-2^alpha a sqrt(3); c1=2Delta/(9r), c2=1+3(1-c1)/a²; fs=3p/(lambda Delta), fd=(2p/pe)^alpha, pe=p_ref exp((N-ln(1+e))/lambda). Thus K=3Q/(lambda Delta)=3(lambda+kappa)/(2lambda kappa). The parameter r cancels from this isotropic stiffness action; this is not a new fit or omission from the full model.

## Closed form and checks

Let x=|axial strain| and eta=sign(axial strain), fixed on each monotonic path. Each principal strain is eta*x; volumetric strain is 3eta*x. Conservation integrates exactly:

    1+e = (1+e0) exp(-3eta*x),  pe=pe0 exp(3eta*x/lambda).

Define q=fd^-1=(2p/pe)^(-alpha), h=alpha(3/lambda-K), g=alpha K Yi. Direct differentiation of ln q gives q_x=eta*h*q+g. Consequently

    q=q0 exp(eta*h*x)+g (exp(eta*h*x)-1)/(eta*h),
    p=pe/2 * q^(-1/alpha).

The zero path is assigned the exact original p0/e0. For h→0 the quotient tends x and q→q0+g*x. The helper explicitly implements this limiting branch. For the frozen coefficients h<0, g>0, alpha>0, Delta>0. Loading has positive fixed point q*=-g/h=2^-alpha, and q=q*+(q0-q*)exp(hx)>0; unloading has b=-h>0, q=q0 exp(bx)+g(exp(bx)-1)/b>0. Hence p stays positive. Void ratio remains nonnegative up to compression x=ln(1+e0)/3≈0.195929, well beyond these endpoints. These statements concern the mathematical isotropic path, not every numerical stage or general material admissibility.

An independent coefficient/sign check uses p=pe (NCL): Yi fd=(lambda-kappa)/(lambda+kappa), giving loading dlnp/dx=3/lambda and unloading dlnp/dx=-3/kappa. The script compares the positive magnitude K(1+Yi fd) to 3/kappa. The chosen initial state has pe0≈1.2824 MPa, so it is not asserted to be an NCL or source-prepared specimen. Its extension path is simply monotonic unloading from the supplied state.

The q transform degenerates at alpha=0; this branch requires a separately derived limit of the original p equation. Delta=0 makes fs singular; kappa=0 gives unbounded isotropic stiffness. These are outside the regular frozen inputs. This packet does not extrapolate the formula through such singularities. The h=0 quotient limit alone does not cure alpha=0. There is no physical time, finite-rotation, shear, cyclic reversal, general control or strain-partition claim.

## Freeze, results and prospective gates

`prospective-freeze.json` was written and its hash sent to the coordinator before calculation: `2f51139b8a9114f6e7d2f30b956061b8cfb1fbf866242c3a6b13728e4855e56d`. Each literal has its binary64 hex and exact integer ratio; Decimal calculations start from those ratios, not ideal decimal values or a reconstructed angle. Requested phi .3944444109507185 and recorded .39444441095071853 parse to the same binary64. The five Table I base defaults are phi,lambda,kappa,N,r; p_ref=1000 Pa is the fixed pressure normalization. Initial e=.8 is retained as its actual binary64 value.

| Equal principal strain target | p (Pa), rounded for display | e, rounded for display |
|---|---:|---:|
| +.002 | 122575.045509212858 | .789232335297083520 |
| -.002 | 79913.338628571919 | .810832464897316802 |
| +.01 | 270546.907031774989 | .746801960387314760 |
| -.01 | 33024.607966434419 | .854818161116330387 |
| 0 | 100000 | actual binary64 .8 |

`references.json` retains full 80/160-digit calculations, seven-component Mandel state [p,p,p,0,0,0,e], density factors, ODE derivatives, residuals and prospective budgets. All five endpoint convergence checks and both precision sets of coefficient/ODE checks pass the frozen 1e-60 scaled threshold. Largest 80/160 pressure discrepancy is below 6.56e-80 scaled; void below 1.05e-79. This is convergence evidence, not a certified transcendental error bound or proof of the full source law.

For a separately frozen finite-driver study, all six stress channels have absolute budget 1e-5*max(1 Pa, reference p); void has absolute budget 1e-6. Shear references are exactly zero. The gates were fixed before reference calculation and remain unchanged; no observations from compiled code are present. These source finite-path budgets do not alter any old 41 instantaneous-rate vector, finite-only support gate or near-boundary diagnostic. Coordinator must bind actual driver/candidate, full explicit initialization, partition settings, controls and endpoint strain convention before execution; verify equal diagonal controls and volumetric strain independently, and retain any integration failure.

## Reproduction

Run with only the Python standard library:

```sh
python3 -B docs/ingestion/hypoplastic-clay-2005/isotropic-finite-v1/check.py --root /Users/bmar5496/code/constitutive-atlas
```

The check regenerates freeze/references into a fresh temporary directory, compares exact JSON, checks hashes and finite endpoint gates, and writes no repository files. `reference.py` uses its own Decimal sine series, ln/exp and closed form; it contains no Atlas import or source-oracle evaluation. `manifest.json` identifies every other packet file. Initial script development failed parsing `else0`; that failure is retained in `initial-failure.txt`. Before numerical evaluation the token was corrected and the zero-identity checker was placed in the matching precision context. No reference, gate or source equation changed in response to a numerical failure. No numerical/domain/convergence failure was observed.
