# Experimental initialization recipes

The [v0.3 initialization contract](FORMULATION_CONTRACT.md#initialization-contract)
now distinguishes illustrative values from required persistent state. The generic
`atlas.initialization.initialize_state` entry point checks explicit incremental
or physical-time state without constructing it. Existing physical-time recipes
can target v0.3 after explicit model-hash reconciliation; their output passes
through that same initializer at time zero. Original recipes and pins remain
unchanged. This does not extend the recipe language to incremental models or add
preparation-history execution.

Initialization is separate from constitutive evolution and specimen preparation. The new [recipe schema](../schemas/initialization-recipe.schema.json) describes typed inputs, ordered guarded expressions, named state outputs and an initial strain-rate tensor using the existing restricted expression language. The Python preprocessor checks dimensions, finite results, parameter bounds, model domain and model `initial_checks` before returning fields for the common timed driver. It adds no material-specific solver kernel. Native/Wasm recipe execution and general numerical initialization solves are not implemented.

Every parameter and input is supplied explicitly under the [input schema](../schemas/initialization-input.schema.json). Recipes pin the canonical model hash, and outputs retain recipe/configuration/model/run-field hashes. CLI outputs also hash the exact input-file bytes parsed. Model changes require recipe reconciliation; changing a pin without review does not establish equation equivalence. Initialization runs at time zero. Its output is not proof of admissibility at another start time, a nonlinear solver, a consolidation/reversal history or a calibrated parameter set.

```sh
python -m atlas.cli initialize \
  initialization/terracotta-2024-fig1-total-stress.json \
  initialization/terracotta-2024-kaolin-initialization.json \
  --model-definition models/research/terracotta-2024-fig1.json \
  --output /tmp/terracotta-initial.json
```

The result's `run_fields` contains `model`, flat `parameters`, flat `initial`, and `initial_strain_rate`, ready to merge into an explicit v0.2 timed schedule. It deliberately supplies no strain origin, segment durations or loading controls. Preserve the result/configuration with the schedule; the native driver receives the explicit arrays, not the recipe provenance. The supplied initial rate controls the left-side initial stress; a different first-segment rate can produce an instantaneous algebraic stress jump.

## Terracotta Figure 1 positive stable branch

The [recipe](../initialization/terracotta-2024-fig1-total-stress.json) targets the existing restricted [Figure 1 research model](models/terracotta-2024-transcription.md). Its sources are the [journal paper](https://doi.org/10.1016/j.jmps.2024.105789) and the pinned author equation image linked in the recipe. The inverse expressions are Atlas algebraic rearrangements of the elastic stress equations, with an explicit choice of the positive stable root. They do not resolve the journal/author mixed-control discrepancy or define the Appendix B variant.

Inputs are total pressure `p`, signed total `q`, solid fraction `phi`, mesoscopic temperature `Tm`, volumetric rate `Dv` and signed shear rate `Ds`, in SI units. The recipe subtracts viscous and mesoscopic contributions:

```text
pe = p - 2 alpha Tm Dv/Gamma - Tm^2/Gamma
qe = q - 2 gamma Tm Ds/Gamma
d = 1 - K/(3G) (qe/pe)^2
ev_e = sqrt(pe/(K phi^6) (1 + sqrt(d)))
es_e = qe/(3G phi^6 ev_e)
```

It requires `0<phi<=1`, `Tm>=0`, `pe>0` and `d>=0`, then applies all current model constraints, including transport/stability inequalities and parameter ordering. There is no clipping, pressure floor or discriminant repair. The dimensionless discriminant avoids squaring large pressure values directly, but extreme or near-boundary floating-point inputs can still fail. Equality at the repeated root follows the current draft domain; its physical/source boundary review remains open. The other elastic root is not selected.

Rates reconstruct as `Dxx=Dv/3+Ds`, `Dyy=Dzz=Dv/3-Ds/2`, with zero shear. Changing K/G reinitializes elastic strain to preserve the requested pressure, rather than keeping a default elastic strain with a different pressure. The included kaolin configuration explicitly uses the rounded author-code `pOne=543e6 Pa` preset; it does not silently substitute the journal's rounded `phi1` value. Zero Tm reduces this same recipe to elastic-stress initialization.

## Checks and remaining work

[Tests](../tests/test_initialization.py) independently generate stresses from elastic energy derivatives for compression/extension, several solid fractions and nonzero temperature/rates, then recover the original state. They check changed parameters, repeated-root equality, inadmissible states, dimensions, explicit inputs, model pins, initial-history guards, a second tensor-state Maxwell recipe and CLI provenance/input protection. A small native Terracotta test checks continuous persistent state and exact viscous jumps at a rate switch, followed by `Tm(t)=Tm0/(1+eta Tm0 t)` at zero strain rate. This is relaxation/temperature-decay evidence, not an independent creep benchmark.

The implementation remains experimental Python preprocessing. Browser recipe controls, nonzero initialization time, general prescribed total-stress inversion with unknown rates, alternative roots and a declarative nonlinear solve require separate designs. Terracotta still needs complete journal reconciliation, external source-matched creep/mixed-control references, broader refinement and clay experimental matching. No public model status or executable-model count changes.

The [retained investigation manifest](../catalogue/investigations/initialization-and-pm4-flow-v1/manifest.json) pins inputs/implementation, the default and nonzero-temperature initialization results, the native boundary/decay response and the passing 34-test combined run. The reused research binary catalogue matches the pinned model; no new native build or PM4Sand native execution was performed.

A [separate scalar prepared-creep study](TERRACOTTA_CREEP_REFERENCE.md) now supplements initialization and boundary checks. Its native runs begin from frozen independently prepared states, rather than treating this algebraic recipe as specimen preparation.
