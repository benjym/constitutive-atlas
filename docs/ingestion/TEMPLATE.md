# <model-id> — ingestion packet

Delivery tracking: for a full model assignment, also create `DELIVERY.md` from `docs/ingestion/DELIVERY_TEMPLATE.md` and follow `docs/MODEL_DELIVERY_CHECKLIST.md` (repository-root paths). This packet closes the source phase only.

Task ID: ING-<model-id>
Owner / date:
Scope / remaining work:

## Identity and sources

Exact formulation/version, bibliographic links, private source receipts and SHA-256, page/equation/table locators, access/redistribution limits. Separate confirmed facts from unavailable source details.

## Existing work and gaps

Link prior dossiers, schema definitions, reviews and evidence. Explain what this packet adds.

## Equations and schema crosswalk

Target: [schema v0.3](../../schemas/model-v0.3.schema.json); read the [formulation contract](../FORMULATION_CONTRACT.md). New records use `schema_version: "0.3"` with an explicit `formulation`, without top-level `integration`. Existing-record migration is separately owned.

Record source-backed values or explicit gaps for time dependence, equation form, kinematics, frame, objective rate, tensor representation, stress/strain signs and stress output binding/scope. Cite source locators for these decisions. Identify unsupported profiles without inventing defaults.


| Source locator | Equation / quantity | Schema representation / units | Status / ambiguity |
| --- | --- | --- | --- |
| | | | |

List parameters, states, tensor/sign conventions, inputs, domains, initialization and preparation.

## Temporal integration and transactions

Law type; time or strain-path variable; rate/history inputs; zero-load/hold behavior; trial/commit/rollback; old/new ordering and events; tangent/solver needs; unsupported cases. Use “unspecified in inspected source” where appropriate.

## Public profile draft

Follow [the public-profile contract](../PUBLIC_MODEL_PROFILES.md). Write a reader-facing title/summary, explanation of characteristic behaviours, material-parameter meanings/units, starting-state guidance, meaningful scope/limits and readable references. Include local source locators and a proposed supported experiment when justified. For a source-only assignment, keep the draft here or in a packet-local file and hand it to the coordinator for `web/model-profile-data.mjs`; do not edit shared web files. Literature-only entries get a bounded conceptual explanation without invented controls, defaults or equations. Keep curation status and check receipts out of the public prose.

## Independent checks

Derivation or reference provenance, exact commands, results and limitations. Record failures. Do not claim compiled checks that were not run.

## Handoff

Exact owned files; blockers and next actions; proposed shared capabilities; proposed next bounded study. For full delivery, identify the next E0–E8 phase/owner in `DELIVERY.md`; do not stop the umbrella task here. Separately state source completeness, executable support, numerical verification and scientific admission. The coordinator records review/integration on the live board.
