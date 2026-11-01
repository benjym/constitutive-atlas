# Model approval by independent agent review

Effective 1 November 2026, at the user's instruction, **an independent agent review is sufficient for project model approval. Human scientific review, signatures, credentials and further user sign-off are not required.** This replaces the human-signature prerequisite in earlier plans and packets. Actual source and numerical checks remain required. It does not turn numerical test execution into an independent review.

## Approval pathway

1. The implementation agent prepares the exact model, source dossier and numerical evidence. Freeze model bytes, source receipts, acceptance bounds, supported scope and known failures.
2. A **separate agent run**, preferably with fresh context, reads the original sources and the model/evidence, performs the checklist below, and records findings. It must not be the run that authored the transcription. Record the actual agent/run identity and independence basis; never invent a review. The reviewer may challenge the implementation or reference instead of endorsing either.
3. Resolve blocking findings and obtain the reviewing agent's accepted decision for the exact revised bytes. A coordinator may correct clerical errors, but cannot manufacture the reviewer's technical decision. Low concerns and excluded applications may remain explicit limitations; in-scope uncertainty that prevents a checklist pass blocks approval.
4. Save a new record under `catalogue/agent-reviews/` using [the template](AGENT_REVIEW_TEMPLATE.json) and [schema](../schemas/agent-review.schema.json). Attach hashed reports/receipts to every checklist item, with optional `#` locators. Public source receipts may identify privately retained originals; do not redistribute copyrighted sources.
5. Validate and generate the approval entry:

   ```sh
   python3 -B -m atlas.agent_review catalogue/agent-reviews/MODEL-agent-v1.json --for-approval
   python3 -B -m atlas.agent_review catalogue/agent-reviews/MODEL-agent-v1.json --approval-output /tmp/MODEL-approval.json
   ```

   The coordinator adds the generated entry to `catalogue/approved-models.json` after checking exact scope and integrity. This is integration, **not a human scientific approval gate**. Model metadata changes require a newly bound review/approval rather than silently changing approved bytes.

## Checklist v1

| ID | Reviewer must assess |
| --- | --- |
| `source_provenance` | Exact publication/variant, persistent source links, readable original equations and source hashes; distinguish later variants and author implementations. |
| `equation_fidelity` | Every implemented equation, branch, parameter and evolution law against source locators; label corrections, regularizations and numerical choices. |
| `conventions_dimensions` | Units, signs, tensor/shear conventions, stress measure/scope, kinematics, frame and objective-rate assumptions. |
| `initialization_domain` | Complete parameter/state inventory, admissible ranges, specimen/preparation assumptions, initial values and domain/branch boundaries. |
| `integration_transactions` | Rate versus incremental law, physical time versus path fraction, discretization, hold/reversal/events, trial/commit/rollback, restart and failure behavior for the claimed interface. |
| `independent_numerical_evidence` | Source-derived algebraic/analytical or separately constructed references, refinement and derivative/covariance checks where relevant; retained failures and reasonable predeclared tolerances. Backend agreement alone is insufficient. |
| `backend_delivery` | Native/Wasm and exposed-interface qualification for the proposed approval scope; unsupported interfaces are excluded explicitly. Only this item may be `not-applicable`, with a reason and evidence, when no compiled interface is claimed. |
| `applicability_claims` | Model assumptions, supported protocols/parameter region, limitations and failure disclosures. Experimental validation is assessed separately; its absence is not a blanket approval blocker. No unsupported experimental, FE, finite-rotation or general parameter claim. |
| `reproducibility_rights` | Exact model/source/tool/evidence bindings, reproduction instructions and source/data reuse and retention. No private copyrighted assets in public distribution without permission. |

Each item requires a reason and hashed evidence. Acceptance requires all nine entries exactly once, all core entries passing, no unresolved blocking findings, and current model hash/ID agreement. The schema and checker establish integrity and completeness of the record; they cannot authenticate an agent or substitute for its scientific assessment.

## Status and historical evidence

An accepted checklist enables `approved` in the approval registry (or `reviewed` when reporting review status), only within its declared scope. A green build alone does not approve a model. Keep executable capability, approval, deployment and experimental validation distinct. No additional human scientific sign-off is required to count agent-reviewed formulations toward roadmap review gates.

Existing explicit user approvals remain valid for their recorded scope. Existing v0.1 source-review records and all prior reports, including pending records and statements about absent human signatures, remain immutable historical evidence. They are not prerequisites under this policy. Do not retrospectively mark them accepted or automatically approve other models. A technical review already performed by a separate agent can be reconciled into a **new** checklist record after checking every item and exact revision; missing review work must actually be done.

Publication, external messaging, deployment permissions and experimental-data rights are unchanged. This policy changes model approval authority, not those separate actions.
