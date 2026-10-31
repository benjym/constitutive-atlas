"""Deterministic literal stored-input corpus, without Atlas or material evaluation."""
from pathlib import Path
import itertools,json,math,hashlib
P=Path(__file__).parent
hx=lambda v:[float(x).hex() for x in v]
def corpus():
    seeds=[]
    for j in range(38):
        v=[float(i==j) for i in range(30)] if j<30 else [(((j+1)*(i+3))%17-8)/(1+(i+j)%5) for i in range(30)]
        seeds.append(dict(current=hx(v[:12]),parent=hx(v[12:24]),loading=hx(v[24:])))
    # Traceless trial and mu=2 make these diagonal control increments exactly dyadic.
    bases={'elastic':[2,0,-2],'face':[9,0,-9],'upper':[5,4,-9],'lower':[9,-4,-5],
           'repeat-upper':[4,4,-8],'repeat-lower':[8,-4,-4],
           'yield':[3,0,-3],'face-upper-boundary':[8,2,-10],'face-lower-boundary':[10,-2,-8]}
    cases=[];ep=[.125,-.25,.375,-.5,.625,-.75]
    def put(name,loading,parent=None,parameters=None):
        cases.append(dict(id=name,parameters=parameters or dict(p_ref=1.,lame_lambda=3.,mu=2.,k=3.),current=hx([.25,-.5,.75,.1,-.2,.3]+[.01,-.02,.03,-.04,.05,-.06]),parent=hx(parent or [0.]*6+ep),loading=hx(loading)))
    for name,v in bases.items():put(name,[x/4 for x in v]+[0]*3)
    for name,v in bases.items():
        if name in ('yield','face-upper-boundary','face-lower-boundary'):continue
        for j,perm in enumerate(itertools.permutations(range(3))):
            if j:put(name+'-permutation-'+str(j),[v[i]/4 for i in perm]+[0]*3)
    Q=[[1/9,8/9,4/9],[8/9,1/9,-4/9],[-4/9,4/9,-7/9]]
    for name,v in bases.items():
        a=[[sum(Q[i][k]*v[k]*Q[j][k]/4 for k in range(3)) for j in range(3)]for i in range(3)]
        put('dense-'+name,[a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]])
    for h in (0.,64.,-64.):
        put('hydro-'+str(h),[0]*6,parent=[h,h,h,0,0,0]+ep)
    for name in ('yield','face-upper-boundary','face-lower-boundary'):
        v=bases[name]
        for sign in (-1,1):
            d=[x/4 for x in v]+[0]*3;d[1]=math.nextafter(d[1],math.inf if sign>0 else -math.inf)
            put(name+'-neighbor-'+str(sign),d)
    for power in (-80,80):
        scale=2.**power
        put('scaled-face-'+str(power),[x/4 for x in bases['face']]+[.1,-.2,.3],parameters=dict(p_ref=scale,lame_lambda=3*scale,mu=2*scale,k=3*scale))
    put('large-offset-face',[x/4 for x in bases['face']]+[0]*3,parent=[2.**40]*3+[0]*3+ep)
    put('near-isolation-upper',[x/4 for x in bases['repeat-upper']]+[0]*3,parent=[2.**60]*3+[0]*3+ep)
    history_loading=[[.125,-.0625,-.0625,0,0,0],[2,-1,-1,0,0,0],[0,0,0,.5,.125,-.25],[-.25,.125,.125,0,0,0],[0]*6,[-3,1.5,1.5,-.25,0,.125],[0,0,0,-.5,-.125,.25],[3,-1.5,-1.5,0,0,0],[0]*6,[-1,.5,.5,.25,-.125,.0625],[1,-.5,-.5,-.25,.125,-.0625],[0]*6]
    return dict(version='tresca-literal-rounded-inputs-0.1',columns=38,seeds=seeds,cases=cases,history=dict(initial=hx([0]*6+ep),parameters=dict(p_ref=1.,lame_lambda=3.,mu=2.,k=3.),loading=[hx(v) for v in history_loading]),rejection_plan=[dict(id=x,requirement=y)for x,y in [('missing-state','Reject missing sigma or ep before evaluation'),('outside-initial','Reject supplied initial exact-rounded principal range above2k; do not silently project'),('nonpositive-parameters','Reject each zero/negative p_ref,lambda,mu,k'),('nonfinite-input','Reject nonfinite state/loading/parameter/seed without partial commit'),('spectral-isolation','Report source-valid near-isolation cases separately; selected backend guard must reject honestly'),('overflow','Retain finite-input overflow failure and immediate same-instance recovery'),('rollback','Every rejected attempt returns all12 incoming persistent components unchanged')]])
if __name__=='__main__':
    data=corpus();target=P/'inputs.json';assert not target.exists(),'Use a fresh task identity instead of overwriting frozen inputs';target.write_text(json.dumps(data,indent=2)+'\n')
    pins={n:hashlib.sha256((P/n).read_bytes()).hexdigest()for n in ('inputs.json','reference-policy.json','sources.json','freeze_inputs.py','spectral_source.py','generate.py','check.py')}
    (P/'pre-generation-freeze.json').write_text(json.dumps(pins,indent=2)+'\n')
    print(json.dumps(dict(cases=len(data['cases']),directions=len(data['seeds']),history_steps=len(data['history']['loading']))))
