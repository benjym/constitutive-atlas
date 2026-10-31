"""Portable source-only draft/reference checks, not a compiled study collector."""
import copy
import hashlib
import json
import math
from pathlib import Path
from atlas.model import load, interpret
from atlas.dsl import Sym
import reference

HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_reference(record=None):
    protocol=json.loads((HERE/'protocol.json').read_text())
    for name,digest in protocol['frozen_inputs'].items():
        if sha(HERE/name)!=digest: raise ValueError('changed frozen dependency:'+name)
    supplied=json.loads((HERE/'reference.json').read_text()) if record is None else copy.deepcopy(record)
    # Exact fresh replay includes both precision grids, all channels and failures.
    fresh=reference.build_reference()
    canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
    if canonical(supplied)!=canonical(fresh): raise ValueError('frozen reference differs from fresh independent replay')
    if len(supplied['records'])!=protocol['valid_count'] or len(supplied['invalid'])!=protocol['invalid_count']:
        raise ValueError('reference completeness')
    for row in supplied['records']:
        # Precision differences are empirical evidence, not rigorous certificates.
        for x,y in zip(row['oracle80']['values'],row['oracle120']['values']):
            if abs(x-y)>4*math.ulp(y):raise ValueError('precision replay insufficient')
    return supplied


def draft_rate(case, model=None):
    model=load(HERE/'model-draft.json') if model is None else model
    if type(case) is not dict or set(case)!={'id','state','loading','parameters'} or type(case['id']) is not str:
        raise ValueError('exact case keys required')
    pars=case['parameters']
    if type(pars) is not dict or set(pars)!=set(model['parameters']):raise ValueError('parameter names')
    for n,spec in model['parameters'].items():
        v=pars[n]
        if type(v) not in (int,float) or not math.isfinite(v) or not spec['min']<=v<=spec['max']:
            raise ValueError('parameter bounds/type:'+n)
    for name,n in [('state',7),('loading',6)]:
        a=case[name]
        if type(a) not in (list,tuple) or len(a)!=n or any(type(x) not in (int,float) or not math.isfinite(x) for x in a):
            raise ValueError('finite non-Boolean vector:'+name)
    state={'sigma':case['state'][:6],'e':case['state'][6]}
    values=interpret(model,state,state,case['loading'],pars)
    if set(values)!={'sigma','e'} or not isinstance(values['sigma'],Sym):raise ValueError('draft state layout')
    result=list(values['sigma'].v)+[values['e']]
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in result):raise ValueError('nonfinite equation result')
    return result


def assess_values(case,actual,expected):
    if type(expected) not in (list,tuple) or len(expected)!=7 or any(type(x) not in(int,float) or not math.isfinite(x) for x in expected):
        raise ValueError('finite non-Boolean reference seven-rate required')
    if type(actual) not in (list,tuple) or len(actual)!=7 or any(type(x) not in(int,float) or not math.isfinite(x) for x in actual):
        raise ValueError('finite non-Boolean seven-rate required')
    p=case['parameters'];sn=math.hypot(*case['state'][:6]);dn=math.hypot(*case['loading'])
    if not any(case['loading']):
        if any(x!=0 for x in actual):raise ValueError('exact zero-loading rates required')
        return {'stress_scaled_error':0.,'void_ulp_error':0.}
    natural=(p['c4']+p['c5']*sn)*dn/(case['state'][6]-p['emin'])
    scale=max(natural,math.hypot(*expected[:6]))
    error=max(abs(x-y) for x,y in zip(actual[:6],expected[:6]))/scale
    if error>2e-12:raise ValueError('stress rate accuracy')
    if expected[6]==0:
        if actual[6]!=0:raise ValueError('exact zero void rate required')
        vu=0.
    else:
        vu=abs(actual[6]-expected[6])/math.ulp(expected[6])
        if vu>4:raise ValueError('void rate4ULP accuracy')
    return {'stress_scaled_error':error,'void_ulp_error':vu}


def run():
    frozen=checked_reference()
    inputs=reference.read_inputs()
    expected={x['id']:x for x in frozen['records']}
    if len(expected)!=len(inputs['valid']):raise ValueError('unique case identity')
    model=load(HERE/'model-draft.json')
    rows=[]
    for c in inputs['valid']:
        result=draft_rate(c,model)
        metrics=assess_values(c,result,expected[c['id']]['oracle120']['values'])
        rows.append({'id':c['id'],'draft_values':result,**metrics})
    rejected=[]
    for c in inputs['invalid']:
        try:draft_rate(c,model)
        except (ValueError,ArithmeticError) as exc:rejected.append({'id':c['id'],'rejected':True,'message':str(exc)})
        else:raise ValueError('draft accepted invalid:'+c['id'])
    return {'version':'barodesy-sand-2015-python-rate-check-v1','records':rows,'invalid':rejected,
            'compiled_execution':False,'admission':False}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=run()
    if args.output:
        if args.output.exists():raise SystemExit('fresh output path required')
        args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('PASS',len(result['records']),'valid,',len(result['invalid']),'rejected; max stress scaled error',max(x['stress_scaled_error']for x in result['records']))
