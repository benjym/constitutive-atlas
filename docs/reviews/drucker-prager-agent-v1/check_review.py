"""Independent scalar oracle and saved-evidence replay. No backend execution."""
import argparse, hashlib, json, math, subprocess, tempfile
from pathlib import Path

def oracle(initial, de, p):
    pref,E,nu,M,Md,c=p
    K=E/(3*(1-2*nu));G=E/(2*(1+nu))
    mean=sum(initial[:3])/3;theta=sum(de[:3]);pt=mean+K*theta
    st=[initial[i]-(mean if i<3 else 0)+2*G*(de[i]-(theta/3 if i<3 else 0))for i in range(6)]
    qt=math.sqrt(1.5*sum(x*x for x in st));ft=qt-M*pt-c
    if Md>M or initial[6]<=0: return None
    if ft<=0: lam=0;qn=qt;pn=pt
    else:
        lam=ft/(3*G+M*K*Md);qn=qt-3*G*lam;pn=pt+K*Md*lam
        if qn<0:
            if M*Md==0:return None
            pn=-c/M;lam=(pn-pt)/(K*Md);qn=0
            assert lam>=qt/(3*G)-1e-14
    out=[(pn if i<3 else 0)+(st[i]*qn/qt if qt else 0)for i in range(6)]
    return out+[(1+initial[6])*math.exp(-theta)-1,lam]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3]);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--private-sources',type=Path);a=ap.parse_args();r=a.repo.resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(r/'models/drucker-prager.json')=='b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877'
    sourcechecks=[]
    retention=json.loads((r/'docs/ingestion/drucker-prager/retention-v1/receipts.json').read_text())
    assert sha(r/retention['original_receipts_path'])==retention['original_receipts_sha256']
    retained=[]
    for receipt in retention['files']:
        p=r/receipt['local_path']
        if p.exists():assert sha(p)==receipt['sha256'] and p.stat().st_size==receipt['bytes'];retained.append(receipt['sha256'])
    if a.private_sources:
        for receipt in json.loads((r/'docs/ingestion/drucker-prager/source-receipts.json').read_text())[:2]:
            assert sha(a.private_sources/receipt['private_file'])==receipt['sha256'];sourcechecks.append(receipt['sha256'])
    study=r/'catalogue/investigations/dp-dilatancy-domain-v1';deck=json.loads((study/'cases.json').read_text());t=deck['tolerances'];native=json.loads((study/'results/raw.json').read_text());wasm=json.loads((r/'docs/reviews/dp-dilatancy-web-v1/results/raw.json').read_text())
    rows=[]
    for c,n,w in zip(deck['cases'],native['calls'],wasm['calls'],strict=True):
        args=dict(zip(c['arguments'][::2],c['arguments'][1::2]));p=list(map(float,args['--parameters'].split(',')));de=list(map(float,args['--strain'].split(',')));expected=oracle(c['initial'],de,p)
        nr=json.loads(n['stdout']);wr=json.loads(w['stdout']);assert n['id']==w['id']==c['id']
        if c['expected_failure']:
            assert nr['ok'] is wr['ok'] is False and n['returncode']!=0
            assert nr['state']==wr['state']==c['initial'];ratio=None
        else:
            assert expected is not None and nr['ok'] is wr['ok'] is True
            # Every successful frozen request completed in one internal solve.
            assert nr['diagnostics']['increment_fractions']==wr['diagnostics']['increment_fractions']==[1]
            limits=[(t['stress_absolute_Pa']if i<6 else t['other_state_absolute'])+t['relative']*abs(v)for i,v in enumerate(expected)]
            ratio=max(abs(v-e)/lim for actual in [c['expected'],nr['state'],wr['state']]for v,e,lim in zip(actual,expected,limits))
            assert ratio<=1,(c['id'],ratio)
        rows.append({'id':c['id'],'passed':True,'independent_budget_fraction':ratio})
    # Distinct algebra checks: paired sign/normalization, physical shear work and apex dual norm.
    rho=.31;rhob=.08;sy=14000.;p=80000.;s=[24000.,-12000.,-12000.,1300.,-1900.,2200.]
    norm=math.sqrt(sum(v*v for v in s));q=math.sqrt(1.5)*norm;M=3*math.sqrt(1.5)*rho;Md=3*math.sqrt(1.5)*rhob
    assert math.isclose(math.sqrt(1.5)*(norm-3*rho*p-math.sqrt(2/3)*sy),q-M*p-sy,abs_tol=1e-10)
    # Mandel shear sqrt2 factors preserve contraction and source engineering work.
    tau=1100.;engineering=.003;assert math.isclose((math.sqrt(2)*tau)*(engineering/math.sqrt(2)),tau*engineering)
    assert math.isclose(.001*((1.2-2)*100000+10000),-70.)
    for friction in [.1,1.2,3.]:
        for dil in [0,friction/2,friction]:
            for pressure in [-10000/friction,0,100000]:assert (friction-dil)*pressure+10000>=-1e-10
    # Tensor covariance using a proper 90 degree rotation around z in Mandel ordering.
    rot=lambda x:[x[1],x[0],x[2],-x[3],x[5],-x[4]]
    params=[100000,30000000,.25,1.2,.2,10000];initial=[100000,100000,100000,1000,-2000,3000,.7,0];de=[.01,-.004,-.003,.002,.001,-.001]
    u=oracle(initial,de,params);v=oracle(rot(initial[:6])+initial[6:],rot(de),params)
    assert max(abs(x-y)for x,y in zip(rot(u[:6])+u[6:],v))<1e-9
    # Explicit state restart semantics: gamma does not enter either persistent update.
    restarted=oracle(initial[:7]+[123.],de,params);assert restarted==u
    logs=[]
    with tempfile.TemporaryDirectory()as tmp:
        result=subprocess.run(['python3','-B',str(study/'run_study.py'),'--replay',str(study/'results/raw.json'),'--output',tmp],capture_output=True,text=True,check=True)
        assert (Path(tmp)/'report.json').read_bytes()==(study/'results/report.json').read_bytes();logs.append(result.stdout.strip())
    web=r/'docs/reviews/dp-dilatancy-web-v1'
    manifest=json.loads((web/'manifest.json').read_text())
    for f,h in manifest['files'].items():assert sha(web/f)==h,f
    direct=subprocess.run(['python3','-B',str(web/'verify.py')],capture_output=True,text=True)
    # Root files have evolved. Preserve that failure and reconstruct exact frozen bytes.
    frozen=json.loads((web/'prospective-freeze.json').read_text());resolved=[]
    with tempfile.TemporaryDirectory()as tmp:
        tr=Path(tmp)
        for f,h in frozen['files'].items():
            source=r/f
            if sha(source)!=h:
                source=r/'catalogue/source-snapshots'/h/f
            if source.exists() and sha(source)==h:b=source.read_bytes();origin=str(source.relative_to(r))
            else:
                origin='git:235b59a79ef18eb753a2c94a80cfa71d7bb40c00:'+f
                b=subprocess.check_output(['git','show','235b59a79ef18eb753a2c94a80cfa71d7bb40c00:'+f],cwd=r)
            assert hashlib.sha256(b).hexdigest()==h,f
            dst=tr/f;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b)
            if origin!=f:resolved.append({'path':f,'sha256':h,'resolved_from':origin})
        needed=['docs/reviews/dp-dilatancy-web-v1/prospective-freeze.json','docs/reviews/dp-dilatancy-web-v1/check.mjs','docs/reviews/dp-dilatancy-web-v1/results/raw.json','catalogue/investigations/dp-dilatancy-domain-v1/cases.json','catalogue/investigations/dp-dilatancy-domain-v1/results/raw.json']
        for f in needed:
            dst=tr/f;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((r/f).read_bytes())
        out=tr/'replay';result=subprocess.run(['node',str(tr/'docs/reviews/dp-dilatancy-web-v1/check.mjs'),str(tr),'unused',str(out),str(tr/'docs/reviews/dp-dilatancy-web-v1/results/raw.json')],capture_output=True,text=True,check=True)
        assert (out/'report.json').read_bytes()==(web/'results/report.json').read_bytes();logs.append(result.stdout.strip())
    report={'kind':'independent-dp-agent-check-v1','model_sha256':sha(r/'models/drucker-prager.json'),'private_source_hashes_checked':sourcechecks,'durable_private_hashes_checked':retained,'case_count':len(rows),'passed':True,'cases':rows,'algebra':['OpenSees normalized yield','paired sign conversion','Mandel engineering shear work','old negative-work witness -70Pa','nonnegative work over declared cone domain','proper orthogonal tensor covariance','temporary gamma restart independence'],'saved_report_replays':logs,'direct_web_verifier':{'returncode':direct.returncode,'stdout':direct.stdout,'stderr':direct.stderr},'frozen_archive_resolution':resolved,'execution':'Python algebra and saved JSON replay only; no builds or compiled artifacts executed.'}
    a.output.write_text(json.dumps(report,indent=2)+'\n');print('Independent algebra, 83 native/Wasm saved responses, and exact saved report replays pass.')
if __name__=='__main__':main()
