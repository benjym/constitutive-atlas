"""Verify the ninth-draft production identities and retained checks, without builds."""
from pathlib import Path
import datetime,hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
read=lambda p:json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 for name,pin in read(HERE/'evidence-manifest.json').items():assert sha(HERE/name)==pin,name
 for name,pin in read(HERE/'integration-inputs.json')['source_files'].items():assert sha(ROOT/name)==pin,name
 for name,pin in read(HERE/'prior-models.json').items():assert sha(ROOT/name)==pin,name
 study=ROOT/'catalogue/investigations/clay2005-preview-v1'
 for p in(study/'models').glob('*.json'):assert p.read_bytes()==(ROOT/'models'/p.name).read_bytes(),p.name
 builds={role:read(HERE/(role+'-build.json'))for role in('native','wasm')}
 assert datetime.datetime.fromisoformat(builds['native']['finished_utc'])<=datetime.datetime.fromisoformat(builds['wasm']['started_utc'])
 for role,build in builds.items():
  assert build['input_pins_sha256']==sha(HERE/'integration-inputs.json')and build['exact_frozen_generated_declarations']is True
  for name,artifact in build['artifacts'].items():assert sha(Path(artifact['path']))==artifact['sha256'],name
  for cmd in build['commands']:assert sha(HERE/cmd['path'])==cmd['sha256']and read(HERE/cmd['path'])['returncode']==0
  final=read(HERE/build['commands'][-1]['path']);assert final['argv'][-4:]==['--target','atlas_solver','--parallel','1']and final['EMCC_CORES']=='1'
  config=read(HERE/(role+'-configuration.json'));assert config['build_sha256']==sha(HERE/(role+'-build.json'))
  for name,pin in config['files'].items():assert sha(HERE/name)==pin
  work=Path(next(iter(build['artifacts'].values()))['path']).parent
  for name in('models.hpp','models.json'):assert(work/'generated'/name).read_bytes()==(study/'generated'/name).read_bytes()
 checks=read(HERE/'production-checks.json');assert all(c['returncode']==0 for c in checks['checks']);assert 'passed for 45 model/protocol combinations'in checks['checks'][0]['stdout'];assert checks['skipped_native_fixture_tests']==3
 assert read(HERE/'browser-comparison.json')['pass']is True
 sys.path.insert(0,str(study))
 try:
  from assess import physical
  current=read(HERE/'browser-export.json');frozen=read(study/'browser/export.json');assert current['specification']==frozen['specification']and physical(current['result'],'run')==physical(frozen['result'],'run')
 finally:sys.path.remove(str(study))
 package=read(HERE/'package.json');assert package['catalogue_sha256']==sha(ROOT/'catalogue/manifest.json')
 for name,pin in package['files'].items():assert sha(Path(package['path'])/name)==pin,name
 from atlas.evidence import checked_receipt
 archive=read(HERE/'historical-catalogue-archive.json');checked_receipt(ROOT,str((HERE/'historical-catalogue-archive.json').relative_to(ROOT)),'catalogue/manifest.json',archive['sha256'])
 return {'pass':True,'local_models':9,'production_protocol_pairs':45,'exact_browser_channels':True,'compiled_execution':False,'scientific_admission':False,'deployment':False}
if __name__=='__main__':
 sys.path.insert(0,str(ROOT));print(json.dumps(verify(),indent=2))
