"""Validate/stage normal-generated GIS2024 v0.3 sources. Never compile or integrate."""
import argparse,gzip,hashlib,json,math,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.model import load
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError

def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pins():
 for name in ['source-pins.json','prospective-freeze.json']:
  for path,expected in read(HERE/name)['files'].items():assert sha(ROOT/path)==expected,path
def named(z):
 assert len(z)==14
 return {'sigma':z[:6],'e':z[6],'h':z[7:13],'Omega':z[13]}
def validate_inputs():
 pins();model=load(HERE/'model.json');bridge=read(HERE/'bridge.json');old=read(ROOT/bridge['legacy_path']);assert sha(ROOT/bridge['legacy_path'])==bridge['legacy_sha256']
 for key in bridge['identical_fields']:assert old[key]==model[key],key
 assert len(old['state'])==len(model['state'])==4
 for a,b in zip(old['state'],model['state']):
  for key in bridge['state_numeric_fields']:assert a[key]==b[key],key
 cross=read(ROOT/bridge['formulation_authority']);assert model['formulation']==cross['formulation']and model['initialization']==cross['initialization']
 assert [{'name':s['name'],'shape':s['shape'],'unit':s['unit'],'semantics':s['semantics']}for s in model['state']]==cross['state_contract']
 policy=read(HERE/'policy.json');ref=read(ROOT/policy['reference']);bycase={c['input']['id']:c for c in ref['cases']}
 for c in ref['cases']:
  for k,budget in policy['reference_budget'].items():assert 0<=c['fine_difference'][k]<=budget/4
 rows=read(HERE/'trajectory-requests.json.gz');assert len(rows)==20 and len({r['id']for r in rows})==20
 expected={(name,t,n)for name in bycase for t,n in [(1e-4,1),(1e-6,1),(1e-8,1),(1e-4,7),(1e-8,7)]};assert {(r['case'],r['tolerance'],r['partitions'])for r in rows}==expected
 for r in rows:
  assert r['model']==model['id']and r['initial']==bycase[r['case']]['input']['initial'];assert len(r['increments'])==3*r['partitions']
  assert r['original_endpoint_indices']==[r['partitions']*j for j in [1,2,3]]
  for key in ['initial','parameters','settings']:
   numbers=list(map(float,r['wire'][key].split(',')));assert [x.hex()for x in numbers]==[float(x).hex()for x in r[key]]
  assert len(r['wire']['increments'])==len(r['increments'])
  for wire,d in zip(r['wire']['increments'],r['increments']):assert [float(x).hex()for x in wire.split(',')]==[float(x).hex()for x in d]and len(d)==6
  assert initialize_state(model,named(r['initial']),dict(zip(model['parameters'],r['parameters'])))['initial']==r['initial']
 assert sum(len(r['increments'])for r in rows)==204
 rejected=[]
 probes=read(HERE/'probes.json')['probes'];assert len(probes)==9
 for p in probes[:5]:
  r=p['request']
  try:initialize_state(model,named(r['initial']),dict(zip(model['parameters'],r['parameters'])))
  except (ValidationError,ValueError,ArithmeticError):rejected.append(p['id'])
  else:raise AssertionError(p['id']+' accepted')
 return {'model':model['id'],'schema_version':'0.3','identical_mathematical_fields':bridge['identical_fields'],'persistent_components':14,'requests_validated':20,'caller_updates_per_backend':204,'initializer_calls_passed':20,'invalid_initializers_rejected':rejected,'api_and_execution_probes_deferred':[p['id']for p in probes[5:]],'stored_reference_adequacy':'passes unchanged per-component fine-difference limits','candidate_integrations':0,'compiled_builds':0,'scientific_admission':False}
def prepare(destination):
 result=validate_inputs();destination.mkdir(parents=True,exist_ok=False)
 for name in read(HERE/'source-pins.json')['files']:
  target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
 target=destination/'models'/f"{result['model']}.json";target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE/'model.json',target)
 generate(destination/'build/generated',[target])
 result['generated']={f.name:sha(f)for f in sorted((destination/'build/generated').iterdir())if f.is_file()};result['staged_source_files']=len(read(HERE/'source-pins.json')['files'])
 (destination/'preflight.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('destination',type=Path);a=ap.parse_args();print(json.dumps(prepare(a.destination),indent=2))
