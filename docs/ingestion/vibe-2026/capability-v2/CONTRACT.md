# Controlled physical-time contract proposal v2

CAP-vibe2026-controlled-time-design-v2, `/root/vibe_capability`, 2026-11-03. **Design only.** No schema/runtime/model changes, generation, builds or material calls were performed. Existing `path_ode`, physical-time `ode`, schemas and historical qualification retain their identities and semantics. This proposal needs separate review before implementation.

## Chosen boundary

Add a fifth v0.3 profile: `time_dependence: physical_time`, `equation_form: controlled_ode`. State equations are explicit derivatives **per second**, with persistent state only, SI dimensions, fixed-spatial small-strain Mandel conventions. Stress is a symmetric Pa observable, scoped effective, total or **net**. No stress output remains possible. It is not a dimensionless coordinate model, DAE, projection/update map, stress-control solver, transport PDE or generalized tangent.

Use a **new separate generated catalogue/runtime/API** with a distinct `controlled-time-ode-v1` identity. The existing scalar/vector stage sampler, explicit midpoint/step-doubling algorithm and transactional buffer discipline in `atlas.path`, `atlas.path_compiler`, `path_runtime.hpp` and `web/path-engine.mjs` are implementation references. Reuse pure internal helpers only if unchanged old generated outputs and tests prove compatibility. Initially copying a small generic algorithm into a new module is safer than reinterpreting old runtime types or silently changing path binding dimensions.

Keep mechanics explicit: one control `strain` is a **symmetric** accumulated infinitesimal strain tensor; equation `strain_rate` is its first derivative. Scalar fields such as temperature/suction have separate scalar controls. The flat ABI has eight control components for VIBE, but the schema, generated metadata, initialization, browser and restart retain strain as a six-component Mandel tensor rather than six anonymous scalar temperatures/strains. No engineering shear is accepted at this boundary.

## Input declaration

Required equation input `time` is scalar seconds, stage-sampled finite physical time. Required `strain_rate` descriptor retains existing quantity/measure/shape/unit/configuration and adds `binding:{control:strain,derivative_order:1}`. A required `formulation.controls` map declares control meaning, shape and **base value unit**:

```
strain:      quantity=strain, measure=infinitesimal_strain,
             shape=sym, unit=1, configuration=current, constraint=finite
temperature: quantity=temperature, shape=scalar, unit=K, constraint=positive_finite
suction:     quantity=suction, shape=scalar, unit=Pa, constraint=nonnegative_finite
```

Additional equation inputs explicitly bind control names and derivative order0 or1; their declared units are the **actual expression dimensions**. Thus `temperature` has K and `temperature_rate` K/s; `suction` has Pa and `suction_rate` Pa/s. Optional `strain` value input may bind the same symmetric control with order0. Each `(control,order)` pair appears at most once. Shape must match its control; derivative dimensions must equal base dimensions minus one time exponent for order1. Control names and equation symbols are separate namespaces with identifier/collision checks. Required `strain_rate` binds the unique mechanical symmetric control. For this initial subset all other controls are scalar; do not accidentally allow several unlabelled mechanical tensors. Every declared control is required even if no equation uses its value. Descriptor quantities/measure/configuration must match the bound control; derivative quantities distinguish temperature_rate/suction_rate/strain_rate or use a reviewed generic external_field_rate enum, never claim a rate has the value's quantity.

At most32 scalar **control components** and at most64 bound value/rate components plus time; state remains32 scalar components. Limit parameters/observables by existing validated limits. These limits require explicit generator/runtime capacity checks and max-boundary tests rather than inference from channel count.

Advance inputs are exactly `start_time` seconds and `duration` positive finite seconds. No `progress`, `coordinate`, `path_coordinate`, `de`, `dt` or previous-state symbol. Source equation units are state units divided by seconds, not state units. The usual initialization contract lists all and only actual persistent fields.

## Sampling, initialization and restart

