"""Run/verify the bounded scalar-reference creep study through existing binaries."""
import argparse
import json
import math
from pathlib import Path
import subprocess

from atlas.initialization import canonical_hash
from atlas.model import ROOT, load
from atlas.schedule import DEFAULTS, schedule_command


def make_request(reference, case, model, tolerance):
    if canonical_hash(model)!=reference['model_sha256'] or model['id']!=reference['model_id']:
        raise ValueError('creep reference model pin mismatch')
    parent=case['points'][0]
    return {'schema_version':'0.2','units':'SI','model':model['id'],'start_time':0,
            'parameters':[reference['parameters'][k] for k in model['parameters']],
            'initial':parent['state'],'initial_strain':parent['strain'],'initial_strain_rate':parent['rate'],
            'segments':[{'id':'creep','duration':20,'samples':10,
                         'controls':[{'quantity':'stress','kind':'hold'} for _ in range(3)]
                                    +[{'quantity':'strain','kind':'hold'} for _ in range(3)]}],
            'solver':{'method':'backward-euler-step-doubling','relative_tolerance':tolerance,
                      'absolute_scale_fraction':1e-11,'maximum_substeps':100000}}


def compare_response(request, response, case):
    if response.get('ok') is not True:raise ValueError('creep run failed; no partial success comparison')
    for key in ('schema_version','units','model','start_time','parameters','initial','initial_strain','initial_strain_rate','segments'):
        if response.get(key)!=request[key]:raise ValueError('creep response/request mismatch: '+key)
    expected_settings=DEFAULTS|request['solver']|{'maximum_depth':40}
    if response.get('solver')!=expected_settings:raise ValueError('creep solver settings mismatch')
    points=response.get('points',[])
    expected=[(-1,'left',0),(0,'right',0)]+[(0,'left',2*i) for i in range(1,11)]
    if len(points)!=len(expected):raise ValueError('creep observation count mismatch')
    for point,(segment,side,time) in zip(points,expected):
        if (point.get('segment'),point.get('side'),point.get('time'))!=(segment,side,time):
            raise ValueError('creep grid/order/boundary mismatch')
        for key,length in (('state',4),('strain',6),('strain_rate',6),('observables',13)):
            values=point.get(key,[])
            if key=='strain_rate' and segment==0 and side=='right':
                if values != [None,None,None,0,0,0]:
                    raise ValueError('unexpected masked stress-control boundary rates')
                continue
            if (not isinstance(values,list) or len(values)!=length
                    or any(type(x) not in (int,float) or not math.isfinite(x) for x in values)):
                raise ValueError('invalid creep response channel: '+key)
    if any(points[0][k]!=request[v] for k,v in [('state','initial'),('strain','initial_strain'),('strain_rate','initial_strain_rate')]):
        raise ValueError('initial creep point differs from declared initial conditions')
    if points[0]['state']!=points[1]['state'] or points[0]['strain']!=points[1]['strain']:
        raise ValueError('hold entry must preserve persistent state and strain')
    for point in points:
        for key in ('iterations','substeps','rejected'):
            if type(point.get(key)) is not int or point[key]<0:
                raise ValueError('invalid creep diagnostic counter')
        for key,bound in [('temporal_error_norm',1),('nonlinear_residual_norm',request['solver'].get('nonlinear_tolerance',DEFAULTS['nonlinear_tolerance']))]:
            value=point.get(key)
            if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=bound*(1+1e-12):
                raise ValueError('invalid or excessive creep diagnostic norm')
        o=point['observables'];expected_stress=[o[6]+2*o[7]/3,o[6]-o[7]/3,o[6]-o[7]/3,0,0,0]
        if any(abs(a-b)>1e-7 for a,b in zip(o[:6],expected_stress)):
            raise ValueError('creep stress tensor/invariant inconsistency')
    selected=[points[0]]+points[2:]
    if len(case['points'])!=len(selected) or any(a['time']!=b['time'] for a,b in zip(selected,case['points'])):
        raise ValueError('reference grid mismatch')
    metrics={key:[max(abs(a[actual][j]-b[key][j]) for a,b in zip(selected,case['points']))
                  for j in range(length)] for key,actual,length in
                 [('state','state',4),('strain','strain',6),('rate','strain_rate',6)]}
    metrics['elastic_stress_Pa']=[max(abs(a['observables'][i]-b[key]) for a,b in zip(selected,case['points']))
                                  for i,key in [(8,'elastic_pressure'),(9,'elastic_q')]]
    metrics['held_stress_Pa']=[max(abs(p['observables'][i]-case['targets'][key]) for p in points)
                              for i,key in [(6,'pressure'),(7,'signed_q')]]
    return metrics


