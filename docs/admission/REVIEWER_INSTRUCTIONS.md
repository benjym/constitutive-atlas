# Constitutive model admission reviewer instructions

Use this file for an independent technical assessment of a bounded model-admission
package. The coordinator supplies a task ID, input packages, decision IDs, owned
output directory and any explicit execution authorization. Review the actual
evidence; the package author's proposed disposition is a hypothesis to test.

Current approval authority is [independent agent checklist v1](../AGENT_REVIEW_POLICY.md). A completed separate-agent checklist is sufficient for model approval; human scientific sign-off and further user approval are not required. This supersedes earlier instructions that kept an agent review outside the admission gate. Preserve exact model/scope binding and resolve blocking findings.

## Role and independence

- Start from a fresh context where practical. State reviewer identity, date, agent
  run identity, prior involvement and the basis and limits of independence.
- An agent can independently challenge another agent's work. Label the result
  **AI technical review**, without inventing human credentials or a scientific
  signature. An accepted checklist permits bounded project admission. Deployment and experimental validation remain separate.
- Assess the exact named formulation and bounded use, not the reputation of its
  model family. Separate source fidelity, executable support, numerical evidence,
  experimental applicability and release qualification.
- Do not resolve a missing source, equation or convention by guessing. Record an
  unresolved decision with the smallest specific evidence needed to settle it.

## Read before reviewing

Read `AGENTS.md`, the claimed row in `IMPLEMENTATION_PLAN.md`, `ROADMAP.md`,
`docs/RESEARCH_CHARTER.md`, `docs/STATUS.md`, the current
`schemas/model-v0.3.schema.json` and `docs/FORMULATION_CONTRACT.md`.
Then read the assigned decision sheets, source receipts, source audits, dossiers,
crosswalks, model definitions, prospective freezes, reports and retained failures.
Follow evidence links beyond summaries. Record the files actually examined and
their SHA-256 values, including this instruction file and the input manifests.

Verify input pins before relying on evidence. Distinguish stale live inputs from
valid historical archives; report mismatches rather than repinning or repairing
them. Preserve the identity and limits of historical v0.2 records when reviewing
a proposed v0.3 crosswalk. A new definition requires new artifact-bound evidence.

## Review questions

For every assigned decision, assess:

1. **Source fidelity:** exact publication/version and equation/page locators;
   source law versus later revision, implementation or Atlas numerical choice;
   ambiguity, transcription errors and explicitly justified corrections. Inspect
   readable originals where available. A prior audit is secondary evidence: state
   when the original was not read. Use the PDF skill for PDF inspection.
2. **Formulation:** equation form, physical time versus path parameter, kinematics,
   frame/objective rate, stress binding/scope, signs, units, tensor and shear maps,
   parameters, state layout and admissible domain. Unsupported profiles stay gaps.
3. **Lifecycle:** initialization and preparation, persistent versus temporary state,
   trial/commit/rollback, ordering and lagging, zero/hold behavior, branches,
   reversal/reset events, singular limits and solver/tangent requirements.
4. **Evidence:** independent equation checks versus shared-backend agreement;
   frozen reference and acceptance policy; actual failures and supersession;
   exact model/build/report bindings; path/control/parameter coverage. Passing
   saved replay establishes replay, not current-build qualification. Verify
   numerical claims by reading reports, not just their pass labels.
5. **Claim:** whether the proposed scope follows from that evidence. Distinguish
   bounded material-point verification from FE qualification, finite rotations,
   experimental prediction and calibrated physical preparation. Name exclusions
   precisely and reject claims that rely on untested generalization.

Challenge the proposed acceptance: seek at least one plausible counterexample or
failure mechanism per model and explain whether evidence covers it. Use small
independent algebraic or isolated Python checks where useful. Do not launch a
broad campaign merely to increase test counts. A requested additional study must
name the uncovered claim and prospectively freeze its reference and gates.

## Execution and ownership

Write only within the coordinator's assigned output directory. Do not modify
input templates, existing reports, model/review records, shared code, schemas,
catalogue manifests, the live board or another worker's files. No stage, commit,
reset, stash, clean, push, deploy, author contact or other external messages.
No compiled artifact or supplied author code execution. Native/Wasm builds and
execution require a separate explicit coordinator handoff; build serially with
one explicit target and `--parallel 1` if authorized. Read-only pure Python,
algebra and saved-data assessors are allowed after inspecting their execution
paths. Record commands, actual outcomes and retained failures.

Do not relax an acceptance gate after seeing a failure. Propose any changed
policy as a distinct prospective study. Keep copyrighted full texts private;
record receipts, hashes and locators instead of copying source PDFs into the repo.

## Deliverables

Create a new review output; never overwrite a historical input template. Include `agent-review.json` using [the current template](../AGENT_REVIEW_TEMPLATE.json): assess all nine checklist items, name hashed artifacts and exact model bytes, and record the actual separate-agent run. An accepted record must pass `python3 -B -m atlas.agent_review RECORD --for-approval`.

- `README.md`: review scope, identity/independence, verdict per model, findings
  ordered by severity, evidence limits, checks and smallest next actions.
- `decisions.json`: one entry per assigned decision with ID, model definition
  hash if applicable, question, judgment (`supported`, `conditional`, `rejected`
  or `unresolved`), rationale, exact evidence paths/locators, conditions, excluded
  claims and follow-up. Conditional means its named conditions remain open;
  unresolved means available evidence cannot decide. Neither means admitted.
- `inputs.json`: SHA-256 bindings for all material actually examined, including
  instruction and input-package identities. Record source-access limitations.
- Check logs or independently derived results, if performed, with reproducible
  commands and output identities. A skipped check must remain a skipped check.

Submit the actual agent checklist decision for coordinator integration; do not modify the model or approval registry directly or declare a release.
Return the task ID, exact files, checks, findings, unresolved issues and smallest
next action to the coordinator. Only the coordinator integrates the review and
marks its delivery task complete. An accepted agent checklist permits bounded model approval under the research charter; no additional human scientific sign-off is needed. Release authorization remains separate.
