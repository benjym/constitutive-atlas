# Formulation contract v0.3

A model's top-level `formulation` defines what its equations mean and what a
consumer must supply and interpret. It replaces the v0.1 `integration` flag and
extends the v0.2 physical-time declaration. The authoritative structural schema is
[model-v0.3.schema.json](../schemas/model-v0.3.schema.json); `atlas.model.validate`
additionally checks dimensions, symbols, state rules and stress bindings.

This first contract defines three executable profiles. It makes the existing
mathematics explicit; it does not add finite-deformation or objective updates.

```json
{
  "schema_version": "0.3",
  "formulation": {
    "time_dependence": "strain_path",
    "equation_form": "incremental_residual",
    "kinematics": "small_strain_3d",
    "frame": "fixed_spatial",
    "objective_rate": "none",
    "tensor_representation": "mandel",
    "stress_sign": "compression_positive",
    "strain_sign": "compression_positive",
    "inputs": {
      "equation": {
        "de": {
          "quantity": "strain_increment",
          "measure": "infinitesimal_strain",
          "shape": "sym",
          "unit": "1",
          "configuration": "current",
          "sampling": "increment",
          "constraint": "finite"
        }
      },
      "advance": {}
    },
    "stress": {
      "source": "state",
      "name": "sigma",
      "measure": "cauchy",
      "scope": "effective"
    }
  }
}
```

This is the formulation portion of a model, not a complete model definition.
Every contract field shown is required; there are no implicit convention defaults
in v0.3. The top-level `integration` field is forbidden.

## Equation meaning and inputs

| `time_dependence` | `equation_form` | Required loading input | Meaning of each state equation |
| --- | --- | --- | --- |
| `strain_path` | `incremental_residual` | Symmetric strain increment `de` | Residual equal to zero, with the corresponding state's units; current and committed `_n` state are available. |
| `strain_path` | `strain_path_rate` | Symmetric strain increment `de` | Derivative with respect to dimensionless path fraction, with the corresponding state's units; the fraction runs from zero to one over the supplied increment. This is not a derivative per second. |
| `physical_time` | `ode` | Physical stage `time` in seconds and symmetric `strain_rate` in 1/s | Derivative per second of the corresponding persistent state. Previous-state symbols, `de`, `dt`, transient solve variables and incremental resets are unavailable. |

Only these pairings are allowed. There is one equation per state. The legacy
incremental profiles retain their `1`/`Pa` declaration units and stress-first state
layout. Physical-time ODEs retain the v0.2 SI-unit declarations and observables.
Physical-time residuals, DAEs and general discrete-update maps require future
schema profiles; they must not be approximated by relabeling an existing one.

For a strain-path rate, the caller supplies a straight strain path and the
integrator partitions it internally. A residual specifies an incremental relation;
its response under subdivision need not equal a single unsplit solve. The
[existing incremental integration semantics](ARCHITECTURE.md) and
[parent-increment reset scope](PARENT_INCREMENT_RESETS.md) remain in force.
The [physical-time API](TIME_ODE_API.md) specifies stage rates and clock handling.

## Explicit input declarations

`formulation.inputs` is required. Its `equation` object declares externally
supplied expression symbols; its `advance` object declares additional context
needed to advance the material. All listed inputs are required and have no
defaults, even if a particular equation does not reference them. Current state,
committed state and parameters retain their separate model declarations; they
are not duplicated here. The identity tensor `I` is a language constant, not an
external input.

Each input declares physical quantity, scalar/symmetric shape, SI unit, sampling
and value constraint. Mechanical inputs additionally declare their measure and
configuration. `configuration: current` denotes current spatial Cartesian
components under the fixed-frame infinitesimal approximation; it neither adds
finite-deformation kinematics nor converts material/reference-frame inputs.
Tensor ordering and signs inherit the formulation's explicit declarations.
`finite` requires every scalar/component to be finite; `positive_finite` also
requires a strictly positive value. Symmetric inputs always contain six Mandel
components, including for the axisymmetric profile. That profile imposes its
additional equal-radial and zero-shear restrictions.

Incremental profiles declare exactly the `de` descriptor in the example above,
with an empty `advance` object. `sampling: increment` means the supplied increment
for that equation evaluation; internal substepping supplies the corresponding
subincrement. No physical duration, strain-rate history or clock is implied.

