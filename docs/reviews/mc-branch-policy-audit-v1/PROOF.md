# Exhaustive H=0 classifier: exact arithmetic proof

This proof uses the source-pinned H=0 formulas in `docs/ingestion/mohr-coulomb/FORMULAS.md`: Sysala–Cermak arXiv1508.07435v3, pp7–13, Eqs3.1–3.6 and4.8–4.29. It does not extend the strict parameter domain `K,G,c>0`, `0<s=sin(phi)<1`, `0<d=sin(psi)<1`, `cos(phi)>0`. The proof is exact mathematics, not a floating classifier guarantee.

Let `x=t1−t2>=0`, `y=t2−t3>=0`, `a=g_sl=x/[2G(1+d)]`, `b=g_sr=y/[2G(1−d)]`, `L=g_la`, `R=g_ra`. Then

```
L = [(1+d)a + 2(1−d)b]/(3−d)
R = [2(1+d)a + (1−d)b]/(3+d)
L−R = 3(1−d²)(b−a)/(9−d²).
```

Both are strict convex combinations of a,b when a≠b. Therefore:

- a<b: `a<R<L<b`; the source right interval `[b,R)` is empty; `max(L,R)=L`.
- b<a: `b<L<R<a`; the source left interval `[a,L)` is empty; `max(L,R)=R`.
- a=b: `a=b=L=R`; both edge intervals are empty.

These statements include a=0 or b=0. Hydrostatic trial means a=b=L=R=0.

## Positive denominators

The four affine q slopes are strictly negative because their denominators are

```
D_s = 4Kds + 4G(1+ds/3)
D_l = 4Kds + G(3−s−d+ds/3)
D_r = 4Kds + G(3+s+d+ds/3)
D_a = 4Kds.
```

`3−s−d+ds/3>4/3`: it decreases separately in s,d on(0,1), with infimum4/3 at the excluded corner(1,1). All other positive terms are explicit. This holds even when Lamé `K−2G/3` is negative. The transition denominators `2G(1±d)` and `2G(3±d)` are also strictly positive. No restriction `psi<=phi` was used or needed.

## Continuous decreasing scalar function

Let each branch have source affine function `q_j(gamma)=N_j−D_j*gamma` and root `gamma_j=N_j/D_j`. Direct substitution in source numerators gives

```
q_s(a)=q_l(a), q_s(b)=q_r(b),
q_l(L)=q_a(L), q_r(R)=q_a(R).
```

For example `N_s−N_l=(D_s−D_l)a`, with `D_s−D_l=G(1+s)(1+d)`. Similarly `D_s−D_r=G(1−s)(1−d)`. The check script verifies all four continuity identities independently using Fractions at every sampled trial.

There is consequently a continuous strictly decreasing q on gamma>=0:

- a<b: q_s on[0,a), q_l on[a,L), q_a on[L,infinity).
- b<a: q_s on[0,b), q_r on[b,R), q_a on[R,infinity).
- a=b: q_s on[0,a), q_a on[a,infinity).

When the trial yield F<=0, the explicitly selected elastic update gamma0 is admissible; F=0 belongs to elastic. For F>0, q(0)=F>0 and q tends to minus infinity. Thus it has exactly one positive root, in exactly one of those half-open intervals.

## Equivalence of the proposed classifier

Set M=max(L,R), m=min(a,b).

1. `gamma_a>=M` iff `q_a(M)>=0`, iff `q(M)>=0`, iff the unique global root is >=M. This selects exactly the source apex interval, including its lower equality.
2. Otherwise the root is <M. `gamma_s<m` iff that root lies in the smooth interval(0,m), selecting exactly the smooth source face. Since F>0, gamma_s>0 automatically.
3. Otherwise the root is in[m,M). If a<b this interval is the left interval[a,L); if b<a it is the right interval[b,R). The selected affine edge root is positive and satisfies both exact endpoint inequalities.
4. If a=b then m=M, so steps1–2 already exhaust every positive root. The final `otherwise right` tie arm is unreachable in exact arithmetic. It assigns no extra mathematical branch.

