"""Independent source algebra / saved-data audit. No builds or material binaries.

Dense Decimal Taylor exponential and source coefficients here were separately
written by /root/barodesy2017_agent_review. Production DSL is used only as the
object under test, never as the numerical reference.
"""
import argparse, copy, hashlib, importlib.util, json, math, sys
from decimal import Decimal, localcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
MODEL='models/barodesy-clay-2017.json'
SHA='0bf4fd2789274f1271b438ffea57168866f7ebea55cfcf8ef786532903ab3477'
PDF_SHA='bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15'
SOILS=[('London',22.6,1.375,.11,.016),('Dresden',35,.622,.038,.008),('Weald',24,.8,.059,.018)]
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(x):return math.sqrt(sum(v*v for v in x))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def direction_exp(A):
    # Deliberately independent dense Decimal series, not the runtime expm.
    with localcontext() as ctx:
        ctx.prec=80
        A=[[Decimal.from_float(float(v)) for v in row] for row in A]
        n=max(sum(abs(v) for v in row) for row in A);scale=0
        while n>Decimal('.5'):n/=2;scale+=1
        A=[[v/(2**scale) for v in row] for row in A]
        I=[[Decimal(int(i==j)) for j in range(3)] for i in range(3)]
        total=copy.deepcopy(I);term=copy.deepcopy(I)
        for k in range(1,201):
            term=[[v/k for v in row] for row in mul(term,A)]
            total=[[total[i][j]+term[i][j] for j in range(3)] for i in range(3)]
            if max(abs(v) for row in term for v in row)<Decimal('1e-74'):break
        else:raise AssertionError('Decimal Taylor failed to converge')
        for _ in range(scale):total=mul(total,total)
        size=sum(v*v for row in total for v in row).sqrt()
        out=[[float(v/size) for v in row] for row in total]
    s=math.sqrt(2)
    return [out[0][0],out[1][1],out[2][2],s*out[0][1],s*out[1][2],s*out[0][2]]
def coefficients(p):
    ph,N,l,k,ss=p;s=math.sin(ph);c2=-1.5*(math.sqrt(2)+1)
    c1=(1-s)/(2*c2*c2*s);c5=(1+s)/(1-s);t=c5*l
    c3=math.sqrt(3)*(1/k-1/l)/(2**t+.002**t-2)
    c6=.5/(-math.sqrt(3)/(c3*k)+2**t-1)
    return c1,c2,c3,c5,c6

def oracle(p,state,E,factor=2):
    ph,N,l,k,ss=p;c1,c2,c3,c5,c6=coefficients(p)
    r=norm(E);sigma=state[:6];e=state[6]
    if r==0:return [0.]*7
    U=[v/r for v in E];tr=sum(U[:3]);delta=-tr
    if E[0]==E[1]==E[2] and not any(E[3:]):
        delta=-math.copysign(math.sqrt(3),E[0]);P=[1/math.sqrt(3)]*3+[0.]*3
    else:
        q=norm([v-tr/3 for v in U[:3]]+U[3:]);m=-math.sqrt(1.5)*delta/q
        x=c1*(m-c2)**2
        a=math.log(x/(1+x))/(math.sqrt(1.5)*q)
        s=math.sqrt(2);B=[[-a*U[0],-a*U[3]/s,-a*U[5]/s],[-a*U[3]/s,-a*U[1],-a*U[4]/s],[-a*U[5]/s,-a*U[4]/s,-a*U[2]]]
        P=direction_exp(B)
    L=(l+k)/2-(l-k)*delta/(2*math.sqrt(3))
    beta=-1/(c3*L)+(2**(c5*l)-1)/math.sqrt(3)
    f=c6*beta*delta-.5
    ec1=math.exp(N)*(factor*sum(sigma[:3])/(3*ss))**(-l)
    g=(1-c6)*beta*delta+((1+e)/ec1)**c5-.5
    return [c3*r*(f*norm(sigma)*v+g*w) for v,w in zip(P,sigma)]+[-(1+e)*sum(E[:3])]

