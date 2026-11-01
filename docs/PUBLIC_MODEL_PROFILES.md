# Public model profiles

Every catalogue entry needs a public profile that helps a reader understand the model, explore its behaviour and identify the inputs needed to use it. Write for researchers comparing models and readers learning constitutive behaviour. Lead with the material and its response. Keep curation history and detailed checks in the closed technical section.

Profiles are required for runnable formulations, model families and literature-only entries. A reading profile explains the concept and links to related formulations; it does not promise an executable implementation. A runnable profile describes only controls and examples available through its actual laboratory route.

## Content contract

Author the entry in [model-profile-data.mjs](../web/model-profile-data.mjs), keyed by the stable catalogue ID. [model-profiles.mjs](../web/model-profiles.mjs) renders the profile. Keep explanatory prose separate from executable model JSON and immutable source/review records.

| Field | Required content |
| --- | --- |
| `title` | Readable model name and enough author/year or variant information to distinguish it. Keep implementation IDs and curation labels out of the heading. |
| `summary` | One sentence explaining the material behaviour or central idea. Also used on catalogue cards and in the laboratory. |
| `introduction` | Explain the mechanism and why the model is useful to understand, without claiming suitability for every material in its class. |
| `behaviours` | At least two short title/explanation pairs covering the characteristic response. Define unfamiliar terms where they arise. |
| `explorationTitle`, `exploration`, `comparison` | For a runnable model, explain a useful supported experiment, what to change and what to look at. `comparison` is optional. Name the real controls or preset; supply a complete initial context or point to its registered example. Omit executable instructions for a reading-only entry. |
| `parameters` | An array of guides with exact definition `name`, readable `symbol`, `meaning`, `help` and physical `unit`. Explain the material parameters needed to interpret the example. Put numerical scales and safeguards in technical details. Use an empty array when a source-backed parameter guide is unavailable. |
| `parameterNote` | Explain the calibration and unit conventions relevant to the listed parameters. Values are read from the packaged definition when available; do not duplicate default values in editorial data. |
| `stateLabels` | Optional mapping of exact persistent-state names to readable input labels. Explain tensors and memory in the starting-state prose. |
| `preparation` | Required initial stress, density, internal memory and preparation assumptions. Distinguish a software example from a prepared specimen. |
| `scope` | The exact formulation, stress interpretation, time/path coordinate and supported kinematic or dimensional restrictions, in readable language. |
| `limits` | Missing physical mechanisms and implementation restrictions that affect interpretation or use. Distinguish the implemented variant from its broader family. |
| `equations`, `equationIntro`, `equationNote` | Optional core-equation pairs and definitions, shown in a closed disclosure. Use only source-supported equations; leave full discrete algorithms in technical details. |
| `references` | At least one readable citation with `label` and an HTTPS `url`, preferably an original publication or author/institutional explanation. |
| `related` | Optional catalogue IDs linking families, exact variants and useful comparisons. Explain important differences in the text. |
| `contentSources` | Local definition, dossier, packet or control-source paths supporting the explanation. These are authoring provenance and are not displayed to readers. A catalogue record supports bibliographic scope, not missing equations. |

## Writing and scope

Use concrete descriptions such as “stiffness increases with pressure” or “the model stores recent loading direction.” Explain the effect of a parameter rather than repeating its symbol. Describe a plot feature the reader can inspect. Keep limitations beside the behaviour they qualify, and avoid repeating generic validation disclaimers throughout the profile.

Model availability comes from the actual application routes. Profiles do not contain an approval badge or manufacture an executable status. Accepted equations, numerical checks and review receipts remain accessible under **Technical details, implementation and checks**. Experimental comparisons belong to the named material, parameter set and protocol; a plotted demonstration does not establish a calibration.

For family entries, link to the exact runnable formulation and explain the distinction. For literature-only entries, provide a useful conceptual profile bounded by the inspected source. Do not fill missing parameters, initialization rules or equations from a related model. Use the scope to state that a public laboratory run is unavailable, without exposing the internal task ledger.

Preserve existing model definitions, receipt hashes and scientific decisions when editing public explanations. A change to prose alone does not revise the constitutive law. If a profile reveals a scientific discrepancy, resolve it through the normal model/source process rather than silently changing the implementation.

## Delivery checks

Run from the repository root:

```sh
node tools/check_model_profiles.mjs
node --test tests/test_model_profiles.mjs tests/test_description_context.mjs tests/test_catalogue_browser.mjs tests/test_laboratory_deeplinks.mjs
```

The standard web builder runs the profile-coverage check before packaging. It rejects missing profiles, incomplete content, invalid parameter/state names, broken related-model identities and missing local content sources. These structural checks do not replace reading the scientific explanation against its source.

Follow [E6–E8 in the model-delivery checklist](MODEL_DELIVERY_CHECKLIST.md): integrate the profile, inspect the actual packaged card/dialog/laboratory link, confirm parameter units and current example instructions, then verify the same profile assets and links in the authorized live release. Check long names and tables on a narrow screen. Review/evidence records should remain closed on first opening. A source-only specialist supplies a draft and provenance in its assigned packet; the integration owner installs it in the shared web data.
