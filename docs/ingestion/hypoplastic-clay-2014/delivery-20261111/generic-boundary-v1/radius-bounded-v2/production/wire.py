"""Frozen scoped recorded wires, shared by the native and Wasm profile."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys

D=Path(__file__).resolve().parent
C=D.parents[2]
read=lambda p:json.loads(p.read_text())
def csv(a):return ','.join(map(str,a))
def bits(a):return [struct.pack('>d',x).hex() for x in a]

def prepare():
    d=read(C/'controlled-regression-v1/protocol.json')
    m=read(C/'candidate-v3.json')
    cases=[]
    for group in ('original_equal_lateral_positive','distinct_two_lateral_positives','original_equal_lateral_negatives'):
        rows=d[group] if isinstance(d[group],list) else [d[group]]
        for f in rows:
            x,y=f['parent'][:2]
            ctr=f.get('recorded_controls_wire') or sum(d['original_equal_lateral_rows'],[])
            knots=f.get('recorded_knots_wire') or sum([[i/16,x,y,(i if i<=16 else 32-i)*2e-5/16,0,0,0,0] for i in range(33)],[])
            assert bits(f['parent'])==f['parent_bits']
            cases.append(dict(id=f['id'],negative=group.endswith('negatives'),parent=f['parent_bits'],
                       args=[m['id'],csv(f['parameters'][k] for k in m['parameters']),csv(f['parent']),
                             '0,0,0,0,0,0',csv(ctr),csv(knots),'2e-10,1e-8,45,20,20000,11','','effective']))
    print(json.dumps(cases,indent=2))

def assess(case,row):
    if case['negative']:
        ok=(not row['ok'] and not row.get('points',[]) and 'state' in row and bits(row['state'])==case['parent']
            and row['message']=='simultaneous stress constraints did not converge; entire path rolled back')
        return dict(pass_=ok,reason=row.get('message'))
    ref=[]
    for source in ('independent-boundary-v1/results.json','independent-onset-v2/results.json'):
        f=read(C/source)['cases'].get(case['id'],{})
        if f.get('pass'):ref=f['attempts'][-1]['checkpoints'];break
    if not ref:
        f=next(x for x in read(C/'independent-path-v1/supplement-results.json')['cases'] if x['id']==case['id'])
        assert f['status']=='converged' and f['passing_consecutive_pairs']>=2
        ref=f['attempts'][-1]['checkpoints']
    if not row['ok'] or len(row['points'])!=33:
        return dict(pass_=False,reason=row.get('message'))
    errors=[]
    for a,b in zip(row['points'][1:],ref,strict=True):
        assert a['coordinate']==b['segment']-1+b['fraction']
        z,t=a['state'],b['state']
        e=[math.dist(z[:6],t[:6]),abs(z[6]-t[6]),math.dist(z[7:],t[7:])]
        c=[1e-3+2e-6*max(1e5,math.hypot(*t[:6])),2e-8,2e-9]
        errors.append(dict(coordinate=a['coordinate'],errors=e,caps=c,passed=all(i<=j for i,j in zip(e,c))))
    return dict(pass_=all(x['passed'] for x in errors),checkpoints=errors)

def native(binary,output,match):
    output.mkdir(exist_ok=False)
    for case in read(D/'wire-fixtures.json'):
        name=case['id']
        if match and match not in name:continue
        model,p,z,e,c,k,mat,settings,scope=case['args']
        cfile=output/(name+'.controls')
        kfile=output/(name+'.knots')
        cfile.write_text(c);kfile.write_text(k)
        cmd=[str(binary.resolve()),'--mode','recorded','--model',model,'--parameters',p,'--initial',z,
             '--initial-strain',e,'--recorded-controls-file',str(cfile),'--recorded-knots-file',str(kfile),
             '--integration-settings',mat,'--recorded-stress-scope',scope]
        q=subprocess.run(cmd,capture_output=True,text=True)
        (output/(name+'.json')).write_text(q.stdout)
        (output/(name+'.stderr')).write_text(q.stderr)
        (output/(name+'.exit')).write_text(str(q.returncode)+'\n')
        a=assess(case,json.loads(q.stdout))
        (output/(name+'.assessment')).write_text(json.dumps(a,indent=2)+'\n')
        print(name,a['pass_'],a.get('reason'),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=('prepare','native'))
    ap.add_argument('--binary',type=Path)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--match')
    a=ap.parse_args()
    if a.action=='prepare':prepare()
    else:
        for n,h in read(D/'wire-freeze.json').items():
            assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h,n
        native(a.binary,a.output,a.match)
