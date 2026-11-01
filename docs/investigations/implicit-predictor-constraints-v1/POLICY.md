# Prospective generic predictor-constraint capability policy v1

Frozen before any compiled observations in this study. A synthetic declarative incremental law, not a scientific model, isolates transition between the multiplier-zero elastic predictor and full complementarity corrector. No MD equations, requests, physical yield constraint or prior failed reports change.

Scalar reference: p_n>0; K>0; Y>0; volumetric increment v=trace(de). Elastic trial p_tr=p_n+K*v. Exact update p=min(p_tr,Y), gamma=max((p_tr-Y)/K,0), ep=ep_n+gamma, provided p>0 and p<=physical_cap. Stress is isotropic with all normal components p; shear remains zero. Complementarity is gamma>=0, f=(p-Y)/K<=0, gamma*f=0. The fixture residual uses the generic square-root complementarity expression; reference uses only this closed-form projection. Gamma is reset per parent increment, ep persists. An independent physical cap can exclude the only algebraic root even after full correction; that case MUST reject, never return elastic predictor success or clip stress.

Parameter order K,Y,physical_cap =100Pa,10Pa,100Pa. Initial sigma=(1,1,1,0,0,0)Pa, ep=0, gamma=0. Tight fixture integration settings residual_tol1e-12, rate_tol1e-6,max_iterations40,max_depth0,max_substeps1,max_backtracks11. No subdivision may hide failure. Accepted pressure/state absolute error<=1e-8, gamma/ep<=1e-10; every returned success must satisfy yield<=1e-10 (scaled by K), gamma>=-1e-12, p<=physical_cap and p>0. Native/Wasm parity all state components abs<=1e-10; nearzero exact rollback below is stricter. Preserve raw responses, exact requests/settings, engine and generated metadata hashes. Do not relax gates after observations.

Frozen cases in requests.json:

- inside-yield: v=.02 →p3,ep0,gamma0.
- first plastic increment: v=.2 →p10,ep.11,gamma.11. Its converged elastic predictor p21 violates final yield; it must reach the corrector successfully.
- load-unload chain: the prior plastic endpoint, then v=-.04 →p6,ep.11,gamma0. Load again v=.08 →p10,ep.15,gamma.04. Hold v0 →p10,ep.15,gamma0. Preserve restart state and reset transient gamma.
- initially invalid: p=-1, zero increment →reject and preserve full input state; then independent valid recovery inside-yield must succeed.
- domain endpoint invalid: v=-.02 from initial →p_tr=-1, no p>0 root; must reject and restore complete input state, then valid recovery.
- physical-root exclusion: cap8 with v=.2 from initial →the complementarity root p10 is domain-valid but physically excluded; must reject/rollback exactly. Recovery at same cap v=.02 must yield p3. Neither predictor transition nor line search may admit p>cap.
- iteration-budget exhaustion: max_iterations1 and v=.2 must reject/rollback exactly; next ordinary valid step succeeds. No changed settings on successful recovery beyond restoring frozen ordinary fixture settings.

Failures must have ok=false and exact complete original state (including supplied transient before reset where public rollback contract requires it). Accepted steps compare all8state components, not a plotted scalar. Raw failures remain failures. Parent executes native first, then Wasm same requests, then unchanged MD study plus all current16ordinary-model and dedicated-profile regression policies. Independent reviewer assesses actual evidence and code before any shared integration. Source-only checks below do not count as compiled qualification or approval.