Physical-time profiles instead require:

```json
"inputs": {
  "equation": {
    "time": {
      "quantity": "time", "shape": "scalar", "unit": "s",
      "sampling": "stage", "constraint": "finite"
    },
    "strain_rate": {
      "quantity": "strain_rate", "measure": "infinitesimal_strain_rate",
      "shape": "sym", "unit": {"si": [0, 0, -1, 0]},
      "configuration": "current", "sampling": "stage", "constraint": "finite"
    }
  },
  "advance": {
    "start_time": {
      "quantity": "time", "shape": "scalar", "unit": "s",
      "sampling": "start", "constraint": "finite"
    },
    "duration": {
      "quantity": "duration", "shape": "scalar", "unit": "s",
      "sampling": "interval", "constraint": "positive_finite"
    }
  }
}
```

`time` and `strain_rate` are evaluated at matching integration stages; they are
the only externally supplied equation symbols. `start_time` and `duration` are
update-call arguments, not expression symbols, and cannot be redeclared as
parameters/state/derived values. Evaluation alone needs no advancement interval.
Advancement requires a finite, representably later endpoint
`start_time + duration`. The integrator supplies stage times; a constant prescribed
rate or a time-history callback supplies stage rates according to the existing
API. This declaration does not serialize a loading history or authorize a model
to execute an arbitrary callback. Control discontinuities still require separate
advances.

Declarations must match the profile exactly: inputs cannot be omitted, renamed,
made optional or assigned another measure, unit or sampling rule. Temperature,
pore pressure, deformation gradients and other external fields need a future
profile with defined evaluator/host semantics. Declaring such fields alone must
not make an unsupported model appear executable. The validator and compiler
derive their expression input types from these declarations.

## Kinematics, frame and representation

`small_strain_3d` means infinitesimal symmetric strain in three dimensions.
`axisymmetric_x` is additionally available for physical-time ODEs: x is axial,
yy and zz loading components are equal, and all shear loading components vanish.
It retains the current stage-level roundoff tolerance and stress-output symmetry
checks; it is a restriction on supported loading, not a tensor storage format.

`fixed_spatial` and `objective_rate: none` specify fixed Cartesian components with
zero spin. No automatic rotation, objective stress rate or finite-deformation
transport is supplied. Fixed-frame rotational covariance does not establish
finite-rotation objectivity. An MPM host cannot infer permission to rotate stress
and arbitrary history tensors from this contract.

All symmetric tensors use Mandel order
`[xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz]`. Stress and strain are
compression-positive. Values use SI units. These conventions apply to equation
inputs and outputs. State-specific meanings and basis-transformation rules are
declared separately below; finite-step transport remains unsupported.

## State semantics and lifecycle

Each v0.3 state field requires `semantics`, alongside its existing name, shape,
unit, illustrative initial value and numerical scale. For example:

```json
{
  "name": "sigma", "shape": "sym", "unit": "Pa",
  "initial": [100000, 100000, 100000, 0, 0, 0], "scale": "p_ref",
  "semantics": {
    "role": "persistent",
    "quantity": "cauchy_stress",
    "transformation": "symmetric_spatial_tensor"
  }
}
```

`role` replaces the legacy `transient`/`multiplier` booleans, which are forbidden
in v0.3:

| Role | Storage and equation meaning |
| --- | --- |
| `persistent` | Committed material history. Preserve across successful updates and restart. Incremental expressions may read its committed `_n` value. |
| `increment_unknown` | Temporary residual solve variable, reset to zero at each internal residual solve. It is not accumulated physical history and has no `_n` expression symbol. |
| `plastic_multiplier` | Dimensionless scalar temporary solve variable with the existing zero-plastic-increment elastic predictor before complementarity correction. It has no `_n` expression symbol. |

Both temporary roles require zero illustrative initial values and an incremental
residual profile. Rate/ODE profiles require persistent state throughout. Every
field still occupies the full engine state layout and has one equation;
temporary values may appear in diagnostics or update output, but do not become
physical history. The initializer fills their layout slots with zero. The engine
retains its existing reset policy for subsequent solves.