def run(reference, solver):
    model=load(ROOT/'models/research/terracotta-2024-fig1.json');records=[]
    for case in reference['cases']:
        for tolerance in (1e-4,1e-6,1e-8):
            request=make_request(reference,case,model,tolerance)
            process=subprocess.run(schedule_command(request,solver),capture_output=True,text=True,timeout=60)
            response=json.loads(process.stdout)
            if process.returncode!=0:raise ValueError('native creep failed: '+response.get('message',''))
            records.append({'case':case['id'],'relative_tolerance':tolerance,'request':request,
                            'response':response,'maximum_errors':compare_response(request,response,case)})
    return records


def assess_study(records, reference, expected_catalogue_hash=None):
    """Recompute errors and require the entire declared matrix, including failures."""
    model=load(ROOT/'models/research/terracotta-2024-fig1.json')
    expected={(case['id'],tol) for case in reference['cases'] for tol in (1e-4,1e-6,1e-8)}
    seen={};summary=[]
    if expected_catalogue_hash is None and records:
        expected_catalogue_hash=records[0]['response'].get('catalogue_hash')
    if not isinstance(expected_catalogue_hash,str) or len(expected_catalogue_hash)!=64 or any(c not in '0123456789abcdef' for c in expected_catalogue_hash):
        raise ValueError('missing valid creep runtime catalogue hash')
    for record in records:
        key=record['case'],record['relative_tolerance']
        if key not in expected or key in seen:raise ValueError('unexpected or duplicate creep study record')
        if record['response'].get('catalogue_hash')!=expected_catalogue_hash:
            raise ValueError('creep runtime catalogue hash mismatch')
        case=next(c for c in reference['cases'] if c['id']==key[0])
        if record['request']!=make_request(reference,case,model,key[1]):
            raise ValueError('creep study request differs from frozen reference protocol')
        metrics=compare_response(record['request'],record['response'],case)
        if record.get('maximum_errors')!=metrics:raise ValueError('creep study metrics mismatch')
        if max(metrics['held_stress_Pa'])>1e-4:raise ValueError('held total stress residual exceeds study bound')
        seen[key]=metrics
    if set(seen)!=expected:raise ValueError('incomplete creep study matrix')
    for case in reference['cases']:
        levels=[seen[(case['id'],tol)] for tol in (1e-4,1e-6,1e-8)]
        for channel in ('state','strain','rate','elastic_stress_Pa'):
            for i in range(len(levels[0][channel])):
                errors=[level[channel][i] for level in levels]
                if max(errors)>1e-13 and not errors[2]<errors[1]<errors[0]:
                    raise ValueError('creep error does not improve under tolerance refinement')
        fine=levels[-1]
        if (any(a>b for a,b in zip(fine['state'],[2e-9,2e-10,1e-7,1e-8]))
                or max(fine['strain'])>1e-8 or max(fine['rate'])>1e-9 or max(fine['elastic_stress_Pa'])>.01):
            raise ValueError('fine creep run exceeds componentwise study bounds')
        summary.append({'case':case['id'],'fine_maximum_errors':fine})
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--solver',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();records=run(json.loads(args.reference.read_bytes()),args.solver)
    assess_study(records,json.loads(args.reference.read_bytes()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(records,indent=2,allow_nan=False)+'\n')
    for record in records:print(record['case'],record['relative_tolerance'],record['maximum_errors'])


if __name__=='__main__':main()
