"""Assess full-path reference, analytical invariants and source-only convergence."""
import hashlib
import json
import math
from pathlib import Path
import platform
import struct
import sys

ROOT=Path(__file__).resolve().parent

def bits(v):return struct.pack('>d',v)

def assess(d,policy):
    failures=[];summary={};invariants={};comparison_count=0
    def require(condition,label):
        nonlocal comparison_count
        comparison_count+=1
        if not condition:failures.append(label)
    invariant_bounds=policy['numerical_invariant_absolute_bounds']
    phase_keys={'state':4,'strain':6,'rate':6,'elastic_pressure':1,'elastic_q':1,'pressure':1,'signed_q':1}
    def difference(left,right,phase):
        result={k:([0.]*n if n>1 else 0.) for k,n in phase_keys.items()}
        for x,y in zip(left,right):
            if x['phase']!=phase:continue
            require((x['time'],x['phase'],x['side'])==(y['time'],y['phase'],y['side']),'matching sample identity')
            for k,n in phase_keys.items():
                if n>1:result[k]=[max(a,abs(b-c)) for a,b,c in zip(result[k],x[k],y[k])]
                else:result[k]=max(result[k],abs(x[k]-y[k]))
        return result
    for case in d['cases']:
        cid=case['id'];errors={};all_runs=case['rk4_refinements']+[case['midpoint']]
        for phase in ('preparation','hold'):
            errors[phase]={}
            for label,a,b in [('rk4_first_pair',0,1),('rk4_last_pair',1,2),('midpoint_fine',3,2)]:
                err=difference(all_runs[a]['points'],all_runs[b]['points'],phase);errors[phase][label]=err
                if label=='rk4_first_pair':continue
                bound=policy['reference_comparison_absolute_bounds'][phase]
                for key,val in err.items():
                    thresholds=bound[key] if key in ('state','strain','rate') else bound['stress']
                    if isinstance(val,list):
                        if not isinstance(thresholds,list):thresholds=[thresholds]*len(val)
                        require(all(a<=b for a,b in zip(val,thresholds)),f'{cid}:{phase}:{label}:{key}')
                    else:require(val<=thresholds,f'{cid}:{phase}:{label}:{key}')
        inv={'temperature_error':0.,'density_preparation_error':0.,'density_strain_error':0.,'capture_rate_error':0.,'hold_target_error':0.}
        for run in all_runs:
            pts=run['points'];targets=run['transition_targets'];prep=pts[:11];hold=pts[11:]
            require(len(pts)==22,f'{cid}:complete sample count')
            require([x['time'] for x in prep]==policy['phase_grids']['preparation'],f'{cid}:prep physical times')
            require([x['time'] for x in hold]==policy['phase_grids']['hold'],f'{cid}:hold physical times, no clock reset')
            l,r=prep[-1],hold[0]
            require(all(bits(a)==bits(b) for a,b in zip(l['state']+l['strain'],r['state']+r['strain'])),f'{cid}:exact carried state/strain')
            require((l['side'],r['side'])==('left','right'),f'{cid}:one-sided transition metadata')
            inv['capture_rate_error']=max(inv['capture_rate_error'],max(abs(a-b) for a,b in zip(l['rate'],r['rate'])))
            for q in pts:
                require(all(math.isfinite(x) for k in ('state','strain','rate') for x in q[k]),f'{cid}:finite channels')
                phi_exact=case['initial_state'][3]*math.exp(sum(q['strain'][:3]))
                inv['density_strain_error']=max(inv['density_strain_error'],abs(q['state'][3]-phi_exact))
                if q['phase']=='preparation':
                    dv,ds=case['prep_rates_Dv_Ds'];p=d['parameters'];production=p['alpha']*dv*dv+p['gamma']*ds*ds
                    exactT=math.sqrt(production/p['eta'])*math.tanh(math.sqrt(production*p['eta'])*q['time'])
                    exactphi=case['initial_state'][3]*math.exp(dv*q['time'])
                    inv['temperature_error']=max(inv['temperature_error'],abs(q['state'][2]-exactT))
                    inv['density_preparation_error']=max(inv['density_preparation_error'],abs(q['state'][3]-exactphi))
                    require(all(abs(a-b*q['time'])<=1e-15 for a,b in zip(q['strain'],case['initial_rate'])),f'{cid}:prescribed accumulated strain')
                else:
                    inv['hold_target_error']=max(inv['hold_target_error'],abs(q['pressure']-targets['pressure']),abs(q['signed_q']-targets['signed_q']))
            require(abs(prep[0]['pressure']-100000.)<1e-8 and prep[0]['signed_q']==0.,f'{cid}:100kPa zero-q start')
            require(all(q['state'][2]>0 for q in hold),f'{cid}:positive-temperature hold')
        for key,pkey in [('temperature_error','preparation_temperature'),('density_preparation_error','preparation_density'),('density_strain_error','density_strain_closure'),('capture_rate_error','capture_rate'),('hold_target_error','hold_target')]:require(inv[key]<=invariant_bounds[pkey],f'{cid}:analytic:{key}')
        summary[cid]=errors;invariants[cid]=inv
    c,e,iso=d['cases']
    for cr,er in zip(c['rk4_refinements']+[c['midpoint']],e['rk4_refinements']+[e['midpoint']]):
        for x,y in zip(cr['points'],er['points']):
            require(all(abs(x['state'][i]-sgn*y['state'][i])<=invariant_bounds['sign_symmetry'] for i,sgn in enumerate((1,-1,1,1))),'compression/extension material symmetry')
            require(abs(x['elastic_q']+y['elastic_q'])<=1e-8 and abs(x['signed_q']+y['signed_q'])<=1e-8,'compression/extension stress symmetry')
    for run in iso['rk4_refinements']+[iso['midpoint']]:
        require(all(q['state'][1]==0. and q['elastic_q']==0. and q['signed_q']==0. and q['rate'][0]==q['rate'][1]==q['rate'][2] for q in run['points']),'isotropic zero shear invariant')
    return {'identity':'terracotta-preparation-hold-reference-checks-v2','status':'pass' if not failures else 'fail','assertions':comparison_count,'failures':failures,'phase_errors':summary,'invariants':invariants}

def main():
    from reference import hold_rate
    d=json.loads((ROOT/'references.json').read_text());policy=json.loads((ROOT/'policy.json').read_text())
    result=assess(d,policy)
    singular=False
    try:hold_rate(d['cases'][0]['initial_state'],(100000.,0.))
    except ValueError:singular=True
    result['zero_temperature_stress_inversion_rejected']=singular
    if not singular:result['failures'].append('zero-temperature singularity not rejected');result['status']='fail'
    result['runtime']={'python':sys.version,'platform':platform.platform()}
    result['inputs']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('reference.py','policy.json','references.json','source-freeze.json')}
    (ROOT/'checks.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(result['status'],result['assertions'],'assertions',result['failures'])
    if result['failures']:raise SystemExit(1)

if __name__=='__main__':main()