An accepted update commits its persistent result. A failed update returns the
complete incoming layout, including any temporary slots, without committing
partial internal work or reset effects. Repeated trials must start from the same
committed parent. These lifecycle meanings do not add event location or change
the existing parent-increment reset scope.

`quantity` records the source-supported physical meaning. Apart from the enforced
stress binding `cauchy_stress`, these are descriptive identifiers, not a universal
ontology or automatic unit/physics inference. `unspecified` explicitly records
unresolved meaning. Migration uses it for history fields rather than guessing
from names such as `h`, `alpha` or even scalar component names.

`transformation` declares behavior under a passive orthonormal change of spatial
basis, separate from time evolution:

| Transformation | Meaning |
| --- | --- |
| `scalar_invariant` | A genuine scalar unchanged by basis rotation; requires scalar shape. |
| `symmetric_spatial_tensor` | A symmetric tensor in current spatial coordinates: if Q maps old components to new components, A' = Q A Q^T. Requires symmetric shape; Mandel encoding is applied after the tensor transformation. |
| `fixed_components` | Components are only specified in the declared fixed frame. No re-expression/rotation rule is asserted, including for scalars that may encode directional components. |

The stress state `sigma` must declare persistent Cauchy-stress spatial-tensor
semantics. Other migrated fields use `fixed_components` until source evidence
supports a more specific rule. Consumers needing frame changes must reject
unresolved transformations or obtain a reviewed mapping. Declaring a spatial
tensor does not specify an objective rate or authorize a corotational finite-step
update. The current runtime does not automatically transform history tensors.

## Initialization contract

Every v0.3 model requires a top-level `initialization` declaration. For the
linear-elastic example:

```json
"initialization": {
  "method": "explicit_state",
  "default_policy": "examples_only",
  "required_state": ["sigma", "e"],
  "validation": "domain_and_initial_checks"
}
```

`required_state` must list all and only persistent fields in declared layout
order. Initial values must be supplied explicitly; the field-level `initial`
literals are illustrative examples, not a physical default or a preparation
prescription. Temporary slots are excluded from this list and initialized to
zero. This version supports explicit state only. Algebraic construction can be
performed by a separate reviewed recipe; numerical inversion, projection,
consolidation and other preparation procedures are not implied.

The Python entry point `atlas.initialization.initialize_state` requires complete
named persistent state and complete resolved parameters. It checks shapes,
finiteness, parameter bounds, positive numerical scales at those parameters,
model `domain` and `initial_checks`. Physical-time models also require explicit
initial time and strain rate, and all their initial observables must evaluate
finitely. Axisymmetric restrictions apply at initialization too. Incremental
initialization uses zero strain increment with the supplied state as its own
committed parent and has no physical clock.

The result contains named full state, a flat `initial` array in engine layout,
resolved parameters, time/loading context, initial observables and model-hash
provenance. Inputs are not mutated. No example substitution, projection or
clipping is performed. Passing the declared checks establishes only their
conditions: it does not prove specimen preparation, initial equilibrium or all
physical consistency conditions absent from the definition.

```python
from atlas.model import load, migrate_formulation
from atlas.initialization import initialize_state

model = migrate_formulation(load("models/linear-elastic.json"))
prepared = initialize_state(
    model,
    {"sigma": [100000, 100000, 100000, 0, 0, 0], "e": 0.7},
    {"p_ref": 100000, "E": 30000000, "nu": 0.25},
)
# prepared["initial"] is the complete array for a material update.
```

Newly compiled v0.3 models also reject omitted/empty state arrays in the native
CLI/C ABI instead of silently substituting examples. These low-level entry points
still take the full layout, including temporary slots; they do not execute a
preparation recipe. `atlas::initial_state` remains an explicit example-value
getter, not a consistency-checked initializer. Legacy v0.1/v0.2 default behavior
is unchanged.

## Stress output

`stress` is an output binding, not another equation or an inferred name match:

- Incremental profiles bind effective Cauchy stress to persistent symmetric Pa
  state `sigma`, occupying the first six state components.
- Physical-time profiles bind symmetric Pa observable `stress`, using
  `source: "observable"`, `name: "stress"`, `measure: "cauchy"`, and an explicit
  `scope` of `effective` or `total`.
