"""Additive independent audit; run AND implementation-v1/check_saved.py. No execution."""
from pathlib import Path
import argparse, hashlib, json, math, sys
D=Path(__file__).resolve().parent
I=D.parents[1]/'implementation-v1'
EPS=sys.float_info.epsilon
TINY=float.fromhex('0x0.0000000000001p-1022')
def load(s):
    def bad(v): raise ValueError('non-JSON number '+v)
    z=json.loads(s,parse_constant=bad)
    json.dumps(z,allow_nan=False) # Also reject exponent overflow.
    return z
def finite(x): return type(x) in (int,float) and math.isfinite(x)
def vec(x,n): return isinstance(x,list) and len(x)==n and all(finite(v) for v in x)
def same(a,b,tol=0):
    if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(same(x,y,tol) for x,y in zip(a,b))
    if finite(a) and finite(b): return abs(a-b)<=tol
    return a==b

def partition(a,u,b,v):
    if a.get('ok') is not True or b.get('ok') is not True or not vec(u,6) or not vec(v,6): return False
    da=a.get('diagnostics',{}); db=b.get('diagnostics',{})
    fs=da.get('increment_fractions',[]); gs=db.get('increment_fractions',[])
    aa=da.get('accepted_increments',[]); bb=db.get('accepted_increments',[])
    retry=da.get('partition_retries')
    if not fs or not len(fs)==len(gs)==len(aa)==len(bb) or type(retry) is not int or retry<0 or retry!=db.get('partition_retries'): return False
    for f,g,x,y in zip(fs,gs,aa,bb):
        if not finite(f) or not finite(g) or f<=0 or f!=g or not vec(x,6) or not vec(y,6): return False
        for j in range(6):
            if u[j]==v[j]:
                if x[j]!=y[j]: return False
            else:
                delta=f*(v[j]-u[j]); want=x[j]+delta
                bound=max(8*TINY,8*EPS*max(abs(x[j]),abs(y[j]),abs(delta)))
                if not all(map(math.isfinite,[delta,want,bound])) or abs(y[j]-want)>bound: return False
    return abs(sum(fs)-1)<=1e-12 and abs(sum(gs)-1)<=1e-12

def synthetic(t,f=None,retry=0,slope=78e6):
    f=[1.] if f is None else f
    return {'ok':True,'state':[0.,slope*t[1],slope*t[1],0.,0.,0.,.7],
      'diagnostics':{'increment_fractions':f,'accepted_increments':[[q*x for x in t] for q in f],'partition_retries':retry,'substeps':len(f)}}

def receipt(actual,expected,add,name):
    add(name+'/ok',actual.get('ok')==expected['ok'])
    add(name+'/state',same(actual.get('state'),expected['state']))
    d=actual.get('diagnostics',{})
    for k,v in expected['diagnostics'].items(): add(name+'/'+k,same(d.get(k),v))

