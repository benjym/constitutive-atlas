"""Explicit scoped recorded execution against a caller-frozen compiled catalogue.

The catalogue must originate from the validated compiler/build. Matching its
native descriptor is an identity check, not independent equation validation.
"""
import copy
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
from .recorded import MATERIAL_DEFAULTS,CONTROL_DEFAULTS,RESTART_DEFAULTS
from .recorded_scope import scoped_recorded_wire,validate_scoped_recorded_model


def _require(condition,message):
    if not condition:raise RuntimeError(message)
def _same(a,b):
    return json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False)
def _values_equal(a,b):
    if isinstance(b,dict):return isinstance(a,dict) and set(a)==set(b) and all(_values_equal(a[k],v) for k,v in b.items())
    if isinstance(b,list):return isinstance(a,list) and len(a)==len(b) and all(_values_equal(x,y) for x,y in zip(a,b))
    if type(b) in (int,float):return type(a) in (int,float) and math.isfinite(a) and a==b
    return type(a) is type(b) and a==b

def _decode(text):
    return json.loads(text,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
def _vector(value,n):
    return isinstance(value,list) and len(value)==n and all(type(x) in (int,float) and math.isfinite(x) for x in value)


def _context(spec,catalogue):
    _require(isinstance(catalogue,dict) and catalogue.get('schema_version')=='0.1' and isinstance(catalogue.get('sha256'),str) and re.fullmatch('[a-f0-9]{64}',catalogue['sha256']) and isinstance(catalogue.get('models'),list),'compiled catalogue required')
    ids=[m.get('id') for m in catalogue['models']];_require(all(isinstance(i,str) for i in ids) and len(set(ids))==len(ids),'ambiguous compiled catalogue')
    selected=[m for m in catalogue['models'] if m.get('id')==spec.get('model')];_require(len(selected)==1,'model absent from compiled catalogue')
    model=selected[0];validate_scoped_recorded_model(spec,model)
    controls,knots=scoped_recorded_wire(spec,model)
    defaults=[p['default'] for p in model['parameters'].values()]
    parameters=spec.get('parameters',defaults)
    _require(_vector(parameters,len(defaults)) and all(p['min']<=v<=p['max'] for p,v in zip(model['parameters'].values(),parameters)),'parameter shape or bounds mismatch')
    initial_default=[v for f in model['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])]
    _require(model['schema_version']!='0.3' or 'initial' in spec,'model0.3 requires explicit state')
    initial=spec.get('initial',initial_default);_require(_vector(initial,len(initial_default)),'initial state shape mismatch')
    return model,controls,knots,parameters,initial


def verify_scoped_recorded_response(result,spec,catalogue):
    """Check identity and complete output shape; retain legitimate failed prefixes."""
    _,controls,knots,parameters,initial=_context(spec,catalogue)
    material=MATERIAL_DEFAULTS|spec.get('integration_settings',{});control=CONTROL_DEFAULTS|spec.get('control_settings',{})
    restarts=RESTART_DEFAULTS|spec['restart_settings'] if 'restart_settings' in spec else None
    _require(isinstance(result,dict) and type(result.get('ok')) is bool,'invalid scoped recorded status')
    _require(result.get('api_version')=='experimental-recorded-replay-0.2','matching scoped recorded engine required; '+str(result.get('message','no versioned response')))
    expected=dict(source='state',name='sigma',measure='cauchy',scope=spec['stress_scope'],tensor_representation='mandel',sign='compression_positive')
    _require(result.get('stress')==expected and set(result['stress'])==set(expected),'scoped recorded stress mismatch')
    _require(result.get('catalogue_hash')==catalogue['sha256'] and result.get('model')==spec['model'],'scoped recorded catalogue/model mismatch')
    _require(_values_equal(result.get('controls_wire'),controls) and _values_equal(result.get('knots_wire'),knots) and _values_equal(result.get('initial_strain'),spec['path']['initial_strain']),'scoped recorded loading mismatch')
    _require(_vector(result.get('parameters'),len(parameters)) and result['parameters']==parameters and _vector(result.get('initial'),len(initial)) and result['initial']==initial,'scoped recorded parameter/initial mismatch')
    _require(_values_equal(result.get('integration_settings'),dict(version='incremental-settings-0.1',norm='scaled_component_max',**material)) and _values_equal(result.get('control_settings'),control),'scoped recorded settings mismatch')
    total=result.get('material_trials');_require(type(total) is int and total>=0,'invalid scoped recorded material trial count')
    if restarts is None:_require(not any(k in result for k in ['restart_settings','restart_diagnostics']),'unexpected scoped restart policy')
    else:
        d=result.get('restart_diagnostics');_require(_values_equal(result.get('restart_settings'),restarts) and isinstance(d,dict) and set(d)=={'searches','material_trials','accepted'} and all(type(v) is int and v>=0 for v in d.values()),'scoped recorded restart mismatch')
        _require(d['accepted']<=d['searches'] and d['material_trials']<=total and (restarts['max_restarts']!=0 or not any(d.values())),'inconsistent scoped restart accounting')
    points=result.get('points');n=len(spec['path']['knots']);failed=result.get('failed_knot')
    _require(isinstance(points,list) and type(failed) is int,'invalid scoped recorded prefix')
    _require((result['ok'] and failed==-1 and len(points)==n) or (not result['ok'] and ((not points and failed==-1) or (1<=failed<n and len(points)==failed))),'incomplete scoped recorded result')
    for i,p in enumerate(points):
        _require(isinstance(p,dict) and type(p.get('coordinate')) in (int,float) and math.isfinite(p['coordinate']) and p['coordinate']==spec['path']['knots'][i]['coordinate'] and _vector(p.get('state'),len(initial)) and _vector(p.get('strain'),6),'invalid scoped recorded point')
    _require(_vector(result.get('state'),len(initial)) and _vector(result.get('strain'),6),'invalid scoped final state')
    if points:
        _require(points[0]['state']==initial and points[0]['strain']==spec['path']['initial_strain'] and result['state']==points[-1]['state'] and result['strain']==points[-1]['strain'],'scoped recorded state/prefix mismatch')
    else:_require(result['state']==initial and result['strain']==spec['path']['initial_strain'],'invalid empty scoped failure state')
    return result


def execute_scoped_recorded(spec,catalogue,solver,timeout=60):
    """Use only the scoped CLI contract; no build, preparation or legacy fallback."""
    spec,catalogue=copy.deepcopy((spec,catalogue));_,controls,knots,_,_=_context(spec,catalogue)
    _require(type(timeout) in (int,float) and math.isfinite(timeout) and 0<timeout<=60,'timeout must be in (0,60]')
    solver=str(Path(solver).resolve())
    metadata=subprocess.run([solver,'--describe'],capture_output=True,text=True,timeout=timeout)
    described=_decode(metadata.stdout)
    _require(metadata.returncode==0 and _same(described,catalogue),'native compiled catalogue mismatch')
    _require(all(list(a['parameters'])==list(b['parameters']) for a,b in zip(described['models'],catalogue['models'])),'compiled parameter order mismatch')
    csv=lambda values:','.join(repr(float(v)) for v in values)
    with tempfile.TemporaryDirectory(prefix='atlas-scoped-recorded-') as directory:
        c,k=Path(directory)/'controls.csv',Path(directory)/'knots.csv';c.write_text(csv(controls));k.write_text(csv(knots))
        command=[solver,'--mode','recorded','--model',spec['model'],'--recorded-stress-scope',spec['stress_scope'],'--initial-strain',csv(spec['path']['initial_strain']),'--recorded-controls-file',str(c),'--recorded-knots-file',str(k),'--integration-settings',csv((MATERIAL_DEFAULTS|spec.get('integration_settings',{})).values()),'--recorded-settings',csv((CONTROL_DEFAULTS|spec.get('control_settings',{})).values())]
        if 'restart_settings' in spec:command+=['--recorded-restarts',csv((RESTART_DEFAULTS|spec['restart_settings']).values())]
        for key in ['parameters','initial']:
            if key in spec:command+=['--'+key,csv(spec[key])]
        process=subprocess.run(command,capture_output=True,text=True,timeout=timeout)
    result=_decode(process.stdout)
    _require(isinstance(result,dict) and type(result.get('ok')) is bool and process.returncode==(0 if result['ok'] else 1),'scoped recorded process status mismatch')
    return verify_scoped_recorded_response(result,spec,catalogue)