A committed context contains exact named persistent state, physical time, complete parameters, complete control **values** and complete endpoint control **rates**, model/catalogue identities and profile version. The initial initializer requires those values/rates explicitly; it validates all shapes, bounds, dimensional contract, domain, initial checks and finite observables. No example substitution, projection, preparation inference or hidden zero-rate assumption.

For an advance provide complete `controls_start` and `controls_end`; start values must equal the committed values exactly after finite numeric decoding. A positive finite duration must produce a representably later finite endpoint. During the interval, all controls interpolate linearly, with derivatives `(end-start)/duration`; the mechanical tensor derivative is assembled in Mandel order. At exact endpoints return the exact supplied endpoint values. Every stage evaluates time, values and rates at the matching physical instant. Validate control value constraints at start/end and stages, not just finite payloads. Rate positivity is **not** inherited from positive value constraints.

A change from the incoming context rate to the new linear ramp is an explicit rate transition at fixed state/time/control values. The run record includes left incoming observation and right new-rate observation separately; no persistent jump is inferred. The right stage context is checked before integration. Initial checks apply to explicit initialization; evolving trial points require domain checks, not re-preparation requirements. End committed rates are the interval's exact prescribed rates, permitting full restart. Discontinuous **values** require caller reinitialization with explicit state and provenance; no implicit hydraulic/thermal jump. Zero-duration advances reject; instantaneous evaluation has its own API and must not masquerade as a time update. A positive-duration hold with unchanged values is legal and can evolve viscous stress.

On any failure no caller state, time, controls, rates, parameters, input arrays or output buffers change. Browser multi-sample schedules are all-or-nothing transactions: earlier trial samples stay local and are discarded on later failure. An incoming left observation is not a new committed step.

## Numerical execution

Prospectively use explicit midpoint, one full versus two half steps, Richardson factor3, accept the two-half state without extrapolation; error weights `atol*state_scale + rtol*max(abs(parent),abs(candidate))`. Full state drives local error; observables still require independent refinement checks. All initial/trial/end states and scalar controls satisfy declared domain/finiteness. Settings explicitly name seconds for minimum/maximum step, positive absolute/relative fractions, bounded integer depth/trial budget. No silent stiffness method switch or after-failure gate relaxation. Expose diagnostics including attempted/rejected/accepted subdivisions; budget rejection rolls back complete parent even if a first half succeeded.

This method can prove a generic transport capability without proving suitability for every VIBE stiffness/branch regime. Full model qualification freezes its own conditions/tolerances/reference corpus separately before any compiled VIBE observation.

## Checked native/Wasm ABI

New symbols only, in a separate generated module:

```
controlled_time_size(model, field)
controlled_time_evaluate(model, state/ns, parameters/np,
                         time, control_values/nc, control_rates/nc,
                         initial_flag, rates_out/ns, observed_out/no, scales_out/ns)
controlled_time_advance(model, state/ns, parameters/np,
                        start_time, duration,
                        current_values/nc, current_rates/nc,
                        controls_start/nc, controls_end/nc,
                        settings/nsettings,
                        state_out/ns, time_out,
                        controls_out/nc, rates_out/nc, observed_out/no,
                        diagnostics_out/nd)
```

`/n` above means explicit pointer plus length, not literal C syntax. `size` returns exact state, parameter, control-component, observable-component, setting and diagnostic counts; unknown model/field returns-1. All pointer/length/flag/integer settings checks occur before reads. Exact scalar/tensor layout comes from generated metadata, ordered controls with offset/size/unit/quantity, state and observable descriptors and equation-input bindings. Every successful output is committed only after all checks; invalid request leaves sentinels unchanged. Input/output overlap must reject or be explicitly made safe via complete input copies before output writes; select and test a single documented policy. Reserve catches for exceptions crossing C boundaries.

Wasm exports these symbols plus malloc/free and HEAPF64. Use same generated evaluator/runtime and ABI for native ctypes and Wasm; backend agreement supplements independent analytical references. New package identity binds exact catalogue/model/source/review/approval/module/Wasm/UI bytes. Old `atlas_integrate_time`, `atlas_run_schedule`, `path_advance` and ordinary material-update/history symbols retain exact signatures and catalogues.