There are no gaps and no overlapping admissible branches. At face/left equality the left branch owns the state; at face/right equality the right branch owns it. At edge/apex equality apex owns it. At the coincident a=b transition, face meets apex directly; apex owns equality. When the transition is gamma0 and F0 (including repeated/hydrostatic elastic yield), step0's elastic test owns it.

## Reconstruction and differentiation domains

For the ordered trial eigenprojectors Pmax,Pmin and returned principal stresses r1>=r2>=r3,

```
face: r2 I + (r1−r2)Pmax + (r3−r2)Pmin
left: rl I + (r3−rl)Pmin, rl=r1=r2
right: rr I + (r1−rr)Pmax, rr=r2=r3
apex: c*cos(phi)/sin(phi) I.
```

These follow directly from P1+P2+P3=I and do not require arbitrary projectors inside repeated eigenspaces. A selected smooth face has m>gamma>0, hence both trial gaps are positive and every ordinary eigenvalue used is simple. A selected left edge has a<L, which implies a<b and y>0: the minimum is isolated and the upper-pair sum/projector complement remain differentiable even if t1=t2. The right statement is symmetric. Apex needs no trial projector; elastic returns the trial tensor directly. Therefore branch-local lazy ordinary spectral operations suffice on the entire strict *mathematical* source domain, including repeated trial pairs and hydrostatic trial.

At a selected branch equality AD differentiates that branch expression. It need not equal the derivative of an adjacent branch and is not a unique classical derivative of the nonsmooth overall map. Apex returned-stress derivative with respect to trial stress is zero at fixed parameters; parameter sensitivity is not zero: `d(c cot(phi))=cot(phi) dc−c csc²(phi) dphi`. The residual `sigma+return_source(−trialAtlas)` has identity derivative with respect to current sigma when trialAtlas uses old sigma_n; the stress-update tangent with respect to old stress/loading is a different derivative.

Atlas uses source trial `−(sigma_n+C:de)` and accepted Atlas stress `−return_source`. Thus `sigma+returned_source=0` has the correct compression sign and the source tensile apex becomes a negative Atlas hydrostatic stress. The source left/right labels reverse repeated upper/lower Atlas principal pairs; do not relabel them silently.

## Floating limitations and smallest next study

Exact exhaustiveness does not prove raw binary64 comparison stability near a boundary. Independently rounded thresholds/roots may disagree, and mathematically valid extreme inputs may trigger overflow, underflow or the generic selected-gap diagnostic. A declared rejection with committed-state rollback preserves the physical source domain; silently clipping or trying another branch would change the stated algorithm. No new physical cutoff, cap, void ratio or dilation/friction ordering is justified here.

Freeze stored-input references before observing compiled model results. At minimum test: open interiors of all5 branches; all4 equality types including a=b; zero-gamma yield; both repeated trial pairs; hydrostatic elastic/apex; dense rotations; all38 directions for current stress, old stress and loading through actual generated contexts; parameter sensitivity via an explicitly supported parameter interface; selected/unselected failure and transactional rollback. Include one-sided boundary perturbations and source subgradient/order/yield checks, not only return-yield residuals. Keep classification identity separate from value/tangent accuracy near rounded boundaries. Large-mean/small-gap classifier intermediates and mixed-scale middle reconstruction need dedicated range cases.


## Source-equivalent gap arithmetic in adopted v2

The proof applies unchanged to `L=(x+2y)/[2G(3−d)]`, `R=(2x+y)/[2G(3+d)]` and `gamma_a=[F−(1+s/3)x−(1−s/3)y]/D_a`. Substitution of `t1=mean+(2x+y)/3`, `t3=mean−(x+2y)/3` gives the source numerator exactly. The same substitution yields left numerator `F−(1+s)x/2` and right numerator `F−(1−s)y/2` if ever needed; those last two are audit identities, not changes to current ordinary gamma expressions. See check_gap_identities.py and the separately retained v1/v2 source reports.
