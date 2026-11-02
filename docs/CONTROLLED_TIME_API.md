# Controlled physical-time external-field ODE API

The v0.3 `physical_time` / `controlled_ode` profile adds typed imposed thermal/hydraulic scalar fields alongside symmetric infinitesimal mechanical strain. It is distinct from `ode` and dimensionless `path_ode`. Equations are derivatives per second. It supports32 persistent scalar components,32 imposed-control components,256 scalar parameters and24observable fields/144components. A symmetric Mandel tensor consumes6components.

This implementation is undergoing source/pure qualification. **Native/Wasm builds, actual compiled acceptance and scientific model approval are separate gates; none is claimed by this document.** Generic engine fixtures are not public scientific models.

## Typed controls and stage equations

The model declares `formulation.controls.strain` as quantitystrain, shapesym, unit1, finite, measureinfinitesimal_strain and configurationcurrent. It is accumulated prescribed strain in Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. Other controls are scalar fields with explicitquantity/unit/valueconstraint. Temperature usesK and suctionPa, with model-supported bounds in domain. Scalar constraints finite/positive_finite/nonnegative_finite apply to values, not rates.

Required equation inputs time and strain_rate declare physicalseconds and Mandelrate/s. strain_rate has `binding:{control:strain,derivative_order:1}`. A scalarfield value/rate input binds its namedcontrol at order0/1, with exactvalueunit or valueunit/s and quantity suffix_rate for derivatives. Eachcontrol/order pair is unique. A symmetricorder0 strain input is optional. Externalvalues/rates are never guessed fromstate orparameters. All declaredcontrols must beprovided evenwhen unusedbyequations. Stageinput flattenedcapacity is65 (time+2×32), checked bysemanticvalidation.

Advances require positive finite duration and finite starttime with representablylater endpoint. Controls interpolate linearly, alltheir derivatives constantduringoneadvance, at matchingtime/state stages. A zero-rate hold has positivephysicalduration and may evolve. Zero-durationadvance rejects; instantaneous evaluation is separate. Split prescribed discontinuities; valuejumps require explicitreinitialization/provenance. This is imposed-field constitutive evolution, not coupled transport/poromechanics, stresscontrol, DAE, generalized tangent or finite-rotationobjectivity.

## Python

```python
from atlas.model import load
from atlas.controlled_time import initialize, advance, Settings, context_from_dict
from dataclasses import asdict
model = load('tests/fixtures/controlled-time/transport.json')
params = {name: field['default'] for name,field in model['parameters'].items()}
state = {'sigma':[10000,20000,30000,4000,-5000,6000],
         'clock_memory':-3.5, 'e':0.8, 'memory':2.0}
values = {'strain':[0.0]*6, 'temperature':300., 'suction':200000.}
rates = {'strain':[0.0]*6, 'temperature':0., 'suction':0.}
parent = initialize(model,state,11.,values,rates,params)
result = advance(model,parent,4.,values,values,Settings())
restart = context_from_dict(model,asdict(result.context))
```

This purely synthetic example is an engineverification fixture. Explicitinitialization checks allpersistentfields, parameters, currentcontrolvalues/rates, domain, initialchecks andobservables; no hiddenzero rate. `Context` stores state,time,controls,control_rates,parameters,model_sha256 andprofile. Restart requiresallfields and exactprofile/modelhash and validates evolvingdomain without rerunningpreparation-onlyinitialchecks. `advance` checksstartvaluesexactlymatchcommittedcontrols andnevermutatesparent. It returns context,finalobservables,leftincoming-rateobservables,rightnew-rateobservables andfourdiagnostics. A ratejump is an observable transition at unchanged state/time/values; no automaticpersistentjump. `run` validates `run-controlled-time-v1.schema.json`, runs1..100linearsegments with1..200samples each and<=10000total intervals, and exposes nopartialresultafterfailure.

Numerics: explicitmidpoint stepdoubling, fullvs2half Richardsonfactor3, accept2halfstate without extrapolation. Localcomponent weights are3×(absolute_scale_fraction×state_scale+relative_tolerance×max(abs(parent),abs(candidate))). Domain/finitenesschecks atallstages. Settings are explicit; localerror doesnot boundglobaltrajectoryerror. The original pure default-rtol1e-8 exponentialreferencegatefailed its unchangedglobalbound; distinctstricter-studyv2 usesrtol1e-10 and retainsthatfailure. Neitherdefault norboundswere silentlyrelaxed. Refinement/stiffness qualification remainsmodel-specific.

