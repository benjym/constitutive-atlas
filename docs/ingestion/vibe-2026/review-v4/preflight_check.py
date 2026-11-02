"""Pure source/request/profile checks; no backend execution or files outside review output."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[4];W=Path('/private/tmp/atlas-vibe2026-controlled-time-v1');P='docs/ingestion/vibe-2026/'
sys.path.insert(0,str(W))
from atlas.controlled_time import validate_request,identity
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 modelpath=W/'models/research/vibe/vibe-2026-explicit-appendix-a.json';m=json.loads(modelpath.read_text());assert sha(modelpath)=='a7d3f0f61ff6654f1dc924178a3551a740ca39212a99813c2b9ce5c15b16c987'
 previous=W/P/'candidate-v1/preimages/29d104bf55ec3225030e8710ee342f96b6518bd8a4434e784e455da300d08778-vibe-2026-explicit-appendix-a.json';old=json.loads(previous.read_text());assert sha(previous)=='29d104bf55ec3225030e8710ee342f96b6518bd8a4434e784e455da300d08778'
 assert [n for n in m if m[n]!=old[n]]==['description'];assert {n:v for n,v in m.items() if n!='description'}=={n:v for n,v in old.items() if n!='description'}
 manifests=[]
 for relative in ['public-examples-v1/manifest.json','profile-v1/manifest.json','profile-v1/manifest-v2.json','mainatlas-implementation-v1/source-manifest-v3.json']:
  p=W/P/relative;manifest=json.loads(p.read_text())
  for row in manifest['files']:assert sha(W/row['path'])==row['sha256'],row['path']
  manifests.append(dict(path=str(p),sha256=sha(p),files=len(manifest['files'])))
 examples=json.loads((W/P/'public-examples-v1/examples.json').read_text());bindings=json.loads((W/P/'public-examples-v1/reference-bindings.json').read_text());assert len(examples)==len(bindings)==8
 histories=[]
 for e,b in zip(examples,bindings):
  assert e['id']==b['id'];validate_request(m,e['request']);ref=R/b['reference_path'];assert sha(ref)==b['reference_sha256'];v=json.loads(ref.read_text());r=next(x['result'] for x in v['runs'] if x['status']=='pass' and x['result']['precision']==70 and x['result']['partitions']==256)
  q=e['request'];z=q['context']['state'];assert [*z['sigma_net'],z['e'],z['a_scan']]==list(map(float,r['initial_state']));assert q['context']['model_sha256']==identity(m);assert sum(s['duration'] for s in q['segments'])==float(r['duration_s']);assert q['segments'][-1]['controls_end']['suction']==float(r['endpoint_suction_Pa']);assert q['segments'][-1]['controls_end']['temperature']==float(r['endpoint_temperature_K']);assert all(s['samples']>=10 for s in q['segments'])
  assert q['context']['parameters']=={n:p['default'] for n,p in m['parameters'].items()};histories.append(dict(id=e['id'],output_intervals=sum(s['samples'] for s in q['segments']),reference_sha256=sha(ref),initial_pressure_Pa=z['sigma_net'][0]))
 assert all(q['context']['control_rates']==dict(strain=[0.]*6,suction=0.,temperature=0.) for q in [e['request'] for e in examples])
 profile=json.loads((W/P/'profile-v1/profile-data-v2.json').read_text());assert len(profile['parameters'])==30;assert set(x['name'] for x in profile['parameters'])==set(m['parameters']);assert all(all(x.get(k) for k in ['name','symbol','meaning','help','unit']) for x in profile['parameters']);assert next(x for x in profile['parameters'] if x['name']=='phi')['unit']=='rad'
 v2=json.loads((W/P/'mainatlas-implementation-v1/source-manifest-v2.json').read_text());v3=json.loads((W/P/'mainatlas-implementation-v1/source-manifest-v3.json').read_text());changes=[a['path'] for a in v2['files'] if next(b for b in v3['files'] if a['path']==b['path'])['sha256']!=a['sha256']];assert changes==['web/controlled-time-laboratory.mjs'];recovered=[]
 for row in v2['files']:
  candidates=[W/row['path'],W/P/'mainatlas-implementation-v1/preimages/source-freeze-v2'/row['path']];matches=[str(p) for p in candidates if p.is_file() and sha(p)==row['sha256']];assert matches;recovered.append(matches[0])
 print(json.dumps(dict(candidate_description_only=True,constitutive_payload_unchanged=True,manifests=manifests,public_histories=histories,profile_parameter_count=30,ui_only_changed_files=changes,prior_ui_source_recovery=recovered,compiled_execution=False),indent=2))
if __name__=='__main__':main()
