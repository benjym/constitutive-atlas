"""Source-onlyv2 replay and support assessment. No native/Wasm execution."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)


def fresh_references(rate_record=None,support_record=None):
    import reference
    import support
    rate=json.loads((HERE/'reference.json').read_text()) if rate_record is None else rate_record
    sup=json.loads((HERE/'support-reference.json').read_text()) if support_record is None else support_record
    if canonical(rate)!=canonical(reference.build_reference()):raise ValueError('rate reference differs from fresh independent replay')
    if canonical(sup)!=canonical(support.build_support_reference()):raise ValueError('support reference differs from fresh independent replay')
    return rate,sup


def assess(repo):
    sys.path.insert(0,str(repo))
    from atlas.model import load,defaults,prepare_increment,evaluation_environment
    from atlas.dsl import I,Sym,evaluate,parse
    import reference
    rate,support_reference=fresh_references()
    m=load(HERE/'model.json');params=defaults(m)
    def evaluated(c):
        state=dict(sigma=c['state'][:6],e=c['state'][6]);E=c['increment'];pars=params|c['parameters']
        prepare_increment(m,state,E,pars)
        return evaluation_environment(m,state,state,E,pars)
    observations=[]
    for c in rate['cases']:
        env=evaluated(c);values=list(env['stress_rate'].v)+[env['e_rate']]
        if any(type(x) not in (int,float) or not math.isfinite(x)for x in values):raise ValueError('nonfinite observed rate')
        se=max(abs(x-y)for x,y in zip(values[:6],c['expected'][:6]));ve=abs(values[6]-c['expected'][6])
        sb=rate['policy']['stress_absolute_floor_Pa']+rate['policy']['stress_relative_to_scale']*c['stress_scale']
        vb=rate['policy']['void_absolute_floor']+rate['policy']['void_relative_to_scale']*c['void_scale']
        if se>sb or ve>vb:raise ValueError('unchanged rate comparison gate failed:'+c['id'])
        observations.append(dict(id=c['id'],values=values,stress_error_Pa=se,stress_bound_Pa=sb,void_error=ve,void_bound=vb))
    invalid=[]
    for c in json.loads((HERE/'invalid-cases.json').read_text())['cases']:
        results={}
        for name,action in [('draft',lambda:evaluated(c)),('cartesian',lambda:reference.evaluate(c))]:
            try:action()
            except (ValueError,ArithmeticError)as exc:results[name]=dict(rejected=True,message=str(exc))
            else:raise ValueError('historical invalid accepted:'+c['id']+':'+name)
        invalid.append(dict(id=c['id'],results=results))
    support_rows=[]
    for c in json.loads((HERE/'support-inputs.json').read_text())['cases']:
        results={}
        for name,action in [('draft',lambda:evaluated(c)),('cartesian',lambda:reference.evaluate(c))]:
            try:
                got=action();accepted=True
                if name=='draft':values=list(got['stress_rate'].v)+[got['e_rate']]
                else:values=list(got['expected'])
                if any(type(x) not in(int,float)or not math.isfinite(x)for x in values):raise ValueError('accepted output is not finite7rate')
                results[name]=dict(accepted=True,finite_rate=True)
            except (ValueError,ArithmeticError)as exc:
                accepted=False;results[name]=dict(accepted=False,message=str(exc))
            if accepted is not c['expected_accepted']:raise ValueError('support status mismatch:'+c['id']+':'+name)
        support_env={'I':I,'sigma':Sym(tuple(c['state'][:6])),**params,**c['parameters']}
        for item in m['derived']:
            if not item['name'].startswith('support_'):break
            support_env[item['name']]=evaluate(parse(item['expr']),support_env)
        guard={name:support_env[name] for name in ['support_xx','support_yy','support_zz','support_minor2','support_det']}
        support_rows.append(dict(id=c['id'],expected_accepted=c['expected_accepted'],results=results,computed_guard=guard))
    pins={f:hashlib.sha256((HERE/f).read_bytes()).hexdigest()for f in ['model.json','reference.py','reference.json','invalid-cases.json','support.py','support-inputs.json','support-reference.json','protocol.json']}
    runtime={f:hashlib.sha256((repo/f).read_bytes()).hexdigest()for f in ['atlas/model.py','atlas/dsl.py','atlas/scalar_math.py','atlas/structure.py','schemas/model.schema.json']}
    return dict(version='clay2005-source-plus-spd-rate-v2-python-check',pins=pins,runtime_pins=runtime,rate_cases=observations,historical_invalids=invalid,support_cases=support_rows,compiled_execution=False,admission=False,
                limitations=['support-only cases do not certify near-singular rate accuracy','near-isotropic highprecision accuracy unresolved','no finite integration or physicaladmissibility proof'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    repo=a.repo or next((r for r in HERE.parents if(r/'atlas/model.py').is_file()),None)
    if repo is None:raise SystemExit('--repo required outside installedcheckout')
    if a.output and a.output.exists():raise SystemExit('fresh output path required')
    result=assess(repo.resolve())
    if a.output:a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('41historical rates,10historical invalids,29support statuses PASS; no compiled execution')
