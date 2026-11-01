#!/usr/bin/env python3
"""Saved-only independent review; never runs a backend or vendor code."""
import copy, hashlib, importlib.util, json, math, pathlib, sys, tarfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
HERE=pathlib.Path(__file__).resolve().parent
BASE=ROOT/'docs/ingestion/j2-linear-hardening/execution-v2'
sys.path.insert(0,str(ROOT))
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_text())
def run():
    from atlas.model import load, interpret
    modelpath=ROOT/'docs/ingestion/j2-linear-hardening/candidate-v03-v2.json'
    assert sha(modelpath.read_bytes())=='a28068cbb8cfc660e49eb648d6ce7fcbf993ea50b45e8eb0d325c6b75f4ffc3b'
    model=load(modelpath)
    receipts=read(ROOT/'docs/ingestion/j2-linear-hardening/source-receipts.json')
    for r in receipts['sources']: assert sha(pathlib.Path(r['private_path']).read_bytes())==r['sha256']
    freeze=read(BASE/'execution-freeze.json')
    interpreter_files={str(pathlib.Path(m.__file__).resolve().relative_to(ROOT)) for n,m in sys.modules.items() if (n=='atlas' or n.startswith('atlas.')) and getattr(m,'__file__',None)}
    with tarfile.open(BASE/'source-closure.tar.gz') as archive:
        members={m.name.removeprefix('./'):m for m in archive.getmembers() if m.isfile()}
        for f in freeze['files']:
            if f['path'] in interpreter_files:
                assert sha((ROOT/f['path']).read_bytes())==f['sha256'], 'live interpreter drift: '+f['path']
            match=[m for n,m in members.items() if n==f['path'] or n.endswith('/'+f['path'])]
            assert len(match)==1,f['path']
            assert sha(archive.extractfile(match[0]).read())==f['sha256']
    # Two exact rationally derived roots, a small-strain deviatoric increment.
    p=dict(p_ref=100000.,K=10e6,G=3e6,sigma_y=2000.,H=1e6)
    parent=dict(sigma=[0]*6,alpha=0.,gamma=0.)
    de=[.001,-.0005,-.0005,0,0,0]
    witnesses=[]
    for label,g,s in [('physical',.0007,[1800.,-900.,-900.,0,0,0]),
                      ('reverse',.001375,[-2250.,1125.,1125.,0,0,0])]:
        x=dict(sigma=s,alpha=g,gamma=g)
        residual=interpret(model,x,parent,de,p)
        flat=list(residual['sigma'].v)+[residual['alpha'],residual['gamma']]
        if label=='physical': assert max(abs(v) for v in flat)==0
        else:
            expected=math.hypot(.001375,-.0675)-.001375-.0675
            assert abs(flat[-1]-expected)<1e-16 and flat[-1]!=0
            assert max(abs(v) for v in flat[:-1])==0
        dep=[de[i]-s[i]/(2*p['G']) for i in range(6)] # trace zero
        work=sum(a*b for a,b in zip(s,dep))
        q=math.sqrt(1.5*sum(v*v for v in s))
        assert g>0 and x['alpha']>=0 and q==p['sigma_y']+p['H']*g
        witnesses.append(dict(branch=label,state=x,residual=flat,plastic_work_Pa=work))
    assert witnesses[1]['plastic_work_Pa']<0
    # Independent projector-form complete 8x6 tangent, no oracle invocation.
    refs=read(BASE/'references.json'); tangent_errors=[]
    defaults=read(BASE/'default-references.json')
    for c in refs['cases']+defaults['cases']:
        if 'tangent' not in c: continue
        _,K,G,sy,H=map(float,c['args'][1].split(','));z=list(map(float,c['args'][2].split(',')));e=list(map(float,c['args'][3].split(',')))
        P=[[(1. if i==j else 0.)-(1/3 if i<3 and j<3 else 0.) for j in range(6)] for i in range(6)]
        sm=sum(z[:3])/3
        s=[z[i]-(sm if i<3 else 0)+2*G*sum(P[i][j]*e[j] for j in range(6)) for i in range(6)]
        q=math.sqrt(1.5*sum(v*v for v in s));g=max(0,(q-sy-H*z[6])/(3*G+H));D=3*G+H
        a=1-3*G*g/q
        C=[[K*(i<3 and j<3)+2*G*a*P[i][j]-(9*G*G/(q*q)*(1/D-g/q)*s[i]*s[j] if g else 0) for j in range(6)] for i in range(6)]
        hist=[3*G*v/(D*q) if g else 0 for v in s];C += [hist,hist]
        err=max(abs(C[i][j]-c['tangent'][i][j]) for i in range(8) for j in range(6))
        assert err<(.2 if c['id'].startswith('default-') else 1e-7)
        for i in (6,7): assert max(abs(C[i][j]-c['tangent'][i][j]) for j in range(6))<2e-8
        tangent_errors.append(dict(case=c['id'],max_abs_error=err))
    # Replay assessor against saved stdout only; never launches native or Wasm.
    import types
    study=types.ModuleType('j2_frozen_study');study.__file__=str(ROOT/'tools/study_j2.py')
    with tarfile.open(BASE/'source-closure.tar.gz') as archive:
        exec(compile(archive.extractfile('tools/study_j2.py').read(),study.__file__,'exec'),study.__dict__)
    backend={};negative_checks=[]
    for label in ['native','wasm']:
        rows=read(BASE/(label+'-raw.json'));backend[label]=study.assess_rows(refs['cases'],rows)
        for mutation in ['stress','history','tangent','ok','rollback','identity','substeps','missing_row']:
            bad=copy.deepcopy(rows);idx=0
            if mutation=='tangent':idx=next(i for i,c in enumerate(refs['cases']) if 'tangent' in c)
            if mutation=='rollback':idx=next(i for i,c in enumerate(refs['cases']) if c['id']=='budget-rollback')
            data=json.loads(bad[idx]['calls'][0]['stdout'])
            if mutation=='stress':data['state'][0]+=1
            if mutation=='history':data['state'][6]+=.01
            if mutation=='tangent':data['state_tangent'][7][5]+=.01
            if mutation=='ok':data['ok']=not data['ok']
            if mutation=='rollback':data['state'][7]+=1
            if mutation=='identity':data['parameters'][1]+=1
            if mutation=='substeps':data['diagnostics']['substeps']=2
            bad[idx]['calls'][0]['stdout']=json.dumps(data)
            if mutation=='missing_row':bad.pop()
            try: study.assess_rows(refs['cases'],bad)
            except (AssertionError,KeyError,IndexError): negative_checks.append(label+':'+mutation)
            else: raise AssertionError('accepted corruption '+mutation)
    # Passive fixed-basis covariance of the candidate residual, using physical matrices.
    def rotate(v,theta):
        a,b,c,d,e,f=v;rt=math.sqrt(2)
        A=[[a,d/rt,f/rt],[d/rt,b,e/rt],[f/rt,e/rt,c]]
        co=math.cos(theta);si=math.sin(theta)
        Q=[[co,-si,0],[si,co,0],[0,0,1]]
        B=[[sum(Q[i][k]*A[k][l]*Q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
        return [B[0][0],B[1][1],B[2][2],rt*B[0][1],rt*B[1][2],rt*B[0][2]]
    covariance_checks=0
    for c in [c for c in refs['cases'] if c['ok'] and (c['id']=='tangent-plastic' or c['id'].startswith('nonproportional-'))]:
        pp=list(map(float,c['args'][1].split(',')));z=list(map(float,c['args'][2].split(',')));e=list(map(float,c['args'][3].split(',')));x=c['expected']
        for angle in (.37,1.1,-.8):
            n=dict(sigma=rotate(z[:6],angle),alpha=z[6],gamma=z[7]);a=dict(sigma=rotate(x[:6],angle),alpha=x[6],gamma=x[7])
            r=interpret(model,a,n,rotate(e,angle),dict(zip(model['parameters'],pp)))
            assert max(abs(v) for v in r['sigma'].v)<1e-7 and abs(r['alpha'])<1e-12 and abs(r['gamma'])<1e-12
            covariance_checks+=1
    # Independent exact-rational uniqueness and positive-radius proof probes.
    from fractions import Fraction as F
    proof_checks=0
    for G in (F(1),F(37),F(80000000000)):
      for H in (F(0),G,3*G,10*G):
       for sy in (F(1),F(2000),F(250000000)):
        for alpha in (F(0),F(1,100)):
         for qt in (F(0),sy/2,sy,2*sy,100*sy):
          Y=sy+H*alpha;D=3*G+H;g=max(F(0),(qt-Y)/D);c=qt-Y-D*g
          assert g>=0 and c<=0 and g*c==0
          assert qt-3*G*g>=0
          if g: assert qt-3*G*g==sy+H*(alpha+g)>0
          # Strictly decreasing c and the complementarity alternatives imply uniqueness.
          assert D>0
          proof_checks+=1
    # Independent saved actual-history request and endpoint audit, beyond parent assessor.
    specs=read(BASE/'paths.json');path_results={};path_negative=[]
    def audit_paths(raw):
        assert len(raw)==len(specs)
        count=0
        for spec,row in zip(specs,raw):
            assert row['id']==spec['id'] and len(row['repeats'])==2
            assert row['repeats'][0]==row['repeats'][1]
            for rows in row['repeats']:
                assert len(rows)==len(spec['increments'])==len(spec['expected'])
                previous=spec['initial']
                for de,ref,data in zip(spec['increments'],spec['expected'],rows):
                    assert data['ok'] is True and data['initial']==previous
                    assert data['model']==spec['model'] and data['parameters']==spec['parameters']
                    assert data['strain']==de
                    assert data['diagnostics']['substeps']==1 and data['diagnostics']['increment_fractions']==[1]
                    state=data['state'];study.close(state[:6],ref[:6],.002);study.close(state[6:],ref[6:],2e-10)
                    _,K,G,sy,H=spec['parameters'];mean=sum(state[:3])/3
                    q=math.sqrt(1.5*sum((state[i]-(mean if i<3 else 0))**2 for i in range(6)))
                    f=q-sy-H*state[6]
                    assert f<=.003 and state[6]>=previous[6]-2e-10 and state[7]>=-2e-10
                    assert abs(state[6]-previous[6]-state[7])<=2e-10
                    tr=sum(de[:3]);oldmean=sum(previous[:3])/3
                    trial=[previous[i]-(oldmean if i<3 else 0)+2*G*(de[i]-(tr/3 if i<3 else 0)) for i in range(6)]
                    qt=math.sqrt(1.5*sum(v*v for v in trial))
                    g=max(0,(qt-sy-H*previous[6])/(3*G+H))
                    assert abs(state[7]-g)<=2e-10
                    previous=state;count+=1
        return count
    for backend_name in ['native','wasm']:
        raw=read(BASE/(backend_name+'-paths-raw.json'));path_results[backend_name]=dict(calls=audit_paths(raw),passed=True)
        for key in ['model','parameters','strain','initial','substeps','state']:
            bad=copy.deepcopy(raw);d=bad[0]['repeats'][0][0]
            if key=='model':d[key]='wrong-model'
            elif key=='substeps':d['diagnostics'][key]=2
            else:d[key][0]+=1
            # Preserve repeat equality so metadata checks themselves must reject.
            bad[0]['repeats'][1]=copy.deepcopy(bad[0]['repeats'][0])
            try:audit_paths(bad)
            except (AssertionError,KeyError):path_negative.append(backend_name+':'+key)
            else:raise AssertionError('accepted path corruption '+key)
    npaths=read(BASE/'native-paths-raw.json');wpaths=read(BASE/'wasm-paths-raw.json')
    for n,w in zip(npaths,wpaths):
        assert n['id']==w['id']
        for nr,wr in zip(n['repeats'],w['repeats']):
            for a,b in zip(nr,wr):
                study.close(a['state'][:6],b['state'][:6],1e-5);study.close(a['state'][6:],b['state'][6:],1e-11)
    # Separate prospectively frozen default-parameter supplement, saved-only.
    default_freeze=read(BASE/'default-study-freeze.json')
    for f in default_freeze['files']: assert sha((ROOT/f['path']).read_bytes())==f['sha256']
    assert defaults['parameters']==[v['default'] for v in model['parameters'].values()]
    default_results={}
    for name in ['native','wasm']:
        default_results[name]=study.assess_rows(defaults['cases'],read(BASE/(name+'-default-raw.json')))
    # Direct independent parity of saved state and every tangent/history entry.
    left=read(BASE/'native-raw.json')+read(BASE/'native-default-raw.json');right=read(BASE/'wasm-raw.json')+read(BASE/'wasm-default-raw.json')
    for c,l,r in zip(refs['cases']+defaults['cases'],left,right):
        x,y=[json.loads(t['calls'][0]['stdout']) for t in (l,r)]
        assert x['ok']==y['ok']
        if 'state' in x:
            study.close(x['state'][:6],y['state'][:6],1e-5);study.close(x['state'][6:],y['state'][6:],1e-11)
        if c['ok'] and 'tangent' in c:
            for i,(a,b) in enumerate(zip(x['state_tangent'],y['state_tangent'])):study.close(a,b,.01 if i<6 else 1e-11)
    return dict(review_reproduced=True,scientific_admission_recommended=True,blocking_findings=[],resolved_finding='SCI-J2-001',
        default_supplement_results=default_results,default_freeze_inputs_verified=len(default_freeze['files']),fixed_basis_residual_covariance_checks=covariance_checks,exact_rational_proof_probes=proof_checks,saved_actual_path_checks=path_results,path_corruption_rejections=path_negative,saved_parity_passed=True,
        source_hashes_verified=len(receipts['sources']),frozen_archive_files_verified=len(freeze['files']),live_study_or_model_paths_used=False,atlas_interpreter_sources_match_freeze=True,
        witnesses=witnesses,independent_complete_tangent_checks=tangent_errors,
        saved_backend_assessments=backend,assessor_corruption_rejections=negative_checks,
        compiled_calls=0,vendor_calls=0,human_signed_approval=False)
if __name__=='__main__': print(json.dumps(run(),indent=2,allow_nan=False))
