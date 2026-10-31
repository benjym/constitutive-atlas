# Multilaminate cap-sign technical decision v1

DECIDE-multilaminate-correction-ledger-v1, 1 November 2026. AI technical analysis; scientific review unsigned. Source-only, bounded to existing equations. No source expansion, author-code execution, model/backend calls, builds or shared edits. Existing immutable ingestion packets remain unchanged.

**Propose the Appendix D minus denominator as a derived correction to Eq36, conditional on retaining the thesis's local primary-compression and N–T elastic compliance meanings.** This is more than an arbitrary preference between two printed signs, but is not proof of author intent, implementation equivalence or scientific signoff. The selected full anisotropic/recovery/nonlocal model remains unresolved.

## Derivation and assumptions

Use source tension-positive strain/stress, but positive magnitudes Q=-sigma_nc and compressive local strain increments du=-d epsilon_n. Work on a scalar compressive cap loading path at tau=0, no competing plastic surface, positive Q and p_ref, constant reference parameters, real power domain, m!=1. This is a local one-dimensional consistency limit, not a claim to predict a complete macroscopic oedometer test.

With a(Q)=(p_ref/Q)^m, the source gives:

1. Eq35 (printed20/PDF38): Q_new^(1-m)=Q_old^(1-m)+K*(m-1)*p_ref^(1-m)*delta_epsilon_n_cap_p. Differentiation gives dQ=K*p_ref^(1-m)*Q^m*du_p, hence plastic compliance Cp=du_p/dQ=a(Q)/(K*p_ref).
2. N–T compliance Eq24 and Appendix C.2 (printed178/PDF196): Ce=a(Q)*(1-2nu_ur)/Eur_ref on the same scalar stress coordinate. This uses the isotropic reference N–T elasticity, not an unspecified degraded anisotropic compliance.
3. Appendix C.3 (printed179/PDF197), read as the total local normal-compression relation illustrated in Fig C.1/68: primary slope dQ/du=3Eoed_ref*(Q/p_ref)^m, hence Ct=a(Q)/(3Eoed_ref). The factor three is source-specific; substituting a standard global oedometer modulus relation would be unjustified. The Chapter3 p20 factor-three explanation is corroborating evidence.
4. Additive strain decomposition du=du_e+du_p requires Ct=Ce+Cp. Cancel a(Q)>0 and solve:

   Kminus=3/[p_ref*(1/Eoed_ref-3*(1-2nu_ur)/Eur_ref)].

The printed PLUS instead gives Cp=a*(1/(3Eoed_ref)+(1-2nu)/Eur_ref); adding the elastic part yields Ct_actual=a*(1/(3Eoed_ref)+2*(1-2nu)/Eur_ref). Thus it cannot preserve the same C.3 primary relation except at zero elastic compliance. It could define a different law if Eoed or the primary relation were reinterpreted; doing so is an underdetermined model change, not an algebraic repair to the same definitions.

## Domain and counterexamples

For Eoed_ref,Eur_ref,p_ref,Q>0 and 1-2nu>0, positive finite plastic compliance and hardening require Eur_ref>3*(1-2nu)*Eoed_ref. This is an additional admissibility requirement for this scalar interpretation, not a claim that the thesis completely specifies all parameter domains. At equality Cp=0: a rigid-plastic-hardening limit could be defined separately, but the literal K is infinite/undefined. Below it, Kminus is negative and compressive plastic flow would soften the cap; it is incompatible with the intended positive-hardening interpretation. Do not hide either case with an epsilon denominator or the listing's m clamp. m=1 remains a separate unresolved limiting-law choice; positive real-power bases remain required.

Exact rational witnesses (Eoed_ref=1000,nu=1/5,p_ref=100; arbitrary consistent stress units):

