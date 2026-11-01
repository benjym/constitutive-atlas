# norsand-1993 — ingestion packet

Delivery tracking: [DELIVERY.md](DELIVERY.md), following [E0–E8](../../MODEL_DELIVERY_CHECKLIST.md). This packet does not complete the full assignment.

Task ID: ING-norsand-1993 / MODEL-norsand-1993  
Owner / date: coordinating parent `/root`, 2026-11-01.  
Scope: original Jefferies1993 complete Nor-Sand formulation; E1 acquisition blocked. Later NorSand elasticity, cyclic rules and general3D closures are excluded from this identity.

## Identity and sources

M. G. Jefferies (1993), *Nor-Sand: a simple critical state model for sand*, Géotechnique43(1),91–103, [DOI10.1680/geot.1993.43.1.91](https://doi.org/10.1680/geot.1993.43.1.91). [Author-upload record](https://www.researchgate.net/publication/245410976_Nor-Sand_a_simle_critical_state_model_for_sand).

Original PDF receipt: **not acquired**; local source path, byte count and source SHA-256 remain null. Access date:2026-11-01. Web reader reports13pages and extracted text, but screenshots for PDF4/5 returned references without inspectable image content. Those references are not visual verification. Direct author-PDF fetch outside sandbox networking returned HTTP403. Initial sandbox DNS failures are retained separately and do not establish publisher availability. See [access attempts](delivery-v1/access-results.json) and [network attempt](delivery-v1/access-network-results.json).

[Local scan](delivery-v1/local-scan.json):34PDF first pages extracted successfully across Downloads, attachments and private-source storage; no matching candidate. This is bounded text screening, not proof that no original exists in archives or image-only pages. Detailed inventory is ignored/private and hash-bound. No copyrighted full text, vendor code or binaries are distributed or executed.

## Existing work and gaps

Reuse the [historical acquisition packet](../../reviews/norsand-1993-source-packet.md), [immutable source audit](../../../catalogue/source-audits/norsand-1993-source-v1.json), [paper partial text audit](../../../paper/study/source_formulations/norsand-1993.json) and [publication binding](../candidate-publication-bindings-v1/norsand-1993-crossref.json). Their equations and provisional ingredient lists are not newly certified. This delivery adds umbrella tracking, current local inventory and retained access outcomes; it preserves those prior bytes.

## Equations and schema crosswalk

Target [schema v0.3](../../../schemas/model-v0.3.schema.json) and [formulation contract](../../FORMULATION_CONTRACT.md). No executable record is created while equations remain unverified. A future record must declare `schema_version: "0.3"`, complete `formulation`, explicit state semantics, inputs and initialization; no legacy top-level `integration`.

| Source verification target | Quantity | Proposed mapping / unresolved requirement |
| --- | --- | --- |
| p92 assumptions (historical text inventory) | Rigid-plastic, drained axisymmetric effective-stress scope | Source images required; do not assert supported small_strain_3d host from triaxial scope. |
| Eqs5a/5b/6/12, pp94–97 | Candidate M, Gamma, lambda_c, N, h | Units/ranges/log base and pressure reference unresolved; no admitted parameter defaults. |
| Eqs7–10, p96; Fig8,p98 | Candidate p,q,e,image pressure and current/image state parameters | Exact dependencies, initialization constraints and history ordering unresolved; no final state count. |
| Eq8,p96 | Candidate fixed3.5 coefficient | Verify image/prose before using it or treating it as fitted. |
| Complete original incl notation p102 | Flow, yield, hardening, domain | Equation transcription withheld pending readable pages91–103. |

All required formulation declarations remain unresolved rather than guessed: time dependence, equation form, kinematics, frame/objective rate, tensor/shear basis, stress/strain signs, and Cauchy stress binding/scope. Historical text suggests rate-independent rigid-plastic axial effective-stress behavior; this is a verification target, not a validated executable profile. Do not invent tensor conventions, an elastic predictor or later3D Lode dependence to fit the current engine.

## Temporal integration and transactions

Original rate/increment interpretation, independent loading parameter, plastic consistency, image-pressure update ordering, unloading/reversal and hold uniqueness require original-equation inspection. Physical time is not an established requirement. A prospective host must explicitly specify complete persistent state, trial/commit/whole-parent rollback, restart, substepping/events and tangent treatment after source/closure resolution. The repository's generic transaction semantics do not establish a unique strain-driven rigid-plastic update. No capability implementation is justified yet.

## Independent checks

No constitutive numerical test is claimed: unverified source equations cannot supply a defensible oracle. Packet integrity checks bind historical inputs, current attempts and private inventory. Separate source-gate reviewer findings are stored under `delivery-v1/independent-review/`; they are not E5 approval. No compiled artifacts, interpreter material runs or builds were executed.

## Handoff

Current blocker NS-SOURCE-01: readable/retainable original PDF or inspectable complete equation pages91–103. Resume E1 on a legal local copy or concrete accessible primary-source route. Then verify Eqs5–12 and all dependent equations; resolve rigid-plastic initialization/strain-driven closure before E2 and freeze source-derived yield-inversion/image/hardening reference gates before numerical observations. Lead remains responsible for E0–E8 after the handoff.

Source completeness: false. Executable support: none for this original identity. Independent constitutive numerical qualification: absent. Agent model approval: absent. Atlas inclusion/browser/live delivery: not performed. Experimental validation: not assessed. Umbrella remains open.