## Dedicated generator and checked native/Wasm ABI

```
python3 tools/generate_controlled_time.py --output OUTPUT MODEL.json
```

Outputs controlled_time_models.hpp, controlled_time_api.cpp and controlled_time_catalogue.json (profile controlled-time-ode-v1). Mixed/oldprofiles rejectbeforedestinationwrites. Genericcommoncompiler refusescontrolled-time, even though physical_time(model) istrue. Existingmaterial/path/timeABIs retainidentities. Native/Wasm target atlas_controlled_time_capability is in cmake/controlled-time; builds requirecoordinatorserialhandoff and --parallel1. No model-specific handwrittenkernel.

Exports controlled_time_size/evaluate/advance. Everyarray hasexplicitpointer/count; size fields0..5 give state,parameters,flattenedcontrols,flattenedobservables,settings(6),diagnostics(4). Native ctypes adapter NativeEngine is explicitly instantiated onlybyauthorizedcaller; import executesnobinary. DedicatedCLI `controlled-time-run` needs exactdefinition/module/catalogue/specification/output; it neverbuilds.

`evaluate` argumentorder:

```
model, state,ns, parameters,np, time, values,nc, incoming_rates,nr,
initial_flag, derivatives,nstate, observables,no, scales,nstate
```

`advance` argumentorder:

```
model, state,ns, parameters,np, start_time,duration,
current_values,nc, current_rates,nr, controls_start,nstart, controls_end,nend,
settings,nsettings, state_out,nstate, time_out,1,
controls_out,ncontrol, rates_out,ncontrol, observables,no, diagnostics,4
```

Settingorder absolute_scale_fraction,relative_tolerance,minimum_step_seconds,maximum_step_seconds,maximum_depth,maximum_trials. Depthinteger1..60; trialsinteger1..1000000 checkedbeforecast; positivefinitefirstfour withmin<=max. Diagnosticorder trials,accepted_half_steps,rejected_trials,final_error. Aliaspolicy rejects everyinput/output andoutput/outputoverlap, permitsreadonlyinput/inputoverlap. Checkeduintptrrange arithmeticbeforeanydereference, nullonlyforzeroactualcount, exactlengths/flags/indices, alloutputs untouchedonfailureincludingdiagnostics. Normalnativeallocationvalidity remainscallerresponsibility. Completeoutputwritesoccuronlyaftersuccess. Tests mustchecksentinels/recoveryinactualcompiledABI; Pythonagreementaloneisnotproof.

## Stress and delivery

The newprofile maybind symmetricPaobservablestress with scopeneffective,total ornet. Net means total minus imposedairpressureidentity in compression-positiveconvention; noconversion or airpressure is inferred. No Bishop/effective mapping or experimental overlay follows. Oldprofiles retain effective/total schemaenum and oldexecutionroutes rejectcontrolled-time. Newprofilebrowser/mainatlas packaging is a separateStageB task; this capability addsno standalonepage, publiccatalogueentry, approval orliveclaim.


The generator also exports `controlled_time_model_hash(model)`,
`controlled_time_catalogue_hash()` and `controlled_time_catalogue_file_hash()` as
read-only C strings. These identify the exact canonical model, canonical catalogue
payload and exact generated catalogue JSON bytes. Native loading checks all three;
Wasm loading checks the exact catalogue bytes and selected model identity before
material calls. Matching array sizes alone does not establish identity.

Prospective compiled qualification uses the standalone 18-case closed-form corpus
in `docs/ingestion/vibe-2026/controlled-time-qualification-v1/`. Native tests require
`ATLAS_CONTROLLED_TIME_SOURCE_MANIFEST` and `ATLAS_CONTROLLED_TIME_RAW_OUTPUT` in
addition to the explicit module/catalogue environment variables. Wasm qualification
requires `MODULE CATALOGUE OUTPUT SOURCE_MANIFEST`. Both retain raw observations,
diagnostics and failed output buffers, bind exact compiled artifacts/catalogue,
reference corpus and implementation manifest, and require a new output identity for
each attempt. No compiled qualification has been performed in Stage A source work.
