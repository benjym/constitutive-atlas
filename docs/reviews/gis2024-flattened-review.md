> Archived AI technical review. Original temporary paths and code pins identify the reviewed snapshots; later fix sections supersede earlier findings. Current repository evidence is pinned in the corresponding investigation manifest. This is not human scientific admission.

# Independent flattened14-state HP/extracted-ASBS + GIS review

31 October 2026. Read-only Python/source review; no builds, native execution, repository changes, integration or scientific admission. Reviewed generated JSON under `/private/tmp/atlas-gis-integrate-20261031-v1/models/research/gis2024/hp-extracted-asbs-gis-2024-research.json` and flatten.py; independently compared with `/private/tmp/atlas-gis-coupled-reference-20261031-v1/tools/reference_gis2024_coupled.py` and its38 retained cases. Pinned primary source SHA256 `39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3`; pp3,4,12 reviewed in preceding host review and pp5-7 visually inspected for this extension.

## Source composition and signs

The14 persistent state components are sigma6,e,h6,Omega, all symmetric components in Atlas Mandel order. The HP host construction is the independently reviewed extracted-ASBS pairing, not S=Y. Source pp3 Eqs8-12 and p7 Eq40 give sigma_rhs=k*fs*L(de-m*C*S**(k**gamma)*norm(de)), with explicit f=0. Flattening substitutes the complete linear E action at effective_de and preserves its outer k. There is no double application of k, swapped nested exponent, finite increment interpretation or unintended stress parameter scaling in the physical law. p4 Eq22 density evolution gives e_rhs=-(1+e)*trace(de) after extension-to-compression conversion.

Source p5 Eq33 and p6 Eqs34-35 give hdir=h/norm(h) or0 at zero memory, rho=norm(h)/R and h_rhs=de-hdir*rho**beta_R*(hdir:de) only on positive loading, otherwise de. Simultaneous sign reversal of de,h,m,sigma leaves q,k,rho,C,S unchanged, while tensor derivatives reverse appropriately. Omega is scalar with p7 Eqs41-43 gamma=gamma_chi*(chi_0+Omega*(chi_max-chi_0)) and Omega_rhs=C_Omega*(1-rho**gamma_Omega-Omega)*norm(de). The flattened expressions preserve these source relations.

The rearranged positive/negative-loading k expressions are algebraically equivalent to p6 Eq39 and avoid cancellation at fully mobilized parallel memory. The q=0 branch at exact zero de is an internal placeholder, not a uniquely defined directional k. Setting suppression0 internally on that branch yields all14 zero derivatives; f=0 is essential to that continuation. No public directional-zero-k claim, state reset, endpoint projection or spin update is justified by these expressions. No such action is present.

The exact zero h/de guards detect nonzero component vectors whose squared norms underflow, rather than treating them as zero. Stable double deviatoric projection, raw Lode guard and nonisotropic j2-underflow rejection carry over from the corrected host. The finite bounds are conservative project restrictions, not complete source/physical admissibility. p_scale<=1e12 makes p_scale*1e280 finite, and p_scale>=1 makes inverse-Pa bounds finite. Some finite tensor norms can overflow much earlier because of squared components; honest rejection is narrower than full binary64 representability and must not be called a complete valid-domain implementation.

##38 independent comparisons

`compare.py` evaluates the flattened JSON through atlas.model.interpret, separately calls the independent Cartesian/dense coupled oracle, and compares all14 derivatives as well as rerunning every saved reference. All38 cases pass a1e-10 max(1,abs(x),abs(y))-scaled tolerance. Maximum observed scaled discrepancy is1.0605093896670778e-12 and maximum absolute discrepancy1.862645149230957e-9 (mixed-unit maximum; use component-specific physical tolerances for later solver tests). Fresh independent-reference outputs equal the saved outputs exactly in this environment. This establishes bounded instantaneous composition agreement, not temporal accuracy, trajectory convergence, preservation of domains or experimental agreement.

## Finding: suppression underflow must be rejected or explicitly admitted

For the retained zero-memory fixture, changing gamma_chi to100 (within JSON parameter bounds) gives gamma80,k5,S=.5455592894806933,k**gamma=8.271806125530277e55. Although S>0 and the mathematical suppression is positive, binary64 S**(k**gamma) underflows to0. The original flattened domain silently accepts it for nonzero de. The independent oracle also accepted this, so reference agreement alone did not reveal the numerical policy gap. `comparison.json` retains this pre-fix probe and model hash.

Recommended strict-scope fix, agreed by parent: require suppression>0 when dn>0, retaining internal suppression0 only for exact zero direction. Add the explicit regression to production composition and independent reference. This is numerical representability rejection, not a new source boundary or clipping rule. Post-fix assessment follows once rechecked.

## Integration boundary caveat to retain

The project accepts memory norm up to R*(1+16eps) without mutating input. At h=[R*(1+8eps),0,...],Omega0,de=[1e-4,0,...], the current source rates give rho=1.0000000000000018,Omega_rhs=-7.993605777301128e-18 and h_rhs_xx=-2.710505431213761e-20. This accepted perturbed boundary state therefore points just outside strict Omega>=0. It is a roundoff-policy interaction, not a source-sign defect. The admitted instantaneous-rate domain need not be an invariant domain of the continuous ODE. Do not promise that adaptive shrinking alone can integrate every accepted boundary fixture. Before native trajectory targeting, include this regression and explicitly choose the numerical acceptance policy without silently clamping or altering the law. An exact source state with rho<=1 andOmega0 has nonnegative Omega derivative.

## Reproduction

```sh
PYTHONPATH=/private/tmp/atlas-gis-integrate-20261031-v1:/private/tmp/atlas-gis-coupled-reference-20261031-v1:/Users/bmar5496/code/constitutive-atlas PYTHONDONTWRITEBYTECODE=1 python3 /private/tmp/atlas-gis-full14-review-20261031-v1/compare.py
```

Review evidence/manifest bind the exact snapshots. Later JSON/reference modifications require regenerated pins and checks. No full material admission, endpoint/ASBS-overshoot prevention or integrated-path validation follows from this review.

## Post-fix readiness assessment

The final JSON now requires `select(dn>0,suppression,1)>0`; the production composition and independent paired oracle each reject nonzero-direction suppression underflow. I inspected all three guards and reran the38 independent flattened-rate comparisons: all pass with the same stated error maxima, while the gamma_chi100 counterexample now rejects in both flattened model and oracle. The exact zero-direction case still returns14 zeros. Post-fix evidence is retained separately; the original pre-fix probe remains visible for provenance. Ten reference/composition test groups from the independent packet pass; the installed repository's three composition test groups also pass. The explicit suppression-underflow regression is established by this review's standalone comparison script; it was not present in the installed three-group suite inspected here. An initial attempt to run that suite directly in the integration staging directory failed at setup because its relocated evidence path was absent; running the installed suite resolved this staging-path issue, with no source/test changes.

Installed repository JSON and reviewed stage JSON have identical SHA256 `4bb56e4703172c5a7a7cf8bea5e662442308aee7405fa39e9e24230fd6102fe6`. No remaining blocker identified for a bounded native **instantaneous-rate** target and selected carefully interior small-step diagnostics. That readiness does not extend to every accepted boundary initial state: preserve the roundoff-margin/Omega caveat above and establish numerical integration acceptance separately. Native/compiler cross-backend agreement, state rollback, accumulated histories and physical/source preparation remain later verification gates. No native execution occurred in this review.
