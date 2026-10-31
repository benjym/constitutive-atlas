# Multilaminate algebra-choice review v1

Bounded AI technical review for DECIDE-multilaminate-correction-ledger-v1, 1 November2026. It reuses the pinned spectral/Hvorslev/full-formulation evidence for [Schädlich2012](https://doi.org/10.3217/wmxdh-rg587), PDF SHA43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9. No new source acquisition, PDF reading, packet rerun, micro-audit, model/backend call, author execution, build or shared edit was performed. These conclusions are proposed ledger dispositions, not independent scientific signoff or authorization for an executable variant.

**LAW-02: two conditional repairs are algebraically compelled.** Given Eq94's orthonormal Kelvin basis, its normal2x2 block is H=[[a,b],[b,d]], where a=(1−nu_hh)/Eh, d=1/Ev, b=−sqrt(2)nu_hv/Eh. Let Delta=sqrt((a−d)^2+4b^2), lambda2=(a+d−Delta)/2 and lambda3=(a+d+Delta)/2. For Delta>0 the unique ordered projectors in this block are

```
P2 = (I − [2H−(a+d)I]/Delta)/2  # low eigenvalue
P3 = I−P2                      # high eigenvalue
```

Embedding uses u=(xx+zz)/sqrt2 and v=yy. An equivalent low-mode angle is omega=atan2(−2b,d−a)/2 modulo pi. The tangent identity tan(2omega)=2b/(a−d) alone does not select a mode; atan2(2b,a−d)/2 selects the **high** eigenvalue along (cos,sin), so it cannot silently replace A.2 while retaining source labels. At b=0 and a<d choose P2=diag(1,0); at a>d choose diag(0,1). At a=d,b≠0 use the projectors, with no division by a−d. This is a conditional Eq94-consistent correction to A.2, supported separately by AppendixD's difference/Eh formula. It is not an assertion that every printed A.2/AppendixD branch is equivalent for every parameter sign.

When Delta=0, H=aI: only P2+P3 is determined; no unique omega exists. Other coincident lambda families likewise do not define unique projectors by eigenvalue alone. Elastic reconstruction is basis-independent within a repeated eigenspace; continuation of mode-dependent history/degradation in the whole nonlinear scheme is **not settled** by this identity. Do not divide by a spectral gap or introduce an unreviewed mode-tracking rule.

Given raw symmetric stress S and unit n, n·S·n contains 2n_x n_z S_xz. Thus Eq104's c2 final raw-stress coefficient must be **2n_x n_z** under its stated basis, matching AppendixD and the retained −4/9 versus printed−2/9 witness. Separately, if sigma_K=M sigma_raw with M=diag(1,1,1,sqrt2,sqrt2,sqrt2), the complete Kelvin projection is P_K=P_raw M^−1. That converts every raw global shear column, not only xz. Engineering strain maps to Kelvin strain as epsilon_K=M^−1 epsilon_engineering. Repeated yy normal labels must become zz given the declared six-component basis. These basis identities do not settle the source's full local work metric or coupled assembly. In particular C_local=P_K C P_K^−1 is the stated **similarity**, not an orthogonal rotation or a compliance congruence.

Neither angle nor traction repair fixes singular local transformations. The existing n=(3/5,4/5,0), s=(−4/5,3/5,0), t=(0,0,1) witness has an identically zero normal-stress contribution to t traction and is singular despite not being axis-aligned. Actual prepared directions and conditioning need explicit selection; no pseudoinverse, perturbation or replacement quadrature is compelled.

**LAW-03: reciprocity is compelled; interpolation choice is not.** With z the already defined log-degradation fraction, two distinct options are:

```
D-listing option:
  nu_hv(z)=(1−z)nu_hv0+z nu_ur
  nu_vh(z)=nu_hv(z) Ev(z)/Eh(z)
Fig29-label option:
  nu_vh(z)=(1−z)nu_vh0+z nu_ur
  nu_hv(z)=nu_vh(z) Eh(z)/Ev(z)
```

They share reciprocal endpoints but generally differ inside the path: the retained midpoint gives nu_vh=9/100 versus1/8. Neither symmetry nor energy positivity determines which to adopt. A proposed corrected variant may explicitly choose the listing option for implementation-lineage fidelity; it cannot call that choice mathematically forced or identical to Fig29. Require reciprocal compliance and positive moduli with −1<nu_hh<1 and 2nu_hv²<(1−nu_hh)Eh/Ev throughout the interpolated/pressure-scaled path, not only endpoints. Engineering/raw versus Kelvin conversion is separately compelled as above; it does not resolve the interpolation ambiguity.

**LAW-04: positive Bcs is compelled for the fixed nondegenerate intersection.** Retain p=−sigma_n>0, Q=−sigma_nc>0, qe=−sigma_ne>0, tau≥0, tcs=tan(phi_cs)>0, te=tan(phi_e). From the cap and CSL,

```
p_cs=M_CP Q/sqrt(M_CP²+tcs²)
tau_cs=p_cs tcs
qe_cs=[Q^(1−m)+A(p_cs^(1−m)−Q^(1−m))]^(1/(1−m))
fHV=tau−p te−Bcs(1−te/tcs)qe
```

At that point fHV=(tcs−te)[p_cs−Bcs qe_cs/tcs]. Therefore, **if te≠tcs**, Bcs=p_cs tcs/qe_cs>0. C.5's consistent signed equality is Bcs=−tau_cs/sigma_ne_cs=sigma_n_cs tcs/sigma_ne_cs. Its first printed ratio must acquire a minus sign (or use the absolute denominator), given the fixed positive-resultant shear convention. The retained rational witness p60,Q100,qe80,tau48 gives Bcs=3/5; the literal first ratio is−3/5. At te=tcs, B cancels completely: that one degenerate intersection cannot determine B. Reusing the generic positive coefficient there is a declared continuous extension, not a new derivation from that point alone.

This repair assumes M_CP>0, positive Q/p/qe, m≠1 as printed, and a strictly positive inner power base. It does not choose cap shape/prestress or repair missing preparation. The m→1 limit is a separate definition, not permission to conceal the printed singularity. Local intersection is not macroscopic simultaneous intersection across yielding planes.

**LAW-01 remains dependent on the cap/hardening decision.** None of the preceding identities chooses the Eq36/AppendixD hardening denominator, GetAcap preparation root, POP sign/branch or initialization. Record this as unresolved pending the separate cap reviewer/parent consolidation; do not imply LAW-04 determines Q evolution. LAW-02 and LAW-04 can be marked “conditionally derived proposed correction; scientific approval pending”; LAW-03 stays “explicit variant choice required,” and LAW-01 stays unresolved here. A named corrected Atlas variant must preserve the printed alternatives and these assumptions before implementation. No new numerical study is justified by this bounded review.
