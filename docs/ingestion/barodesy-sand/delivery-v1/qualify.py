"""Run common production CLI/C ABI against prospectively frozen references.

Coordinator only. Raw responses are saved before assessment. This is a new
study, retaining the unchanged original rate oracle/budgets and prior failure.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MODEL = 'barodesy-sand'
CSV = lambda values: ','.join(format(float(v), '.17g') for v in values)
P = CSV([-1.0246,1,-2.3,465000,28,.87,.35])
Z = CSV([100000,100000,100000,0,0,0,.75])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('backend', choices=['native','wasm'])
    parser.add_argument('artifact', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    policy = json.loads((HERE/'policy.json').read_text())
    limits = policy['budgets']
    settings = policy['settings']
    rows, errors = [], []
    max_error = {'default':[0.,0.,0.], 'tight':[0.,0.,0.]}
    process = subprocess.Popen(['node', str(HERE/'wasm-transport.mjs'), str(args.artifact.resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True) if args.backend=='wasm' else None

    def check(ok, tag):
        if not ok:
            errors.append(tag)

    def call(tag, mode, **kw):
        q = dict(mode=mode, model=MODEL, parameters=P, initial=Z, settings=settings['default'])
        q.update(kw)
        if process:
            process.stdin.write(json.dumps(q)+'\n'); process.stdin.flush()
            raw = json.loads(process.stdout.readline())['raw']
        else:
            if mode=='describe':
                command = [str(args.artifact.resolve()), '--describe']
            else:
                command = [str(args.artifact.resolve()), '--mode', mode, '--model', q['model'], '--parameters',q['parameters'],'--initial',q['initial']]
                if mode=='evaluate': command += ['--current',q['initial'],'--strain',q['strain']]
                elif mode=='integrate': command += ['--strain',q['strain'],'--integration-settings',q['settings']]
                else:
                    for key in ('protocol','target','steps','cycles'): command += ['--'+key,str(q[key])]
                    command += ['--integration-settings',q['settings']]
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            raw = result.stdout
        rows.append(dict(id=tag, request=q, raw=raw))
        (args.output/'journal.json').write_text(json.dumps(rows,indent=2)+'\n')
        return json.loads(raw)

    request = call

    descriptor = request('describe','describe')
    source = json.loads((ROOT/'models/barodesy-sand.json').read_text())
    check(next(m for m in descriptor['models'] if m['id']==MODEL)==source, 'embedded exact model identity')
    old = json.loads((ROOT/'catalogue/investigations/barodesy2015-rates-v2/protocol.json').read_text())
    for case in old['cases']:
        _,p,z,d = case['args']
        out = request('rate/'+case['id'],'evaluate',parameters=p,initial=z,strain=d)
        expected = case['expectation']
        check(out.get('ok') is expected['ok'], case['id']+' rate status')
        if expected['ok'] and out.get('ok'):
            check(len(out['values'])==7 and all(abs(a-b)<=c for a,b,c in zip(out['values'],expected['values'],expected['absolute_budgets'])),case['id']+' unchanged independent rate budgets')
    references = json.loads((HERE/'references.json').read_text())
    for key, ref in references.items():
        c = ref['case']
        for variant in ('default','tight'):
            out = request(key+'/'+variant,'run',protocol=c['protocol'],target=c['target'],steps=c['steps'],cycles=c['cycles'],settings=settings[variant])
            check(out.get('ok') is True,key+'/'+variant+' success')
            points = out.get('points',[])
            check(len(points)==len(ref['points']),key+' point count')
            for index, (point, expected) in enumerate(zip(points,ref['points'])):
                stress_error = max(abs(a-b) for a,b in zip(point['state'][:3],expected[:3]))
                void_error = abs(point['state'][6]-expected[3])
                strain_error = max(abs(a-b) for a,b in zip(point['strain'][:3],expected[4:]))
                for j,v in enumerate((stress_error,void_error,strain_error)): max_error[variant][j]=max(max_error[variant][j],v)
                check(stress_error<=limits['stress_absolute_Pa'] and void_error<=limits['void_absolute'] and strain_error<=limits['strain_absolute'],key+'/'+variant+f' independent point{index}')
                check(abs(point['state'][3])+abs(point['state'][4])+abs(point['state'][5])==0,key+' zero offdiagonals')
                check(abs(point['state'][6]-((1+.75)*math.exp(-math.fsum(point['strain'][:3]))-1))<=limits['void_absolute'],key+' independent volume')
            if variant=='default' and out.get('ok'):
                middle=len(points)//2
                z=points[middle]['state']
                for i in range(middle+1,len(points)):
                    d=[a-b for a,b in zip(points[i]['strain'],points[i-1]['strain'])]
                    restarted=request(key+f'/restart-{i}','integrate',initial=CSV(z),strain=CSV(d))
                    check(restarted.get('ok') is True,key+' restart success')
                    z=restarted.get('state',z)
                check(max(abs(a-b) for a,b in zip(z[:6],points[-1]['state'][:6]))<=limits['restart_stress_Pa'] and abs(z[6]-points[-1]['state'][6])<=limits['restart_void'],key+' complete midpoint restart')
    check(max_error['tight'][0]<=max_error['default'][0]+.01,'tighter settings stress refinement')
    check(max_error['tight'][1]<=max_error['default'][1]+1e-10,'tighter settings void refinement')
    ref=json.loads((HERE/'oblique-reference.json').read_text())
    z=ref['initial']
    for i,d in enumerate(ref['increments']):
        out=request('oblique/'+str(i),'integrate',initial=CSV(z),strain=CSV(d))
        check(out.get('ok') is True,'oblique success')
        z=out.get('state',z)
        check(max(abs(a-b) for a,b in zip(z[:6],ref['points'][i+1][:6]))<=limits['stress_absolute_Pa'] and abs(z[6]-ref['points'][i+1][6])<=limits['void_absolute'],'oblique independent full state '+str(i))
    bits=lambda z:[struct.pack('>d',float(v)).hex() for v in z]
    zero=request('zero','integrate',strain='0,0,0,0,0,0')
    check(zero.get('ok') and bits(zero['state'])==bits([float(v) for v in Z.split(',')]),'zero exact identity')
    failure=request('forced-failure','integrate',strain='.01,0,0,0,0,0',settings=settings['forced_failure'])
    check(failure.get('ok') is False and bits(failure.get('state',[]))==bits([float(v) for v in Z.split(',')]),'failed increment exact rollback')
    recovered=request('after-failure','integrate',strain='0,0,0,0,0,0')
    check(recovered.get('ok') and bits(recovered['state'])==bits(zero['state']),'same-instance recovery')
    if process:
        process.stdin.close();process.wait(timeout=5)
    result=dict(pass_all=not errors,errors=errors,calls=len(rows),maximum_errors=max_error,artifact=str(args.artifact.resolve()),artifact_sha256=hashlib.sha256(args.artifact.read_bytes()).hexdigest(),policy_sha256=hashlib.sha256((HERE/'policy.json').read_bytes()).hexdigest())
    (args.output/'assessment.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__=='__main__':
    main()
