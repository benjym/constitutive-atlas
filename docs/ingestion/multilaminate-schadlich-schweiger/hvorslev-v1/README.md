# Multilaminate Hvorslev strength, softening and nonlocal equations v1

Task SRC-multilaminate-hvorslev-v1; coordinating parent, 1 November 2026. This completes a bounded Chapter6 equation inventory for the [selected thesis formulation](../variant-identity-v1/README.md), not full ingestion, a schema-valid model or scientific admission.

Bert Schädlich, *A Multilaminate Constitutive Model for Stiff Soils*, TU Graz dissertation, April 2012. [Persistent source](https://doi.org/10.3217/wmxdh-rg587). Private PDF SHA-256 `43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9`. Twenty-one complete pages were visually inspected: PDF122–127,140–145,194–197,214,218–219,225–226 (printed pp.104–109,122–127,176–179,196,200–201,207–208). [source-ledger.json](source-ledger.json) pins locators and render hashes. Raw sources remain private; reuse permission is not established.

## Strength boundary and equivalent pressure

Retain tension-negative source normal stresses. Define positive magnitudes `p=-sigma_n`, `Q=-sigma_nc`, `qe=-sigma_ne`, `s=1-m` and `A=3*Eoed_ref*(1-2*nu_ur)/Eur_ref`. On the compressive branch Eqs129–131 become

```
qe = [Q^s + A*(p^s-Q^s)]^(1/s)
cHV = Bcs*(1-tan(phi_e)/tan(phi_cs))
fHV = tau - p*tan(phi_e) - cHV*qe
```

Here tau is the nonnegative local shear resultant; cHV, Bcs, A and m are dimensionless. Stresses, reference moduli and pressure must share units before explicit SI conversion. Eq130 uses absolute stress magnitudes, verified visually; AppendixD p200 writes negative compressive arguments explicitly. Admitted real powers need `p>0`, `Q>0`, `s!=0` and a strictly positive inner base. When A lies outside [0,1], that last condition does not follow from positive p,Q. An even outer power must not conceal a negative inner base.

AppendixC.2–C.3 derives this equivalent pressure from unloading/reloading strain and the primary compression relation. The formula is homogeneous in pressure: scaling p,Q scales qe. At p=Q, qe=Q; A=0 keeps qe=Q and A=1 gives qe=p. Its mathematical m→1 limit is `Q*(p/Q)^A`, but that limit is not the printed m=1 implementation. Fig70 uses m=1 while the host packet records a clamp to0.9999; preserve that distinction rather than silently claiming an exact reproduction.

The cap/cone/tension laws remain necessary; this is not a standalone failure criterion. Page105 expressly allows cone plastic strains before reaching the Hvorslev boundary. Page107 warns that local cap/critical-state intersections do not imply identical macroscopic intersections because other planes may already yield.

AppendixC.6–C.7 gives the local cap/critical-state point:

```
p_cs = M_CP*Q/sqrt(M_CP^2+tan(phi_cs)^2)
qe_cs = equivalent_pressure(p_cs,Q)
```

The square root in C.6 was visually checked. C.5 prints `Bcs=tau_cs/sigma_ne_cs=sigma_n_cs*tan(phi_cs)/sigma_ne_cs`. With positive tau_cs and negative compressive normal/equivalent stresses, its first ratio is negative while its second is positive. A positive-magnitude candidate `Bcs=p_cs*tan(phi_cs)/qe_cs` makes Eq129 intersect `tau_cs=p_cs*tan(phi_cs)` exactly, as the independent witness shows. This is a retained signed-equality failure, not an adopted correction. Bcs depends on cap shape and preparation, not a free fitted cohesion intercept. The prior cap-shape helper/initialization omissions remain open.

## Potentials, derivatives and cap evolution

The cap potential remains associated. Eqs135–137 give `g_cone=tau+sigma_n*tan(psi_m)` and `gHV=tau+sigma_n*tan(psi_HV)`, with `psi_HV=psi_max=phi_max-phi_cs`. Maximum dilatancy follows the current strength boundary; it is not an independent constant. Below critical state the source reuses the basic cubic dilatancy law; Fig71/72 describes the above-critical branch. Full branch choice and its extra research factors still need the consolidated definition.

For fixed cap/prepared state, differentiating Eq130 yields `d(qe)/dp=A*(qe/p)^m`. AppendixB.28–B.32 then gives

```
dfHV/dsigma_n = tan(phi_e) + cHV*A*(qe/p)^m
dfHV/dtau = 1
dgHV/dsigma_n = tan(psi_HV)
dgHV/dtau = 1
local hardening partials dfHV/depsilon_n_HV_p = dfHV/dgamma_HV_p = 0
```

The normal derivative changes sign under `p=-sigma_n`. B.30 specifies a flow-direction partial with psi held as the algorithmic value. Automatically differentiating a substituted stress-dependent psi as though it were the literal potential would add terms absent from this source gradient. B.32 likewise describes the frozen local return, not absence of cap evolution or post-peak damage in the full algorithm. These partials do not establish a consistent full constitutive tangent.

Eq132 combines cap and Hvorslev normal plastic strain in the same power update:

```
Q_new = [Q_old^(1-m) + K*(m-1)*p_ref^(1-m)
         *(delta_epsilon_n_HV_p + delta_epsilon_n_cap_p)]^(1/(1-m))
```

Positive dilatant source strains reduce Q; negative cap compression increases it while the domain holds. K inherits the unresolved plus/minus denominator conflict documented in the [base laws](../base-laws-v1/README.md) and [host contract](../host-contract-v1/README.md). Do not pick a K from this equation inventory.

Eqs133–134 redistribute the Hvorslev strain contribution among planes that have reached their boundary: `delta_d=sum_i(w_i*delta_epsilon_n_HV_p_i)` and `delta_d_i=hsoft*w_i*delta_d`, replacing the corresponding HV contribution in Eq132. These are plane quadrature weights, not spatial neighbour weights. Re-averaging the redistributed contribution scales it by `hsoft*sum(w_i^2)` for the same active set; no unit-sum/conservation identity is stated. Preserve the actual quadrature and active set instead of renormalizing weights or treating the redistribution as a projection of the global tensor.

## Selected spatial nonlocal branch

Eqs140–144 describe alternatives/background. The current model selects Galavi's kernel Eq145:

```
W(r) = (r/l^2)*exp(-(r/l)^2),  l>0, r>=0
```

It has zero self weight, differs from a Gaussian, and remains positive at r=2l. The radius2l neighbourhood cutoff is an additional implementation choice (p125), not compact support of W. The kernel's units are inverse length; its overall scale cancels in the normalized average. A host must still supply physical l, coordinates, consistent influence volumes/areas and boundary neighbourhoods. The source's use of volumes in the general derivation and 2D finite-element areas requires an explicit dimensional host declaration.

Eq146 defines macroscopic damage `d=sum_i(w_i*(epsilon_n_HV_p_i+epsilon_n_cone_p_i))`. In the listing D p207 only **positive** cone increments enter the accumulated damage, whereas the printed Eq146 has no explicit positive-part operator. Preserve this definition/branch question. The Galavi friction/cohesion softening branch is separate and must not be substituted for the Hvorslev branch just because it also calls Non_Local.

Eqs147–149 define

```
Vw = sum_j(W(r_j)*V_j)
d_star = sum_j(d_j*W(r_j)*V_j)/Vw
d_star_i = w_i*d_star
```

Neighbour damage values are known at the **start of a calculation step**, and the spatial average is held while local strains evolve. This is a strain-path lag, not a relaxation time or viscosity. The required snapshot is shared consistently across all material points; in-place neighbour updates would introduce an ordering choice absent from these equations. A rejected trial must not publish damage to other points. Re-evaluating the spatial average on each adaptive material substep is not automatically equivalent to the source calculation-step policy.

Vw must be positive. A single isolated point contributes only W(0)=0 and cannot supply this model's nonlocal average. No local fallback, artificial self weight or prescribed zero damage is introduced. A homogeneous or externally prescribed neighbour history would need an explicit host/benchmark identity and would not establish general spatial regularization.

For the selected **regular post-peak** branch, record `d_star_i_peak` when that plane first reaches the HV boundary. Eq150 derives a separate softened cap from the current hardening-only cap:

```
Q_star = [Q_hard^(1-m) + K*(m-1)*p_ref^(1-m)
          *hsoft*(d_star_i-d_star_i_peak)]^(1/(1-m))
```

Q_hard continues to evolve with cap plastic compression. Q_star is derived from Q_hard plus the accumulated damage since peak; repeatedly applying the whole accumulated damage to the previous Q_star would double-count softening. Pre-peak neighbour softening must not activate this plane early. The alternative modified branch applies averaging from the start (p127); it remains a separately identified variant. The biaxial studies are numerical regularization studies, expressly not reproductions of a particular experiment.

D pp196,207–208 makes additional algorithm choices visible: preserve damage excess with a previous-value maximum, use a stored peak sentinel/threshold, and call Non_Local at most once through a flag. A zero-valued peak damage can be physically distinguishable from 'not reached', but a zero numeric sentinel cannot represent that distinction. The prose's first contact, the listing's positive HV normal-strain trigger, exact ties and the1e-12 threshold require one reconciled event contract. No boolean replacement is silently introduced here. The omitted spatial helper/file lifecycle and full rollback remain gaps.

Page124 limits the approach to finite-width bands with weak/no displacement discontinuity. It does not establish suitability for strong fracture discontinuities or polished residual clay slip surfaces. Chapter6 focuses the Hvorslev formulation on fine-grained soils; do not transfer its clay evidence to Wichtmann sand tests without an applicability justification.

## Integration/schema requirements and next action

The [v0.3 contract](../../../FORMULATION_CONTRACT.md) requires a complete explicit formulation. This inventory emits no partial model or legacy integration flag. The [spectral packet](../spectral-v1/README.md) preserves stiffness/convention failures; none is closed by adding the strength equations.

| Requirement | Source-backed dependency / remaining gate |
| --- | --- |
| Form and time | Time-independent, coupled incremental plastic return plus stiffness/history iteration. Define the complete residual/update and the boundary of a host calculation step; elapsed seconds are not a new material input. |
| Inputs | Strain increment, prepared cap shape/Bcs, reference moduli/pressure/exponent, friction/dilatancy branches, hsoft, spatial l, neighbour IDs/coordinates/volumes and a committed damage snapshot. No implicit neighbourhood default. |
| Persistent state | Keep Q_hard and Q_star distinct; store local plane hardening, damage, peak baseline/activation, nondecreasing damage excess, stiffness contours and prepared metadata. Current32-state engine capacity is insufficient for the preserved source layout. |
| Conventions | Effective plane stresses; explicit source-to-SI, tension-negative to compression-positive conversion of stress and strain; resolve Mandel/engineering shear, fixed material basis and complete stress binding/kinematics/frame declaration. |
| Solving and lifecycle | Coupled nonsmooth surfaces, frozen versus evolving derivative values, domain rejection, transactional neighbour snapshots and restart. Existing source conflicts and unavailable helpers are not solved by a pointwise residual. |

Run `python3 -B check.py --source /private/path/to/thesis.pdf` (source argument optional). [checks.json](checks.json) records seven independent algebra/domain groups, including the signed C.5 failure and definition/sentinel gaps. Exact rational witnesses cover power endpoints, cap/HV/CSL intersection, B.28 sign conversion, derived softening state, plane weights and lagged snapshots. The normalized spatial kernel witnesses use an absolute1e-12 tolerance fixed before observations. No author code, compiled artifact, build, calibration or mesh simulation was executed. Hashes and local links are pinned in [manifest.json](manifest.json).

Stop source expansion here. Next is one consolidated full-formulation decision: resolve or explicitly retain the signed/convention/branch alternatives across the existing packets, define unsupported host capabilities and identify which choices need primary clarification or independent review. Do not start another source micro-audit or a native feature from this packet alone. Complete formulation, executable integration and scientific admission remain separate open gates.