def check(private_source):
    from atlas.model import load,interpret
    from atlas.initialization import initialize_state
    from atlas.evidence import checked_receipt
    assert sha(ROOT/MODEL)==SHA
    assert sha(private_source)==PDF_SHA
    model=load(ROOT/MODEL)
    research=read(ROOT/'models/research/barodesy2017/body-zero-spin.json')
    for key in ('parameters','derived','domain','equations'):assert model[key]==research[key],key
    result={'version':'barodesy2017-independent-review-check-v1','pass':True,'model_sha256':SHA,'private_source_sha256':PDF_SHA,'compiled_execution':False,'builds':False,'new_campaign':False,'source_pages_visually_inspected':[366,367,368,369,374,375],'math_bridge_fields':['parameters','derived','domain','equations'],'checks':{}}
    algebra=[]
    for name,phi,N,l,k in SOILS:
        p=[math.radians(phi),N,l,k,1000.];c1,c2,c3,c5,c6=coefficients(p)
        assert c3<0
        x=c1*(1.5-c2)**2;K=x/(1+x)
        assert abs(K-(1-math.sin(p[0])))<2e-15
        state=[1e5]*3+[0.]*3+[math.exp(N)*(100**(-l))-1]
        E=[1/3]*3+[0.]*3
        body=oracle(p,state,E);appendix=oracle(p,state,E,6)
        assert abs(body[0]/1e5-1/l)<2e-12
        assert abs(appendix[0]/1e5-1/l)>.1
        z={'sigma':state[:6],'e':state[6]};params=dict(zip(model['parameters'],p))
        initialized=initialize_state(model,z,params);assert initialized['initial']==state
        trial=copy.deepcopy(z)
        for label,E in [('zero',[0.]*6),('hydro-compression',E),('hydro-expansion',[-v for v in E]),('oedometer',[.01,0.,0.,0.,0.,0.]),('noncoaxial',[.001,-.0003,-.0002,.0004,-.0002,.0001])]:
            actual=interpret(model,z,z,E,params);a=list(actual['sigma'].v)+[actual['e']];expected=oracle(p,state,E)
            err=norm([u-v for u,v in zip(a,expected)])/max(1,norm(expected))
            assert err<2e-12,(name,label,err)
            assert z==trial
            algebra.append({'soil':name,'case':label,'scaled_rate_error':err})
    result['checks']['independent_body_algebra_and_DSL']=algebra
    invalid=[{}, {'sigma':[0.]*6,'e':.8},{'sigma':[1e5]*3+[0.]*3,'e':-1.},{'sigma':[1e5,1e5,-1.,0.,0.,0.],'e':.8}]
    params={n:f['default'] for n,f in model['parameters'].items()}
    for state in invalid:
        frozen=copy.deepcopy(state)
        try:initialize_state(model,state,params)
        except (ValueError,ArithmeticError):pass
        else:raise AssertionError('invalid state admitted')
        assert state==frozen
    result['checks']['invalid_initialization_no_mutation']=len(invalid)
    rate_checks=[]
    packet=ROOT/'catalogue/investigations/barodesy2017-runtime-v1'
    for backend in ('native','wasm'):
        report=read(packet/f'rates-{backend}.json');worst=0.
        for row in report['records']:
            req=row['request'];expected=oracle(req['parameters'],req['state'],req['increment']);actual=row['response']['values']
            error=norm([a-b for a,b in zip(actual,expected)])/max(1,norm(expected));worst=max(worst,error)
            # Independent reviewer tolerance, not a revision of original 2e-13 gate.
            assert error<2e-12,(backend,row['id'],error)
        rate_checks.append({'backend':backend,'saved_cases':len(report['records']),'maximum_independent_norm_error':worst})
    result['checks']['independent_saved_rate_comparison']=rate_checks
    pins_path='docs/ingestion/barodesy-clay-2017/production-closure-v1/pins.json'
    stale=[];resolved=[]
    for path,pin in read(ROOT/pins_path)['files'].items():
        selected=checked_receipt(ROOT,pins_path,path,pin)
        resolved.append({'path':path,'sha256':pin,'resolved':str(selected.relative_to(ROOT))})
        if selected!=ROOT/path:stale.append(path)
    result['checks']['closure_original_inputs']={'count':len(resolved),'archived_paths':stale}
    # Recompute each frozen current candidate backend assessment from raw journals.
    previews=[]
    for tail in ('barodesy2017-preview-v1','barodesy2017-preview-v2','barodesy2017-preview-v2/browser-default-v1'):
        s=ROOT/'catalogue/investigations'/tail
        spec=importlib.util.spec_from_file_location('independent_saved_assessor',s/'assess.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        a=module.assess(s);assert a['pass'];assert a==read(s/'assessment.json')
        previews.append({'path':tail,**a})
    result['checks']['current_candidate_saved_preview_assessments']=previews
    # Independently re-evaluate the separately pinned analytical assignment.
    example=read(ROOT/'docs/ingestion/barodesy-clay-2017/ncl-example-v1/example.json')
    with localcontext() as ctx:
        ctx.prec=90
        exact=(Decimal('1.375')-Decimal('.11')*Decimal(100).ln()).exp()-1
    assert abs(example['state']['e']-float(exact))<1e-14
    assert example['parameters']=={'phi_c':math.radians(22.6),'N':1.375,'lambda_star':.11,'kappa_star':.016,'sigma_star':1000}
    assert example['state']['sigma']==[1e5,1e5,1e5,0.,0.,0.]
    initialized=initialize_state(model,example['state'],example['parameters'])
    assert initialized['named_state']==example['state']
    assert example['provenance']['experimental_validation'] is False
    result['checks']['analytical_NCL_example']={'example_sha256':sha(ROOT/'docs/ingestion/barodesy-clay-2017/ncl-example-v1/example.json'),'reviewer_decimal90_e':str(exact),'rounded_e':float(exact),'supplied_e':example['state']['e'],'assignment_preserved':True,'physical_preparation_claim':False}
    probes={}
    for study in ['barodesy2017-wider-integration-v1','barodesy2017-integration-v1']:
        rows={}
        for backend in ['native','wasm']:
            r=read(ROOT/'catalogue/investigations'/study/(backend+'.json'));out=[]
            for row in r['failure_probes']:
                a=row['response'];diag=a['diagnostics'];same=a['state']==row['request']['initial'];recovered=row['recovery']==r['recovery_control']
                assert same and recovered
                out.append({'kind':row['kind'],'ok':a['ok'],'substeps':diag['substeps'],'rejected':diag['rejected'],'diagnostic_coverage':sum(diag['increment_fractions']),'returned_parent_exact':same,'recovery_control_exact':recovered})
            rows[backend]={'probes':out,'updates':sum(len(g['calls'])for g in r['records']),'trajectory_groups':len(r['records'])}
        probes[study]=rows
    result['checks']['saved_rollback_recovery']=probes
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--private-source',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args()
    result=check(a.private_source);text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text)
    else:print(text,end='')
