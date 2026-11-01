"""Offline closure audit of actual CI/upload/live/browser evidence; no compiled calls."""
from pathlib import Path
import hashlib,json,tarfile,math,subprocess
D=Path(__file__).resolve().parent;ROOT=D.parents[4]
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 p=read(D/'POLICY.json');ci=read(D/'ci-terminal.json');assert ci['headSha']==p['release'] and ci['databaseId']==p['run'] and ci['status']=='completed' and ci['conclusion']=='success'
 assert {j['name']for j in ci['jobs']}==set(p['jobs']) and all(j['conclusion']=='success'for j in ci['jobs'])
 deployment=read(D/'deployment.json');assert deployment['deployment']['sha']==p['release'] and deployment['deployment']['environment']=='github-pages' and deployment['statuses'][0]['state']=='success'
 a=read(D/'upload-acquisition.json');assert a['run']==p['run'] and a['release']==p['release']
 artifact=next(x for x in read(D/'run-artifacts.json')['artifacts']if x['id']==a['artifact_id']);assert artifact['workflow_run']['id']==p['run'] and artifact['workflow_run']['head_sha']==p['release'] and artifact['name']==a['artifact_name']=='github-pages'
 archive=ROOT/a['private_artifact_path'];assert sha(archive.read_bytes())==a['tar_sha256']
 with tarfile.open(archive)as t:
  members=t.getmembers();assert all(m.isfile()or m.isdir()for m in members);assert all(not Path(m.name).is_absolute()and '..'not in Path(m.name).parts for m in members)
  files=[m for m in members if m.isfile()];assert len(files)==len({m.name.removeprefix('./')for m in files});body={m.name.removeprefix('./'):t.extractfile(m).read()for m in files}
 inventory={n:sha(b)for n,b in body.items()};assert inventory==read(D/'upload-inventory.json')
 for name,source in p['source_assets'].items():assert inventory[name]==sha(subprocess.check_output(['git','show',p['release']+':'+source],cwd=ROOT)),name
 assert inventory['models/'+p['model']+'.json']==p['definition_sha256'];assert inventory[p['review_asset']]==p['review_sha256']
 public=json.loads(body['models.json']);assert public['sha256']==p['catalogue_hash'];assert p['model']in[m['id']for m in public['models']]
 evidence=json.loads(body['evidence.json']);review=next(x for x in evidence['agent_reviews']if x['id']==p['review_id']);assert review['definition_current']and review['status']=='accepted'and review['record_sha256']==p['review_sha256'] and review['registered_approval_id']
 live=read(D/'live-assets.json');assert live['run']==p['run'] and live['release']==p['release'] and live['passed'];assert {x['path']for x in live['assets']}==set(p['assets']) and len(live['assets'])==len(p['assets'])
 for row in live['assets']:assert row['status']==200 and row['passed'] and row['expected']==row['observed']==inventory[row['path']]
 reference=ROOT/p['browser_reference'];assert sha(reference.read_bytes())==p['browser_reference_sha256'];ref=read(reference);out=read(D/'browser-export.json');assert out['schema_version']==ref['schema_version'] and out['catalogue_hash']==p['catalogue_hash'] and out['specification']==ref['specification']
 r=out['result'];assert r['ok']and not r['message'] and r['model']==p['model']and r['catalogue_hash']==p['catalogue_hash']and r['parameters']==ref['result']['parameters']and r['initial']==ref['result']['initial']and r['integration_settings']==ref['result']['integration_settings']and r['stress']==ref['result']['stress']and r['pore_pressure']==ref['result']['pore_pressure']and r['loading']==ref['result']['loading']
 assert len(r['points'])==len(ref['result']['points'])==101;count=0;worst=0.
 for actual,expected in zip(r['points'],ref['result']['points']):
  assert set(actual)==set(expected)and actual['control']==expected['control']
  for key in ['state','strain','p','q','q_signed','u']:
   aa=actual[key]if isinstance(actual[key],list)else[actual[key]];bb=expected[key]if isinstance(expected[key],list)else[expected[key]];assert len(aa)==len(bb)
   if key=='state':assert len(aa)==7
   if key=='strain':assert len(aa)==6
   for i,(x,y)in enumerate(zip(aa,bb)):
    if y is None:assert x is None;continue
    assert isinstance(x,(int,float))and math.isfinite(x);floor=1000. if key in ['p','q','q_signed','u']or key=='state'and i<6 else 1.;error=abs(x-y)/max(floor,abs(x),abs(y));assert error<=p['relative_budget'],(key,i,error);count+=1;worst=max(worst,error)
 b=read(D/'browser-state.json');assert b['url'].startswith(p['base_url'])and b['model']==p['model']and b['completed_increments']==100 and b['approved_scope_visible']and b['stress_cycles_disabled']and b['meaningful_plots']and b['reset_recovered'] and b['invalid_recovered'];assert read(D/'browser-console.json')==[]
 return dict(passed=True,release=p['release'],run=p['run'],required_jobs=len(p['jobs']),uploaded_files=len(inventory),live_assets=len(live['assets']),actual_browser_numeric_comparisons=count,worst_relative_error=worst,scope='Illustrative reviewed OCC default only; retained scientific limitations apply')
if __name__=='__main__':print(json.dumps(main(),indent=2))