- A physical-time system with no stress output declares `{"source": "none"}`.
  It must not also declare the reserved `stress` observable. Such a system can be
  integrated, but does not provide the stress output required by a mechanical host.

These bindings deliberately match the current engine layouts. Arbitrarily named
stress outputs and other stress measures require future implementation support.
An effective-stress declaration supplies no pore-pressure evolution or total-stress
conversion. Total stress does not imply that a coupled poromechanics system exists.
A physical-time stress observable may depend on the prescribed rate, so a state
snapshot alone need not determine stress.

## Numerical execution and consumer responsibilities

The contract describes equation meaning, not a choice of Newton tolerances,
substep budgets or tangent implementation. Those remain execution settings.
Current updates preserve transactional commit/rollback behavior. Transient
multipliers in incremental residuals retain their predictor/reset semantics.

A consumer must validate the complete document and check its own support for the
profile, stress scope and output availability before use. Schema validity is
neither a claim of scientific verification nor a promise that every consumer can
execute it. In particular, this version supplies no generic acoustic wave-speed
bound, energy output, finite-rotation adapter or physical-time update tangent.
Those capabilities must not be inferred from a Cauchy stress output.

## Compatibility and migration

Existing v0.1/v0.2 documents remain accepted with their existing semantics and
bytes. Hash-pinned models and evidence are not rewritten. A v0.3 document receives
its own model/catalogue hash, even where executable equations are identical.

Use `atlas.model.migrate_formulation(model, stress_scope=...)` to obtain a validated
copy, or write a new file with:

```sh
python3 -m atlas.cli migrate-model models/linear-elastic.json --output /private/tmp/linear-elastic-v0.3.json
python3 -m atlas.cli migrate-model models/research/terracotta-2024-fig1.json --stress-scope total --output /private/tmp/terracotta-v0.3.json
```

The command refuses to overwrite an existing file. v0.1 conventions already define
effective stress. For a v0.2 stress observable, migration requires an explicit
source-supported scope; it never guesses effective versus total. Omitted v0.2
kinematics become the documented `small_strain_3d` default. Migration does not
promote review status or change equations, state layout, parameters or illustrative
state values. v0.3 intentionally requires explicit initial state at execution.
Migration writes the complete required input declarations, including explicit
advancement context for physical-time profiles. v0.3 remains an integration
draft; new v0.3 records must include `inputs`, state `semantics` and
`initialization` rather than rely on earlier draft defaults. Migration preserves
equations and numerical reset behavior while replacing the legacy role flags.
Legacy definitions that use temporary variables as `_n` history, nonzero
temporary example values or temporary rate state fail migration and require
source reconciliation; they are not silently rewritten to fit the contract.

The native compiler supports all three v0.3 profiles. Python callers should use
`physical_time(model)` and `integration_kind(model)` rather than dispatching on
schema version or assuming `integration` exists. Separately versioned transports,
including the experimental v0.1-only history bridge, retain their acceptance
boundaries; native update support does not imply acceptance by those transports.

## State-contract verification

`tests.test_state_contract` checks role/shape consistency, unavailable temporary
history symbols, explicit initialization, rejection without projection, actual
time/rate context and existing recipe reconciliation. `tests.test_formulation`
compares generated material-update code against preserved definitions, excluding
catalogue metadata and the new explicit-initialization policy helper.

A small mixed-version native catalogue can be checked separately:

```sh
python3 tools/prepare_state_contract_check.py /private/tmp/atlas-state-contract-check
cmake -S /private/tmp/atlas-state-contract-check -B /private/tmp/atlas-state-contract-check/build -DCMAKE_BUILD_TYPE=Debug
cmake --build /private/tmp/atlas-state-contract-check/build --target atlas_state_contract --parallel 1
ATLAS_STATE_CONTRACT_SOLVER=/private/tmp/atlas-state-contract-check/build/atlas_state_contract python3 -m unittest tests.test_state_contract.NativeStateContractTests -q
```

The native cases check rejection of missing v0.3 state, legacy default
compatibility, exact old/new elasticity/plasticity update agreement, timed update
agreement and rollback. This does not establish scientific admission or Wasm
parity.
