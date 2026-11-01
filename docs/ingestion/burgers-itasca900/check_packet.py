"""Source-partition checks. No compiled solver, vendor code or path integrator."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D, localcontext
import argparse, hashlib, json, math, sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from atlas.model import load, defaults, interpret
from atlas.initialization import initialize_state
R=Path(__file__).resolve().parent

def run(private=False):
    results=[]
    def passed(name,count): results.append(dict(check=name,cases=count,result='pass'))
    receipts=json.loads((R/'source-receipts.json').read_text())['sources']
    if private:
        for s in receipts:
            b=Path(s['private_path']).read_bytes()
            assert hashlib.sha256(b).hexdigest()==s['sha256']
            assert b"9.0.184" in b
        passed('exact private source bytes/version',3)
    m=load(R/'continuous-draft-v03.json'); p=defaults(m)
    prepared=initialize_state(m,{'sigma':[100000]*3+[0]*3,'ek':[0]*6},p,time=0,loading=[0]*6)
    assert len(prepared['initial'])==12
    for state in [{'sigma':[0]*6},{'sigma':[0]*6,'ek':[1,0,0,0,0,0]}]:
        try: initialize_state(m,state,p,time=0,loading=[0]*6)
        except ValueError: pass
        else: raise AssertionError('invalid initialization accepted')
    passed('v0.3 semantic/dimensional validation and explicit initialization',3)
    def dot(a,b): return sum(x*y*(1 if j<3 else 2) for j,(x,y) in enumerate(zip(a,b)))
    for i in range(1,201):
        gm,gk,em,ekv=F(i+3,3),F(i+5,7),F(i+7,5),F(i+11,2)
        h=F(i,37); bulk=F(i+13,9)
        s=[F(i,11),-F(i+1,13),0,F(i%7,9),-F(i%5,17),F(i%3,19)];s[2]=-s[0]-s[1]
        k=[F(i%11,71),F(i%13,73),0,F(i%17,79),F(i%19,83),F(i%23,89)];k[2]=-k[0]-k[1]
        de=[F(i%5,31),-F(i%7,41),0,F(i%3,43),F(i%11,47),F(i%13,53)];de[2]=-de[0]-de[1]
        A=1+gk*h/(2*ekv);B=1-gk*h/(2*ekv)
        a=1/(2*gm)+h/4*(1/em+1/(A*ekv));b=1/(2*gm)-h/4*(1/em+1/(A*ekv))
        sn=[(de[j]+b*s[j]-(B/A-1)*k[j])/a for j in range(6)]
        kn=[(B*k[j]+h*(sn[j]+s[j])/(4*ekv))/A for j in range(6)]
        for j in range(6):
            # Independent original partition residuals, not another update formula.
            avg=(sn[j]+s[j])/2;avgk=(kn[j]+k[j])/2
            assert avg==2*ekv*(kn[j]-k[j])/h+2*gk*avgk
            assert de[j]==kn[j]-k[j]+(sn[j]-s[j])/(2*gm)+avg*h/(2*em)
        assert sum(sn[:3])==sum(kn[:3])==0
        # Continuous energy identity with arbitrary chosen stress derivative.
        sd=de; kd=[(s[j]-2*gk*k[j])/(2*ekv) for j in range(6)]
        ed=[kd[j]+sd[j]/(2*gm)+s[j]/(2*em) for j in range(6)]
        mean=F(i,23);md=F(1,29);vd=md/bulk
        power=dot(s,ed)+mean*vd
        ud=dot(s,sd)/(2*gm)+2*gk*dot(k,kd)+mean*md/bulk
        diss=dot(s,s)/(2*em)+2*ekv*dot(kd,kd)
        assert power-ud==diss and diss>=0
    passed('centered deviatoric update satisfies source Kelvin/Maxwell partitions',200)
    passed('continuous Cartesian power/storage/nonnegative dissipation identity',200)
    # Hydrostatic equation independent of Burgers shear state.
    for v in [F(-3,7),F(0),F(5,11)]:
        old=F(19,3); bulk=F(13,5);new=old+bulk*v
        assert (new-old)/bulk==v
    passed('elastic volume and zero deviatoric drive',3)
    with localcontext() as ctx:
        ctx.prec=80
        gm,gk,em,ev=D(6),D(2),D(3),D(4);s=D(5);k0=D(1)/3
        for t in [D(0),D('.1'),D(1),D(4)]:
            z=(-gk*t/ev).exp(); k=s/(2*gk)+(k0-s/(2*gk))*z
            kd=-(gk/ev)*(k0-s/(2*gk))*z
            strain=s/(2*gm)+k+s*t/(2*em)
            strain_d=kd+s/(2*em)
            assert abs(s-2*ev*kd-2*gk*k)<D('1e-65')
            assert abs(strain_d-kd-s/(2*em))<D('1e-65')
            if t==0: assert strain==s/(2*gm)+k0
        passed('constant-stress exponential creep and initial elastic jump',4)
        a=-D(7)/2;b=D(6);c=D(1)/8;d=-D(1)/2
        r1=-D(2)+D(3).sqrt();r2=-D(2)-D(3).sqrt()
        assert r2<r1<0
        sd0=a*s+b*k0
        C1=(sd0-r2*s)/(r1-r2);C2=s-C1
        for t in [D(0),D('.1'),D(1),D(4)]:
            st=C1*(r1*t).exp()+C2*(r2*t).exp()
            sd=C1*r1*(r1*t).exp()+C2*r2*(r2*t).exp()
            sdd=C1*r1*r1*(r1*t).exp()+C2*r2*r2*(r2*t).exp()
            kt=(sd-a*st)/b; kd=(sdd-a*sd)/b
            assert abs(sd-a*st-b*kt)<D('1e-65')
            assert abs(kd-c*st-d*kt)<D('1e-65')
            if t==0: assert abs(kt-k0)<D('1e-65')
        passed('two-exponential zero-strain-rate relaxation source residuals',4)
    # Model-rate evidence checks against source partitions in Cartesian components.
    max_residual=0.
    for i in range(1,101):
        cart=[1000*i,-300*i,700*i,71*i,-31*i,17*i]
        ek=[i/1e6,-i/3e6,-2*i/3e6,i/7e6,-i/11e6,i/13e6]
        rate=[i/1e7,-i/2e7,i/3e7,i/5e7,-i/7e7,i/11e7]
        def enc(v): return v[:3]+[math.sqrt(2)*x for x in v[3:]]
        def dec(v): return list(v[:3])+[x/math.sqrt(2) for x in v[3:]]
        out=interpret(m,{'sigma':enc(cart),'ek':enc(ek)},None,enc(rate),p,time=.25)
        sd,kd=dec(out['sigma'].v),dec(out['ek'].v)
        mean=sum(cart[:3])/3;v=sum(rate[:3]);sdmean=sum(sd[:3])/3
        for j in range(6):
            sj=cart[j]-(mean if j<3 else 0)
            kelvin=2*p['etak']*kd[j]+2*p['Gk']*ek[j]
            source_rate=kd[j]+(sd[j]-(sdmean if j<3 else 0))/(2*p['Gm'])+sj/(2*p['etam'])
            for ref,val in [(sj,kelvin),(rate[j]-(v/3 if j<3 else 0),source_rate)]:
                residual=abs(val-ref)/max(1,abs(ref));max_residual=max(max_residual,residual)
                assert residual<=1e-12
        assert abs(sdmean-p['Kmod']*v)<=1e-12*max(1,abs(sdmean))
    passed('interpreter rates in independent Cartesian source-partition residuals',100)
    # Compatible preparation kills Kelvin rate but not Maxwell creep/relaxation.
    s=[120000,60000,120000,0,0,0];mean=sum(s[:3])/3
    k=[(s[j]-(mean if j<3 else 0))/(2*p['Gk']) for j in range(6)]
    out=interpret(m,{'sigma':s,'ek':k},None,[0]*6,p,time=0)
    assert max(abs(x) for x in out['ek'].v)<1e-15
    assert max(abs(x) for x in out['sigma'].v)>0
    passed('compatible Kelvin preparation is not a stationary strain hold',1)
    return dict(study='burgers-source-algebra-v1',checks=results,total_cases=sum(x['cases'] for x in results),max_cartesian_normalized_residual=max_residual,private_sources_checked=private,compiled_or_vendor_calls=0,finite_path_integrations=0,scientific_admission=False)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--private-sources',action='store_true');ap.add_argument('--write-results',action='store_true');args=ap.parse_args()
    result=run(args.private_sources)
    if args.write_results:(R/'check-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