## Dispatch and stress compatibility

`physical_time(model)` may remain true for both physical profiles, but **must not be sufficient** to select old time/schedule execution. Add an explicit `controlled_time(model)` predicate and controlled-profile rejection in old interpreter, observe, initialization, recipes, schedule, legacy history/recorded and compiler routes where they would otherwise accept a physical model. `integration_kind` returns distinct `controlled_ode`; common generation partitions the profile explicitly, rejecting mixed catalogues before output. Dedicated Python `atlas.controlled_time.initialize/evaluate/advance` owns the new context. Do not send this profile into old `evaluation_environment` with just strain rate/time.

Add net only to the **new profile's schema stress enum initially**, and to detached stress identity validation. Existing profiles remain effective/total; old enum/consumer limitations stay explicit. New generated metadata represents net without routing it through old material-update enum. Under Atlas compression-positive convention `net = total - ua*I` when air pressure is positive compressive pressure; source sign mapping must be documented. There is **no inferred conversion**: no external air pressure means no total output, and no Bishop/saturation rule means no effective output. Mechanical controls and all plot/export labels say net stress. Ordinary effective/total lab and experimental-overlay routes reject unsupported net or controlled-time models. No generic effective-stress experiment overlay is inherited.

## Browser/main atlas delivery

Add generic controlled-time engine/worker/contract/laboratory modules and a distinct routing key `controlled_time_laboratory:'index.html'`; main laboratory owns the panel. It displays seconds, complete symmetric initial net stress, true internal e/scan, accumulated strain6, initial/end temperature and suction, source-consistent parameters, explicit durations/segments/settings and full state/observables. All input components remain editable. State preparation is source-backed; aggregate em/eM/SrM/Sr/re are readable algebraic outputs and are not fake persistent inputs. Rate/field discontinuities, reset, transactional failures and fresh replay are explicit. Browser units may display kPa/°C only with checked conversion to Pa/K; replay records SI values and conversion provenance.

Catalogue Explore and direct main-lab links reach this panel; unrelated existing panels/routes remain available. A reader-facing VIBE public profile explains micro/macrostructural response, physical holds, parameters and meaningful limits, with curation/check details in technical disclosure. No standalone model page. Package builder consumes approved exact model/review/source lineage and runs the frozen package corpus on the actual delivered Wasm. All source-only VIBE entries remain literature-only until full scientific/website qualification.

## Source-derived minimal witness and unresolved model choice

Source agent's final-paper handoff: Table3p5 and Appendixp15 distinguish eight persistent components (net stress6,e,a_scan), with other double-structure quantities reconstructed algebraically. Positive physical suction `s=ua-uw` Pa, T K, reference pressure1000Pa and `Dr=0.5e-6 /s`. In Atlas compression-positive representation `e_dot=-(1+e)*trace(strain_rate)`. Scanning evolves with suction rate (source agent gives `(se/sen)*(1-r)/(s*(1-ae))*s_dot`, with r direction-dependent); initial a_scan0wet/1dry. Positive-duration zero-loading holds must retain a nonzero physical viscous mechanism. These facts justify external value/rate controls and a true clock; they do not justify an arbitrary matrix-inverse primitive or larger state storage.

Source agent also reports Eq27's absolute combined thermal/hydraulic contribution differs from AppendixA1/A6/A8's separate norms for mixed THM rates. Zero suction and ae=1 need explicit limiting/branch policies. Parent subsequently reports independent review accepts the complete **published explicit Appendix A formulation** as the named target, with the opposing-THM Eq27 discrepancy visibly disclosed and A7/A9 tensor identity completions reviewed. This resolves variant selection without claiming Eq27 equivalence. Keep zero-suction/ae=1 analytic policies and exact source mapping explicit; they are not reasons to weaken capability gates or silently adopt author numerical clipping. Source-v2 and its independent review own those final choices.
