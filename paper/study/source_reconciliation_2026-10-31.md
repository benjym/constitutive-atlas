# Source reconciliation for the paper

Status: assisted review of shared source dossiers and retained numerical evidence, 31 October 2026. This is not a repeated independent review of the original PDFs. The [evidence record](source_reconciliation_2026-10-31.json) pins the inputs; [implementation annotations](model_annotations.json) retain their exact definition identities and historical pilot status.

## Hypoplasticity and IGS

| Identity | Source-specific distinction | Consequence for the comparison |
| --- | --- | --- |
| VW96 | Original eight-parameter host; Eqs. 40–46, pp. 262–263. Table I Hochstetten example uses beta=1.5. | Keep eight material slots in the current implementation annotation. Do not call defaults or the KFS partial calibration a reproduction of this example. |
| IGS97 original | Appendix A, pp. 295–296, uses a seven-parameter host equivalent to the eight-parameter host at beta=1. The overlay adds five memory coefficients. | Original-source reproduction and the current 13-slot implementation are distinct parameterizations. Current default beta=1.05 is not the original host specialization. A fixed beta supplies information even when it is not fitted. |
| IGS97 preparation and numerics | Sections 5 and 7 distinguish overshoot correction, trial-history handling and a resting-period reset; Appendices A/C address objective transport. | Document preparation, reset events and numerical history policy. Zero-spin scope does not resolve the printed spin-sign conflict or establish finite-rotation transport. |

The shared IGS dossier shows that setting mR=mT=1 does not recover the host for arbitrary unsaturated/misaligned history. Saturated aligned loading provides a particular limiting check, not a complete parent reduction. The paper should compare independently calibrated formulations first. A controlled mechanism study needs a reviewed common-host construction, initialization and limiting map before attributing a difference solely to memory.

The paper annotation previously linked only the failed v1 history investigation. The later v2 record passes 303 cases, including eight refined histories, after an endpoint-defect correction, with unchanged tolerances. Both records are now linked. This addresses the specific retained discrepancy for the pinned solver, rather than establishing current-engine accuracy on the proposed cyclic panel. External-code, experimental and independent scientific validation remain open. Historical pilot configurations and counts are unchanged.

## SANISAND: constitutive source versus numerical policy

The original-2004 dossier now supplies current-void-ratio elasticity, fabric/dilatancy evolution and source equation locators. It records a derived dimensional correction for an apparent missing K in printed Eq. (20); this needs independent review. The original model and the pinned OpenSees implementation also differ in their elasticity density choice and other numerical details.

Two executable research definitions share continuous equations but differ in memory preparation:

| Research identity | Policy | Appropriate evidence use |
| --- | --- | --- |
| Fixed-memory backward Euler | Reversal anchor remains fixed; reversal behaviour is unsupported. | Initial-branch equation/integration diagnostics. Do not rank cyclic physical predictions. |
| Parent-direction-reset backward Euler | An anchor is selected from the committed parent and held through internal trials/cutbacks. | Study sensitivity to this declared project policy and its numerical resolution. It does not implement a demonstrated canonical original event rule. |

The source cone-normal trigger and the parent trial-direction trigger can disagree. Caller path boundaries may change reset decisions. Therefore these definitions are numerical-policy variants, not two independently admitted literature formulations or a constitutive parent–extension pair. Refinement within one policy does not prove policy equivalence. Retain policy selection, event boundaries, mixed-control isolation and rollback alongside parameter sets in any future run record.

The next numerical task should use synthetic paths and fixed parameters to separate policy effects from constitutive/calibration effects. Compare common initial branches, explicit reversal boundaries and step refinement; report histories and completion before any aggregate score. Only after an independently reviewed variant and cyclic-control implementation are admitted should laboratory calibration begin. No original-paper reproduction or new model admission follows from this paper-side reconciliation.
