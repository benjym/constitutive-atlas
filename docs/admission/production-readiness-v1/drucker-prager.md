# Drucker–Prager: admission decision sheet

Current definition: `b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877`; schema `0.1`; status `transcribed`.

Pending canonical review: [drucker-prager-source-v4.json](../../../catalogue/reviews/drucker-prager-source-v4.json). Its exact definition binding was checked, not accepted.

Proposed release: the fixed-frame, small-strain material-point scope in [README.md](README.md). Explicit input state is required by the reviewed consumer contract; legacy low-level default behavior is not claimed to have changed. All decisions below are unsigned proposals.

## DP-01: Accept the uncapped constant-elastic perfect-plastic specialization and documented source parameter/multiplier conversions?

Accept only this selected ideal cone; no equivalence to complete OpenSees/Itasca models with tensile cutoff/hardening.

Read: [README.md](../../../docs/ingestion/drucker-prager/README.md), [drucker-prager-apex.md](../../../docs/models/drucker-prager-apex.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## DP-02: Approve the corrected admissible 0<=Md<=M domain and distinguish the preserved old negative-work witness?

Use the exact current candidate; old source crosswalk/checks pin the pre-guard definition and are historical rather than current-root commands.

Read: [README.md](../../../catalogue/investigations/dp-dilatancy-domain-v1/README.md), [previous-definition.json](../../../catalogue/investigations/dp-dilatancy-domain-v1/previous-definition.json), [candidate-definition.json](../../../catalogue/investigations/dp-dilatancy-domain-v1/candidate-definition.json).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## DP-03: Accept trial-direction elimination and the ideal norm subgradient at the apex?

The q_trial=0 denominator is a safe algebraic branch, not a stress floor. Md=0 beyond the tensile apex remains an expected transactional failure.

Read: [drucker-prager-apex.md](../../../docs/models/drucker-prager-apex.md), [drucker-prager-dilatancy.md](../../../docs/models/drucker-prager-dilatancy.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## DP-04: Do the current 83 native cases and separately retained Wasm/browser checks cover the requested bounded behavior?

Review all outcomes and failure/recovery meanings; independent CLI recovery is not persistent-process recovery; preserve failed v1 and earlier v2.

Read: [drucker-prager-dilatancy-v3.json](../../../catalogue/evidence/drucker-prager-dilatancy-v3.json), [README.md](../../../docs/reviews/dp-dilatancy-web-v1/README.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## DP-05: Accept explicit sigma/e, temporary gamma lifecycle, scaled tolerances and project void bookkeeping?

Gamma is final-subsolve temporary data, not accumulated plastic history. Yield/domain tolerances are numerical choices.

Read: [formulation-crosswalk.json](../../../docs/ingestion/drucker-prager/formulation-crosswalk.json), [drucker-prager-dilatancy.md](../../../docs/models/drucker-prager-dilatancy.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## DP-06: Accept the proposed release exclusions and specify any remaining numerical qualification?

Exclude global convergence, arbitrary parameter/path coverage, smooth tangent through all branches and experimental calibration.

Read: [drucker-prager-source-v4.json](../../../catalogue/reviews/drucker-prager-source-v4.json), [FORMULATION_CONTRACT.md](../../../docs/FORMULATION_CONTRACT.md).

Decision: **unassigned / pending**. Record rationale and exact evidence locators in a separately named review output.

## Supersession that must not be lost

The old ingestion README/crosswalk/check script pins the pre-domain-correction definition. It is historical source reasoning, not a failing current model. The current domain study and pending v4 review supersede the old request to add `Md <= M`. The separate local Wasm/browser packet supersedes the v4 record’s dated statement that those checks had not yet happened. Preserve both old statements and cite the later evidence; do not rewrite their hashes.

## Reproduction and final release

Run the parent packet preflight. Existing source/algebra checks and saved reports are verification inputs, not fresh compiled execution. After independent acceptance, prospectively pin a new release build/check matrix and retain every outcome. A reviewer may request a narrower scope or a specific new study; model status remains unchanged until that process is completed.
