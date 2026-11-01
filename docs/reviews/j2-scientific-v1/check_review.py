#!/usr/bin/env python3
"""Saved-only independent review; never runs a backend or vendor code."""
import copy, hashlib, importlib.util, json, math, pathlib, sys, tarfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
HERE=pathlib.Path(__file__).resolve().parent
BASE=ROOT/'docs/ingestion/j2-linear-hardening/execution-v1'
sys.path.insert(0,str(ROOT))
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_text())
def run():
    from atlas.model import load, interpret
    modelpath=ROOT/'docs/ingestion/j2-linear-hardening/candidate-v03.json'
    assert sha(modelpath.read_bytes())=='619ea20bf932247962675e56b785398c7457749aafd28e2bcab94ba0dcc24852'
    model=load(modelpath)
    receipts=read(ROOT/'docs/ingestion/j2-linear-hardening/source-receipts.json')
    for r in receipts['sources']: assert sha(pathlib.Path(r['private_path']).read_bytes())==r['sha256']
    freeze=read(BASE/'execution-freeze.json')
    with tarfile.open(BASE/'source-closure.tar.gz') as archive:
        members={m.name.removeprefix('./'):m for m in archive.getmembers() if m.isfile()}
        for f in freeze['files']:
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
        assert max(abs(v) for v in flat)==0
        dep=[de[i]-s[i]/(2*p['G']) for i in range(6)] # trace zero
        work=sum(a*b for a,b in zip(s,dep))
        q=math.sqrt(1.5*sum(v*v for v in s))
        assert g>0 and x['alpha']>=0 and q==p['sigma_y']+p['H']*g
        witnesses.append(dict(branch=label,state=x,residual=flat,plastic_work_Pa=work))
    assert witnesses[1]['plastic_work_Pa']<0
    # Independent projector-form complete 8x6 tangent, no oracle invocation.
    refs=read(BASE/'references.json'); tangent_errors=[]
    for c in refs['cases']:
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
        assert err<1e-7
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
    return dict(review_reproduced=True,scientific_admission_recommended=False,blocking_finding='SCI-J2-001',
        source_hashes_verified=len(receipts['sources']),frozen_archive_files_verified=len(freeze['files']),live_execution_paths_used=False,
        witnesses=witnesses,independent_complete_tangent_checks=tangent_errors,
        saved_backend_assessments=backend,assessor_corruption_rejections=negative_checks,
        compiled_calls=0,vendor_calls=0,human_signed_approval=False)
if __name__=='__main__': print(json.dumps(run(),indent=2,allow_nan=False))
