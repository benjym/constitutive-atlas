"""Original twelve prescribed-strain paths, using the same recorded ABI."""
import hashlib,json,math,subprocess,sys
from pathlib import Path
from wire import C,D,csv,read

names=['independent-boundary-v1/results.json','independent-onset-v2/results.json',
       'independent-path-v1/path-results.json']
frozen=C/'independent-path-v1/frozen-protocol.json'

def prepare():
    proto=read(frozen);model=read(C/'candidate-v3.json')
    rows=[0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1]
    out=[]
    for f in proto['cases']:
        label=f['protocol']
        if label=='drained-axisymmetric':continue
        x=proto['initial_states'][f['initial']]
        point=[0.]*6;knots=[0.,*point]
        for i,s in enumerate(proto['protocols'][label]):
            inc=s['increment'] if s['mode']=='strain' else [-.5*s['axial']]*2+[s['axial'],0,0,0]
            for a in proto['checkpoints']:
                knots.extend([i+a,*(u+a*v for u,v in zip(point,inc,strict=True))])
            point=[u+v for u,v in zip(point,inc,strict=True)]
        out.append(dict(id=f['id'],args=[model['id'],csv(x['parameters'][k] for k in model['parameters']),
                csv(x['state']),'0,0,0,0,0,0',csv(rows),csv(knots),'2e-10,1e-8,45,20,20000,11','','effective']))
    assert len(out)==12
    print(json.dumps(out,indent=2))

def native(binary,out):
    out.mkdir()
    for f in read(D/'strain-fixtures.json'):
        model,p,z,e,c,k,m,_,scope=f['args'];name=f['id']
        cf,kf=out/(name+'.controls'),out/(name+'.knots')
        cf.write_text(c);kf.write_text(k)
        r=subprocess.run([str(binary.resolve()),'--mode','recorded','--model',model,'--parameters',p,
                          '--initial',z,'--initial-strain',e,'--recorded-controls-file',str(cf),
                          '--recorded-knots-file',str(kf),'--integration-settings',m,'--recorded-stress-scope',scope],
                         capture_output=True,text=True)
        (out/(name+'.json')).write_text(r.stdout)
        (out/(name+'.stderr')).write_text(r.stderr)
        (out/(name+'.exit')).write_text(str(r.returncode)+'\n')
        print(name,json.loads(r.stdout)['ok'],flush=True)

def assess(out):
    refs={}
    for f in names:
        group=read(C/f)['cases']
        if isinstance(group,list):
            group={v['id']:v for v in group if v['status']=='converged' and v['passing_consecutive_pairs']>=2}
        else:group={k:v for k,v in group.items() if v['pass']}
        for k,v in group.items():refs.setdefault(k,v['attempts'][-1]['checkpoints'])
    r={}
    for f in read(D/'strain-fixtures.json'):
        name=f['id'];q=read(out/(name+'.json'))
        if not q['ok']:
            r[name]=dict(pass_=False,reason=q['message']);continue
        rows=[]
        for a,b in zip(q['points'][1:],refs[name],strict=True):
            assert a['coordinate']==b['segment']-1+b['fraction']
            z,t=a['state'],b['state']
            e=[math.dist(z[:6],t[:6]),abs(z[6]-t[6]),math.dist(z[7:],t[7:])]
            c=[1e-3+2e-6*max(1e5,math.hypot(*t[:6])),2e-8,2e-9]
            rows.append(dict(coordinate=a['coordinate'],error=e,cap=c,passed=all(x<=y for x,y in zip(e,c))))
        r[name]=dict(pass_=all(x['passed'] for x in rows),checkpoints=rows)
    passed=all(x['pass_'] for x in r.values())
    print(json.dumps(dict(pass_=passed,cases=r),indent=2))
    return 0 if passed else 1

if sys.argv[1]=='prepare':prepare()
else:
    for n,h in read(D/'strain-freeze.json').items():
        assert hashlib.sha256((D/n).read_bytes()).hexdigest()==h,n
    if sys.argv[1]=='native':native(Path(sys.argv[2]),Path(sys.argv[3]))
    else:sys.exit(assess(Path(sys.argv[2])))
