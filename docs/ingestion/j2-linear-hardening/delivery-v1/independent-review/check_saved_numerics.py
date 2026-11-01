#!/usr/bin/env python3
"""Saved-only delivery numerical review; no native/Wasm/browser execution."""
import copy,hashlib,json,math,pathlib,sys,tarfile,types
ROOT=pathlib.Path(__file__).resolve().parents[5]
BASE=ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1';OLD=BASE.parent/'execution-v2';HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from check_preset import run as exact_preset

def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def run():
    freeze=read(BASE/'execution-freeze.json')
    assert freeze['compiled_observations_before_freeze']==0
    assert sha((BASE/'source-closure.tar.gz').read_bytes())==freeze['archive_sha256']
    with tarfile.open(BASE/'source-closure.tar.gz') as archive:
        files={x.name.removeprefix('./'):x for x in archive.getmembers() if x.isfile()}
        for f in freeze['files']:
            matches=[m for n,m in files.items() if n==f['path'] or n.endswith('/'+f['path'])]
            assert len(matches)==1,f['path']
            assert sha(archive.extractfile(matches[0]).read())==f['sha256'],f['path']
    # Bind every historical reference/assessor source actually consumed below.
    approval=read(ROOT/'docs/admission/j2-approved-v2/approval.json')
    reviewpath=ROOT/approval['review']['path']
    assert sha(reviewpath.read_bytes())==approval['review']['sha256']
    accepted=read(reviewpath);pins={x['path']:x['sha256'] for x in accepted['artifacts']}
    for name in ['source-closure.tar.gz','references.json','default-references.json','paths.json']:
        path=OLD/name;assert sha(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    # Read the original frozen analytical assessor as Python source, never launch its CLI.
    study=types.ModuleType('frozen_j2_study');study.__file__=str(ROOT/'tools/study_j2.py')
    with tarfile.open(OLD/'source-closure.tar.gz') as archive:
        exec(compile(archive.extractfile('tools/study_j2.py').read(),study.__file__,'exec'),study.__dict__)
    expectedmodel='a28068cbb8cfc660e49eb648d6ce7fcbf993ea50b45e8eb0d325c6b75f4ffc3b'
    assert sha((ROOT/'models/research/j2/j2-linear-isotropic-hardening-be.json').read_bytes())==expectedmodel
    reports={};raw={};mutations=[]
    for label,name in [('main','references.json'),('defaults','default-references.json')]:
        cases=read(OLD/name)['cases'];raw[label]={}
        for backend,path in [('native',BASE/'native'/(label+'-raw.json')),('wasm',BASE/('wasm-'+label+'-raw.json'))]:
            rows=read(path);raw[label][backend]=rows
            reports[backend+'-'+label]=study.assess_rows(cases,rows)
            for kind in ['stress','history','tangent','request','rollback']:
                bad=copy.deepcopy(rows);idx=0
                if kind=='tangent':idx=next(i for i,c in enumerate(cases) if 'tangent' in c)
                if kind=='rollback':
                    matches=[i for i,c in enumerate(cases) if c['id']=='budget-rollback']
                    if not matches:continue
                    idx=matches[0]
                data=json.loads(bad[idx]['calls'][0]['stdout'])
                if kind=='stress':data['state'][0]+=1
                if kind=='history':data['state'][6]+=.01
                if kind=='tangent':data['state_tangent'][7][0]+=.01
                if kind=='request':data['strain'][0]+=.01
                if kind=='rollback':data['state'][7]+=1
                bad[idx]['calls'][0]['stdout']=json.dumps(data)
                try:study.assess_rows(cases,bad)
                except (AssertionError,KeyError):mutations.append(backend+':'+label+':'+kind)
                else:raise AssertionError('accepted corrupted saved output')
        for c,n,w in zip(cases,raw[label]['native'],raw[label]['wasm']):
            n,w=[json.loads(x['calls'][0]['stdout']) for x in (n,w)];assert n['ok']==w['ok']
            if 'state' in n:
                study.close(n['state'][:6],w['state'][:6],1e-5);study.close(n['state'][6:],w['state'][6:],1e-11)
            if c['ok'] and 'tangent' in c:
                for i,(a,b) in enumerate(zip(n['state_tangent'],w['state_tangent'])):study.close(a,b,.01 if i<6 else 1e-11)
    preset=read(BASE/'preset-references.json');exact=exact_preset()
    assert preset['parameters']==exact['parameters'] and preset['initial']==exact['initial']
    assert preset['increments']==[r['increment'] for r in exact['rows']]
    for ref,row in zip(preset['expected'],exact['rows']):
        study.close(ref[:6],row['state'][:6],.002);study.close(ref[6:],row['state'][6:],2e-10)
    specs=read(OLD/'paths.json')+[preset];pathreports={};pathraw={}
    for backend,path in [('native',BASE/'native/paths-raw.json'),('wasm',BASE/'wasm-paths-raw.json')]:
        rows=read(path);pathraw[backend]=rows;assert len(rows)==len(specs);count=0;maxstress=maxhistory=0.
        for spec,row in zip(specs,rows):
            assert row['id']==spec['id'] and len(row['repeats'])==2 and row['repeats'][0]==row['repeats'][1]
            for repeat in row['repeats']:
                assert len(repeat)==len(spec['increments'])==len(spec['expected']);previous=spec['initial']
                for step,(increment,ref,data) in enumerate(zip(spec['increments'],spec['expected'],repeat)):
                    assert data['ok'] is True and data['initial']==previous
                    assert data['model']==spec['model'] and data['parameters']==spec['parameters'] and data['strain']==increment
                    assert data['diagnostics']['substeps']==1 and data['diagnostics']['increment_fractions']==[1]
                    maxstress=max(maxstress,study.close(data['state'][:6],ref[:6],.002));maxhistory=max(maxhistory,study.close(data['state'][6:],ref[6:],2e-10))
                    if spec['id']=='public-preset':
                        exactref=exact['rows'][step]['state']
                        study.close(data['state'][:6],exactref[:6],.002);study.close(data['state'][6:],exactref[6:],2e-10)
                    p=data['parameters'];s=data['state'];mean=sum(s[:3])/3
                    q=math.sqrt(1.5*sum((s[i]-(mean if i<3 else 0))**2 for i in range(6)))
                    assert q-p[3]-p[4]*s[6]<=.003 and s[6]>=previous[6]-2e-10 and s[7]>=-2e-10
                    assert abs(s[6]-previous[6]-s[7])<=2e-10
                    previous=s;count+=1
        pathreports[backend]=dict(calls=count,max_stress_error_Pa=maxstress,max_history_error=maxhistory)
    for n,w in zip(pathraw['native'],pathraw['wasm']):
        for nr,wr in zip(n['repeats'],w['repeats']):
            for a,b in zip(nr,wr):
                study.close(a['state'][:6],b['state'][:6],1e-5);study.close(a['state'][6:],b['state'][6:],1e-11)
    package=read(BASE/'package-report.json')
    assert package['passed'] and package['calls']==327 and package['stateComparisons']==1264 and package['tangentComparisons']==192
    assert package['identity']['model_sha256']==expectedmodel
    return dict(passed=True,source_archive_files=len(freeze['files']),source_archive_sha256=freeze['archive_sha256'],main_and_defaults=reports,paths_and_independent_exact_preset=pathreports,saved_native_wasm_parity=True,assessor_corruption_rejections=mutations,package_report=package,compiled_calls_by_reviewer=0,limitations=['Saved package summary accepted provisionally; final executed-loader and copied asset identity/UI evidence remain separately pending.'])
if __name__=='__main__':print(json.dumps(run(),indent=2))
