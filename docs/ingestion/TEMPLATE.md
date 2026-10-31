# <model-id> — ingestion packet

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

## Independent checks

Derivation or reference provenance, exact commands, results and limitations. Record failures. Do not claim compiled checks that were not run.

## Handoff

Exact owned files; blockers and next actions; proposed shared capabilities; proposed next bounded study. Separately state source completeness, executable support, numerical verification and scientific admission. The coordinator records review/integration on the live board.
