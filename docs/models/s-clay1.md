# S-CLAY1 — Wheeler et al. (2003)

S-CLAY1 describes directional yielding in normally or lightly overconsolidated soft clay. An inclined yield surface changes both size and orientation during plastic deformation. Elastic stiffness increases with pressure. Plastic compression and shear drive fabric toward different stress-dependent directions.

This exact implementation uses the original constant-M, full three-dimensional tensor law in Wheeler, Näätänen, Karstunen and Lojander, *Canadian Geotechnical Journal*40,403–418(2003), DOI[10.1139/T02-119](https://doi.org/10.1139/T02-119). It is distinct from S-CLAY1S, bonding/destructuration and creep extensions.

## Equations and conventions

With effective Cauchy stress σ′, p=trσ′/3, s=devσ′, traceless dimensionless fabric A, a²=3A:A/2 and t=s−pA, yield is F=3t:t/2−(M²−a²)(pm−p)p≤0. Associated flow is dεp=dl∂F/∂σ′. Elasticity uses K=vp/κ and G=3K(1−2ν)/(2(1+ν)). Size evolves as dpm=vpm dεvp/(λ−κ). Fabric evolves as dA=μ[(3s/(4p)−A)〈dεvp〉+β(s/(3p)−A)dεdp], where dεdp=√(2devdεp:devdεp/3). The positive-part brackets suppress volumetric rotation during plastic dilation; shear rotation remains active.

Source: p404Eq1–2/associated-flow paragraph, p405Eq3–5, p408Eq7–9 and AppendixA1–A14pp417–418. Appendix explicitly uses Mandel shear components. The original optionally discusses different compression/extensionM or shifted-Lode dependence; the implemented constantM option is the one used in the paper's examples.

The implementation declares schema0.3, fixed Cartesian infinitesimal strain, compression-positive stress/strain, Mandel order xx,yy,zz,√2xy,√2yz,√2xz, and strain-path incremental residuals. It supplies no physical clock or finite-spin transport. Full tensor rotation covariance is a change-of-basis check, not finite-rotation objectivity.

## Starting state and parameters

Supply six effective stress components, six traceless fabric components, specific volume v=1+e and positive yield size pm. Initial F must be nonpositive within disclosed solver tolerance. Require p>0,v>1,M²>a²,λ>κ>0; μ,β≥0 and−1<ν<.5. JSON parameter bounds are input safeguards, not a qualified full parameter envelope. p_ref is numerical stress scaling only.

λ and κ measure slopes of specific volume against natural logarithm of pressure. M controls the critical-state stress ratio; ν relates elastic shear and bulk moduli. β balances shear-driven and compression-driven fabric rotation; μ controls its rate. Initial fabric must reflect loading/preparation history. SourceEq13–14 provide approximate K0-based estimates for normally/lightly overconsolidated one-dimensional preparation with predominantly plastic straining; they are not universal initialization rules.

The illustration uses original Otaniemi constants λ.44,κ.04,M1.1,ν.2,β.67,μ20, and Table4 v3.46/pm17.6kPa. Its stress[20,12.5,12.5,0,0,0]kPa is an Atlas interior example; A=diag(.28,−.14,−.14) embeds scalarα.42. This combination does not reproduce a measured specimen or test.

## Atlas integration choices

The common engine solves endpoint stress, fabric, specific volume and size simultaneously, with temporary scaled multiplierγ=p_ref dl. Its associated stress gradient uses the dimensional yieldF; normalizedF/p_ref² appears only in Fischer–Burmeister complementarity. Endpoint stiffness/fabric and exponential updates v=v_nexp(−trde), pm=pm_nexp(v dεvp/(λ−κ)) are Atlas finite-step choices. The original used tiny stress increments with complianceEq15–16. Refinement against that independent differential reference qualifies convergence of the alternative implementation; backend agreement alone is insufficient.

Zero strain preserves the persistent state and causes no creep. Loading, unloading and dilation retain the same source law. Failed increments roll back the complete parent; mixed-control trials restart from that parent. Restart requires every persistent tensor/scalar and compatible parameters/history, with temporaryγ reset. Existing nonsmooth AD conventions are used atzero norm/positive-part corners. No consistent FE material tangent is exposed.

## Supported illustrations and meaningful limits

Bounded monotonic drained and undrained axial strain demonstrations use1%/100steps, with named source-parameter edits and full tensor/analytical/reference checks documented in the [source packet](../ingestion/s-clay1/supplied-original-v3/README.md). Other public protocols and cycles are disabled pending qualification. Library checks include bounded elastic unload/reload and failure recovery; these do not establish realistic cyclic behaviour.

The source omits elastic anisotropy and small-strain nonlinear stiffness. It cautions against cyclic loading, unloading-dominated applications and predominantly dry-side yielding. Bonding/destructuration are absent; original sensitive-clay examples substantially underpredicted some post-yield volume strains. No experimental calibration, general parameter validity, finite-strain/spin or FE-host qualification is claimed. [Independent review and exact numerical evidence](../ingestion/s-clay1/supplied-original-v3/DELIVERY_NOTES.md) remain distinct from website/browser/live delivery.
