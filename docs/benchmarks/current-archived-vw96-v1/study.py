"""Frozen, bounded synthetic compatibility study; no builds, fits or data reads.

run NEW_ABSOLUTE_DIRECTORY: execute exactly the frozen serial commands.
audit DIRECTORY: reconstruct the scalar result from saved native receipts only.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.benchmark_tmd2 import command
from tools.strict_observation_json import loads
HERE = Path(__file__).resolve().parent

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')

def vector(value, size):
    require(isinstance(value,list) and len(value)==size, 'vector dimension')
    require(all(type(x) in (int,float) and math.isfinite(x) for x in value), 'finite numeric vector')
    return value

def semantic(model):
    value=json.loads(json.dumps(model)); value.pop('sources')
    for parameter in value['parameters'].values():
        parameter.pop('label',None)
    return value

def inputs():
    policy=read(HERE/'policy.json'); freeze=read(HERE/'freeze.json')
    require(sha(HERE/'policy.json')==freeze['policy_sha256'],'policy changed')
    require(sha(Path(__file__))==freeze['study_sha256'],'study changed')
    for name,digest in policy['input_sha256'].items():
        require(sha(ROOT/name)==digest,'input changed: '+name)
    old=read(ROOT/policy['model_files']['archived']); new=read(ROOT/policy['model_files']['current'])
    require(semantic(old)==semantic(new),'mathematical model mismatch')
    require(list(new['parameters'])==policy['parameter_names'],'parameter order mismatch')
    return policy,freeze

def expected_commands(policy):
    commands=[]
    def add(engine,kind,name,options):
        arguments=['--model',policy['model'],'--parameters',','.join(map(repr,policy['parameters'])),
                   '--initial',','.join(map(repr,policy['initial']))]
        commands.append({'engine':engine,'kind':kind,'case':name,'command':[policy['engines'][engine]['path']]+arguments+options})
    for engine,entry in policy['engines'].items():
        commands.append({'engine':engine,'kind':'describe','case':'catalogue','command':[entry['path'],'--describe']})
        for name,strain in policy['law_directions'].items():
            add(engine,'evaluate',name,['--mode','evaluate','--current',','.join(map(repr,policy['initial'])),'--strain',','.join(map(repr,strain))])
        add(engine,'zero','zero',['--mode','integrate','--strain','0,0,0,0,0,0'])
        for path in policy['paths']:
            for steps in policy['caller_steps']:
                add(engine,'run',path['id']+'-'+str(steps),['--mode','run','--protocol',str(path['protocol']),
                    '--target',repr(path['target']),'--steps',str(steps),'--cycles',str(path['cycles'])])
    require(len(commands)==22,'unexpected command budget')
    return commands

def validate_run(raw,request,policy,catalogue):
    options=dict(zip(request['command'][1::2],request['command'][2::2]))
    steps=int(options['--steps']); protocol=int(options['--protocol']); cycles=int(options['--cycles']); target=float(options['--target'])
    for key,value in [('model',policy['model']),('parameters',policy['parameters']),('initial',policy['initial']),
                      ('protocol',protocol),('cycles',cycles),('steps',steps),('target',target),('catalogue_hash',catalogue['sha256'])]:
        require(raw.get(key)==value,'run input echo: '+key)
    require(type(raw.get('points')) is list and len(raw['points'])==steps+1,'incomplete run')
    require(raw['points'][0]['state']==policy['initial'],'initial state mismatch')
    sums={'substeps':0,'rejected':0,'iterations':0}
    for index,point in enumerate(raw['points']):
        state=vector(point['state'],7); strain=vector(point['strain'],6)
        control=target*math.sin(2*math.pi*cycles*index/steps) if cycles else target*index/steps
        require(abs(point['control']-control)<=1e-15 and abs(strain[0]-control)<=1e-14,'caller coordinates differ')
        for key in sums:
            require(type(point[key]) is int and point[key]>=0,'invalid counter '+key)
            sums[key]+=point[key]
        require(type(point['error']) in (int,float) and point['error']>=0,'invalid reported error')
        require(abs(state[1]-state[2])<policy['stress_control_absolute_pa'],'axisymmetric stress')
        require(max(map(abs,state[3:6]))<=1e-12,'unexpected shear stress')
        require(max(map(abs,strain[3:6]))<=1e-12,'unexpected shear strain')
        if protocol==1:
            require(max(abs(state[i]-policy['initial'][i]) for i in [1,2])<policy['stress_control_absolute_pa'],'drained stress control')
        else:
            require(abs(sum(strain[:3]))<=policy['volume_control_absolute'],'undrained volume control')
        q=state[0]-.5*(state[1]+state[2]); mean=sum(state[:3])/3
        u=0 if protocol==1 else policy['initial'][1]-.5*(state[1]+state[2])
        for key,value in [('q_signed',q),('q',abs(q)),('p',mean),('u',u)]:
            require(abs(point[key]-value)<=1e-7,'observable mismatch '+key)
    return sums

def difference(a,b):
    require(len(a)==len(b),'point coverage mismatch')
    maxima={'stress_pa':0.,'void_ratio':0.,'strain':0.,'observable_pa':0.}
    for x,y in zip(a,b):
        require(abs(x['control']-y['control'])<=1e-15,'comparison knots differ')
        maxima['stress_pa']=max(maxima['stress_pa'],max(abs(i-j) for i,j in zip(x['state'][:6],y['state'][:6])))
        maxima['void_ratio']=max(maxima['void_ratio'],abs(x['state'][6]-y['state'][6]))
        maxima['strain']=max(maxima['strain'],max(abs(i-j) for i,j in zip(x['strain'],y['strain'])))
        maxima['observable_pa']=max(maxima['observable_pa'],max(abs(x[k]-y[k]) for k in ['p','q','q_signed','u']))
    return maxima

def compatible(delta,policy):
    thresholds=policy['compatibility_limits']
    return all(delta[key]<=limit for key,limit in thresholds.items())

def audit(out):
    policy,freeze=inputs(); commands=expected_commands(policy); saved=read(out/'processes.json')
    require(len(saved)==len(commands),'receipt coverage mismatch')
    require(read(out/'execution-freeze.json')=={'policy_sha256':sha(HERE/'policy.json'),
            'study_sha256':sha(Path(__file__)),'freeze_sha256':sha(HERE/'freeze.json')},'execution freeze differs')
    raw={}; catalogues={}; diagnostics={}
    for index,request in enumerate(commands):
        stem=f'process-{index:02d}'; receipt=read(out/(stem+'.json'))
        require(saved[index]==dict(request,receipt_sha256=sha(out/(stem+'.json'))),'command ledger differs')
        require(receipt['command']==request['command'],'actual command differs')
        require(type(receipt['returncode']) is int and receipt['returncode']==0,'nonzero process returncode')
        require(receipt['stdout_sha256']==sha(out/(stem+'.stdout')) and receipt['stderr_sha256']==sha(out/(stem+'.stderr')),'process output changed')
        response=read(out/(stem+'.stdout')); engine=request['engine']; kind=request['kind']
        if kind=='describe':
            require(response['sha256']==policy['engines'][engine]['catalogue_hash'],'catalogue identity mismatch')
            matches=[m for m in response['models'] if m['id']==policy['model']]
            require(len(matches)==1 and semantic(matches[0])==semantic(read(ROOT/policy['model_files'][engine])),'compiled model definition mismatch')
            catalogues[engine]=response
        else:
            require(response.get('ok') is True,'native material call failed')
            if kind=='run':
                diagnostics[(engine,request['case'])]=validate_run(response,request,policy,catalogues[engine])
            elif kind=='evaluate':
                vector(response['values'],7)
            else:
                vector(response['state'],7)
        raw[(engine,kind,request['case'])]=response
    scales=[policy['stress_scale_pa']]*6+[1.]
    law=[]
    for name in policy['law_directions']:
        a=raw[('archived','evaluate',name)]['values']; b=raw[('current','evaluate',name)]['values']
        delta=max(abs(x-y)/scale for x,y,scale in zip(a,b,scales))
        law.append({'case':name,'maximum_scaled_difference':delta,'pass':delta<=policy['law_scaled_tolerance']})
    zero=[{'engine':engine,'pass':raw[(engine,'zero','zero')]['state']==policy['initial']} for engine in policy['engines']]
    comparisons=[]; caller_changes=[]
    for path in policy['paths']:
        for steps in policy['caller_steps']:
            key=path['id']+'-'+str(steps)
            delta=difference(raw[('archived','run',key)]['points'],raw[('current','run',key)]['points'])
            comparisons.append({'path':path['id'],'steps':steps,'maximum_differences':delta,'pass':compatible(delta,policy),
                'diagnostics':{engine:diagnostics[(engine,key)] for engine in policy['engines']}})
        for engine in policy['engines']:
            a=raw[(engine,'run',path['id']+'-32')]['points']; b=raw[(engine,'run',path['id']+'-64')]['points'][::2]
            caller_changes.append({'engine':engine,'path':path['id'],'maximum_differences':difference(a,b),'scope':'descriptive only; two resolutions do not establish convergence'})
    return {'id':policy['id'],'policy_sha256':sha(HERE/'policy.json'),'freeze_sha256':sha(HERE/'freeze.json'),
            'native_processes':len(commands),'material_calls':20,'catalogue_queries':2,
            'overall_compatibility_pass':all(row['pass'] for row in law+zero+comparisons),
            'raw_law':law,'zero_increment':zero,'path_comparisons':comparisons,'caller_changes':caller_changes,
            'limits':policy['limits']}

def run(out):
    policy,freeze=inputs()
    require(out.is_absolute() and not out.exists() and ROOT not in out.parents,'new absolute output outside repo required')
    for engine in policy['engines'].values():
        require(sha(Path(engine['path']))==engine['artifact_sha256'],'artifact identity changed')
    out.mkdir(parents=True)
    write(out/'execution-freeze.json',{'policy_sha256':sha(HERE/'policy.json'),
          'study_sha256':sha(Path(__file__)),'freeze_sha256':sha(HERE/'freeze.json')})
    ledger=[]
    for index,request in enumerate(expected_commands(policy)):
        command(request['command'],out,f'process-{index:02d}')
        ledger.append(dict(request,receipt_sha256=sha(out/f'process-{index:02d}.json')))
        write(out/'processes.json',ledger)
    for engine in policy['engines'].values():
        require(sha(Path(engine['path']))==engine['artifact_sha256'],'artifact changed during study')
    result=audit(out);write(out/'results.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    require(len(sys.argv)==3 and sys.argv[1] in ['run','audit'],'usage: study.py run|audit DIRECTORY')
    if sys.argv[1]=='run':run(Path(sys.argv[2]))
    else:print(json.dumps(audit(Path(sys.argv[2])),indent=2))
