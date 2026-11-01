"""Assess saved actual published main-atlas browser output; never executes Wasm."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
EXPECTED='302f2adc06d39b634e1865899e24ff088cc32f72'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def result_log(p):return json.loads(p.read_text().split('### Result\n',1)[1].split('\n###',1)[0])
if len(sys.argv)!=2:raise SystemExit('usage: check_live.py EXACT_EXTRACTED_CI_UPLOAD_DIRECTORY')
upload=Path(sys.argv[1]).resolve();observation=result_log(HERE/'browser-live.log');run=json.loads((HERE/'default.json').read_text());identity=observation['identity'];assert identity['release_revision']==EXPECTED
assert run['provenance']==identity and run['result']['ok'] and run['controls']['mode']=='relaxation';assert run['controls']['duration']==8 and run['controls']['samples']==4 and run['controls']['start']==0
assert run['controls']['parameters']==[20e6,8e6,12e6,2] and run['controls']['initial']==[.002,.001,-.001,.0005,-.0004,.0003,5000,-2000,-3000,1000,-500,250]
known={'model_sha256':'eccfeb372810afd81a5e9cddf5d8ac33e2cb5df6921fc88e14e9175c73e50906','review_sha256':'eda7775348b6b5fbd40cfedf2876d1550505f17c83fdd148b83eb153c2d7582c','approval_sha256':'763c29f59b7156094fd15f9edb73b24b2de70c44e748704c8612a5d42170399b','catalogue_hash':'11dd07e8b896a71bdc72ce4ff93aba664916af583c703fd6b8671a0727a6ff6e'}
for k,v in known.items():assert identity[k]==v,k
cases=json.loads((ROOT/'docs/ingestion/sls-comsol63/execution-v1/cases.json').read_text())['cases'];reference=next(c for c in cases if c['id']=='relax-schedule');n=0
assert len(run['result']['points'])==6
for point in run['result']['points']:
 ref=next(p for p in reference['references'] if p['time']==point['time']);assert len(point['state'])==12 and len(point['observables'])==6
 for i,(a,e) in enumerate(zip(point['state'],ref['state'])):assert abs(a-e)<=(3e-8 if i<6 else 1),(point['time'],i);n+=1
 for a,e in zip(point['observables'],ref['stress']):assert abs(a-e)<=1;n+=1
assert len(observation['assets'])==15
for asset in observation['assets']:assert asset['status']==200 and digest(upload/asset['path'])==asset['sha256'],asset['path']
assert json.loads((upload/'engine-sls/identity.json').read_text())==identity
assert observation['table']=={'rows':7,'columns':19} and observation['plots']==3
assert all(x['status']==200 for x in observation['links']) and len(observation['links'])==5
assert observation['layout']==[{'viewport':1280,'width':1280},{'viewport':390,'width':390}]
assert 'Total messages: 0 (Errors: 0, Warnings: 0)' in (HERE/'browser-console.log').read_text()
assessment={'ok':True,'expectedRevision':EXPECTED,'actualBrowser':observation['browser'],'fullStateStressComparisons':n,'exactUploadAssetComparisons':15,'sourceReviewApprovalLinks':5,'all12StateInspectable':True,'cleanConsole':True,'layoutWidths':[1280,390],'uploadDirectory':str(upload)}
(HERE/'assessment.json').write_text(json.dumps(assessment,indent=2)+'\n');print(json.dumps(assessment))