| Eur_ref | Ce at Q=p_ref | intended Ct | Kminus | Kplus | total compliance using plus |
|---|---|---|---|---|---|
| 3000 | 1/5000 | 1/3000 | 75 | 75/4 | 11/15000 |
| 1800 | 1/3000 | 1/3000 | undefined | 15 | 1/1000 |
| 1500 | 1/2500 | 1/3000 | -150 | 150/11 | 17/15000 |

These are algebraic witnesses, not claimed source-calibrated parameter sets. For the first row the plus law implies effective Eoed=5000/11, rather than 1000. Both signs coincide only in the zero-Ce limit (e.g. formal Eur→infinity); that degenerate limit cannot distinguish the signs. Ordinary isotropic elastic positivity alone does not ensure the new cap-hardening inequality. This analysis does not establish how the full cross-anisotropic degraded stiffness should enter a redefined K, nor show its macroscopic oedometer response.

## Cap root and POP: narrower conclusions

Eq32/B.5 supplies sigma_nc^2=sigma_n^2+tau^2/M_CP^2. With M_CP>0 and the explicit negative compressive cap-intercept convention, select sigma_nc=-sqrt(sigma_n^2+tau^2/M_CP^2); equivalently define magnitude Q by the positive root. The yield equation alone cannot distinguish the two signs. Changing B.5 to an absolute-value/magnitude definition, or adding the negative root under the existing signed-intercept meaning, is a convention repair, not a new cap shape. This does not determine GetAcap, minimum cap/cohesion logic, selection across current/prestress states or zero-Q behavior.

B.1/B.3 print sigma_pv=sigma_v0+POP and sigma_ph=K0nc*(sigma_v0+POP); Appendix D subtracts abs(POP) under negative compressive stress. If POP denotes a nonnegative magnitude of extra prior compressive overburden P, compression-positive magnitudes obey p_pv=p_v0+P, hence signed source stress must be sigma_pv=sigma_v0-P. Under that explicit meaning the code's sign is consistent. But plus is also consistent if POP is instead a signed nonpositive source-stress increment, or B.1 uses pressure magnitudes. Existing equations do not uniquely establish a universal input encoding. Declare P>=0 explicitly in a corrected variant rather than silently copying abs(), and keep prior raw signed input incompatible/explicitly converted. Which branch wins when OCR and POP coexist is not fixed by sign reasoning: code's POP-overrides-OCR is an algorithmic choice requiring review. Likewise do not infer a complete prestress/preparation policy from these signs.

## Proposed ledger disposition and reviewer questions

- HARDENING: `derived_correction_conditional`, adopt MINUS only in an explicitly named corrected variant retaining C.3/N–T/additive meanings; keep Eq36 PLUS and listing provenance visible. Reviewer must affirm C.3's total-strain interpretation and assess the parameter inequality and use alongside anisotropic stiffness.
- CAP ROOT: `convention_repair_conditional`, negative signed intercept / positive magnitude, with declared nondegenerate domain. Reviewer must approve preparation branches and missing helper contract separately.
- POP: `explicit_convention_choice`, nonnegative prior compression magnitude with subtractive source-stress conversion is defensible; historical input semantics and OCR/POP precedence remain unresolved, not algebraically closed.

No numerical campaign is needed to make these distinctions. Next action is scientific review of this proposed correction ledger; this worker neither selects the remaining full-model choices nor assigns a reviewer.

## Source receipts and inspection

Primary: Bert Schädlich, *A Multilaminate Constitutive Model for Stiff Soils*, TU Graz dissertation, April2012, https://doi.org/10.3217/wmxdh-rg587 . Private PDF SHA256 43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9. Read the existing base-laws, host-contract, Hvorslev and full-formulation packets first; targeted PDF197/C.3 was re-rendered and visually inspected using the PDF skill. Other locators reuse their already recorded visual receipts and targeted existing extracted text. Sources and render hash are in findings.json. Raw PDF/render/extracted text remain private and are not payload. Two requested payload files only: README.md and findings.json. Source-only Fraction calculation reproduced the three exact rows above; no failed probes or runtime observations occurred.