def audit_fixture(r):
    checks=[]
    def add(n,p): checks.append({'name':n,'passed':bool(p)})
    policy=load((I/'cases.json').read_text())
    rows=r.get('cases',[])
    add('coverage',[x.get('id') for x in rows]==[x['id'] for x in policy['cases']])
    for c,x in zip(policy['cases'],rows):
      n=c['id']
      try:
        if c['kind']=='helper':
            total=c['total']; direction=c['direction']; base=synthetic(total,slope=-78e6 if n=='negative-slope' else 0 if n=='zero-slope' else 78e6)
            receipt(x['base'],base,add,n+'/base')
            previous=None; selected=None; calls=0
            probes=x['probes']; add(n+'/probe-count',len(probes)==c['probe_records'])
            for k,p in enumerate(probes):
                h=math.ldexp(c['initial_h'],-k); t=[u+h*d for u,d in zip(total,direction)]
                representable=all(finite(v) for v in t) and all(t[j]!=total[j] for j in range(6) if direction[j]!=0) and any(direction)
                add(n+f'/{k}/input',p['h']==h and p['increment']==t and p['representable']==representable)
                if not representable:
                    add(n+'/unrepresentable-stop',k==len(probes)-1 and p['advance']['ok'] is False and p['advance']['state']==[] and p['comparable'] is False and p['finite_slope'] is False and p['slope']==0)
                    break
                calls+=1; expected=synthetic(t)
                if (n=='jump-recovery' and k==0) or n=='exact-boundary':
                    expected=synthetic(t,[.5,.5]);expected['state'][1]-=15600;expected['state'][2]-=15600
                if n=='failed-probe-reset' and k==1: expected['ok']=False;expected['state']=base['state'][:]
                if n=='nonfinite-probe-reset':
                    if k==1:expected['state'][1]=None
                    if k==2:expected['state']=expected['state'][:1]
                    if k==3:expected['state']=[]
                if n=='overflow-slope-reset' and k==1:expected['state'][1]=expected['state'][2]=1e308
                if n=='unstable-slopes':expected=synthetic(t,slope=78e6 if k%2==0 else 156e6)
                if n=='negative-slope':expected=synthetic(t,slope=-78e6)
                if n=='zero-slope':expected=synthetic(t,slope=0)
                if n=='protocol3-direction':
                    expected['state'][0]=78e6*t[0];expected['state'][1]=expected['state'][2]=0
                    if k==0:expected['diagnostics']=synthetic(t,[.5,.5])['diagnostics'];expected['state'][0]-=15600
                receipt(p['advance'],expected,add,n+f'/{k}/callback')
                comparable=partition(x['base'],total,p['advance'],t)
                valid=comparable and vec(p['advance'].get('state'),7)
                slope=0.
                if valid:
                    def observe(s): return s[0]-.5*(s[1]+s[2]) if n=='protocol3-direction' else .5*(s[1]+s[2])
                    slope=(observe(p['advance']['state'])-observe(x['base']['state']))/h
                fs=valid and math.isfinite(slope)
                add(n+f'/{k}/recomputed-audit',p['comparable']==comparable and p['finite_slope']==fs and p['slope']==(slope if math.isfinite(slope) else None))
                stable=fs and previous is not None and abs(slope-previous)<=.001*max(1.,abs(slope),abs(previous))
                if stable:
                    selected=(h,slope);add(n+'/stops-at-first-stable-pair',k==len(probes)-1);break
                previous=slope if fs else None
            add(n+'/evaluator-count',calls==x['evaluator_calls']==c['evaluator_calls'])
            add(n+'/recomputed-decision',x['ok']==(selected is not None))
            add(n+'/recomputed-selection',(x['selected_h'],x['value'])==(selected if selected else (0,0)))
        elif c['kind']=='partition':
            a=c['base_total']; b=c['probe_total']; f=[1/3,1-1/3]
            base=synthetic(a,f,1)
            base['diagnostics']['accepted_increments']=[[v/3 for v in a],[v-v/3 for v in a]]
            probe=json.loads(json.dumps(base))
            probe['diagnostics']['accepted_increments']=[[base['diagnostics']['accepted_increments'][i][j]+f[i]*(b[j]-a[j]) for j in range(6)] for i in range(2)]
            d=probe['diagnostics']
            if n=='reject-counts':d['increment_fractions'].append(.1)
            if n=='reject-order':d['increment_fractions'].reverse()
            if n=='reject-retry':d['partition_retries']=0
            if n=='reject-missing-increments':d['accepted_increments']=[]
            if n=='reject-tensor-length':d['accepted_increments'][0].pop()
            if n=='reject-nonfinite-fraction':d['increment_fractions'][0]=None
            if n=='reject-coverage':base['diagnostics']['increment_fractions']=[.4,.4];d['increment_fractions']=[.4,.4]
            if n=='reject-affine-defect':d['accepted_increments'][0][1]+=1e-10
            if n=='reject-unchanged-channel':d['accepted_increments'][0][5]=TINY
            receipt(x['base'],base,add,n+'/base');receipt(x['probe'],probe,add,n+'/probe')
            add(n+'/recomputed-result',partition(x['base'],a,x['probe'],b)==(n=='non-dyadic-affine'))
        elif c['kind']=='elastic':
            de=x['increment']; probe=de[:];probe[1]+=1e-6;probe[2]+=1e-6
            f=[.5,.5] if n=='analytic-rate-control' else [1.]
            for label,t in [('affine_base',de),('affine_probe',probe)]:
                z=x[label];d=z['diagnostics']
                add(n+'/'+label+'/actual-affine-tensors',d['increment_fractions']==f and same(d['accepted_increments'],[[q*v for v in t]for q in f]))
                # Independent isotropic elasticity, E=30MPa and nu=.25.
                lam=12e6;mu=12e6;tr=sum(t[:3]);stress=[100000+lam*tr+2*mu*t[j] for j in range(3)]+[2*mu*t[j] for j in range(3,6)]
                want=stress+[.7-1.7*tr]
                add(n+'/'+label+'/analytical-state',vec(z.get('state'),7) and all(abs(u-v)<=(1e-6 if j<6 else 1e-12) for j,(u,v)in enumerate(zip(z['state'],want))))
            add(n+'/recomputed-affine-comparability',partition(x['affine_base'],de,x['affine_probe'],probe))
        elif c['kind']=='recovery':
            add(n+'/invalid-parent-derived',x['invalid_parent']==c['initial'][:6]+[-1.])
      except (KeyError,TypeError,ValueError,IndexError,OverflowError) as failure: add(n+'/malformed:'+str(failure),False)
    return checks

def audit_report(path):
    report=load(Path(path).read_text()); checks=[]
    ident=report['identity'];backend=ident['backend'];artifact=str(Path(ident['artifact_path']).resolve())
    expected=[artifact] if backend=='native' else ['node',str(I/'collect_wasm.mjs'),artifact]
    checks.append({'name':'process-command-bound','passed':all(p.get('command')==expected for p in report['processes']) and len(report['processes'])==(2 if backend=='native' else 1)})
    for i,c in enumerate(report['calls']):
        r=load(c['stdout'])
        for check in audit_fixture(r): checks.append({'name':f'{backend}/{i}/'+check['name'],'passed':check['passed']})
    return checks

def main():
    p=argparse.ArgumentParser();p.add_argument('reports',nargs='+');p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output)
    assert not out.exists(),'preserve prior evidence'
    checks=[]
    for f in a.reports:
        try:checks+=audit_report(f)
        except Exception as e:checks.append({'name':f+'/malformed:'+str(e),'passed':False})
    result={'identity':'control-partition-independent-audit-v2','requires_original_checker':True,'passed':bool(checks) and all(x['passed']for x in checks),'checks':checks,'reports':{str(Path(f).resolve()):hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in a.reports}}
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':result['passed'],'checks':len(checks),'failures':sum(not c['passed']for c in checks)}));return 0 if result['passed']else 1
if __name__=='__main__':raise SystemExit(main())
