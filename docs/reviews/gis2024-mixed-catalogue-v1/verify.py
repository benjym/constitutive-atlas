"""Saved-only compatibility replay. No binary, compiler, or constitutive integration."""
import hashlib,importlib.util,json,sys,tarfile,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify():
 for filename in ['prospective-freeze.json','dependencies.json','source-pins.json','manifest.json']:
  data=read(HERE/filename);data=data['files']if filename in ['prospective-freeze.json','manifest.json']else data
  for path,h in data.items():assert sha(ROOT/path)==h,(filename,path)
 current={q.relative_to(ROOT).as_posix():sha(q)for q in (ROOT/'models').glob('*.json')};assert current==read(HERE/'existing-models.json')
 catalogue=read(HERE/'generated-eleven/models.json');assert len(catalogue['models'])==11
 assert sha(HERE/'gis-model.json')==sha(ROOT/'docs/reviews/gis2024-v03-research-freeze-v1/model.json')
 full=mod('saved_mixed_assess',HERE/'assess_all.py');summaries={};results={}
 with tempfile.TemporaryDirectory()as td:
  for backend in ['native','wasm']:
   destination=Path(td)/backend;destination.mkdir()
   with tarfile.open(HERE/(backend+'-gis-evidence.tar.gz'),'r:gz')as archive:
    for member in archive.getmembers():
     path=Path(member.name);assert not path.is_absolute()and '..'not in path.parts and(member.isfile()or member.isdir())
    archive.extractall(destination,filter='data')
   old=full.existing(backend);gis=full.gis(destination);assert old['qualification_pass']and gis['backend_qualification_pass']
   assert {'existing':old,'gis':gis,'compatibility_pass':True}==read(HERE/(backend+'-assessment.json'))
   summaries[backend]={'existing_ten_pass':old['qualification_pass'],'gis_pass':gis['backend_qualification_pass'],'gis_raw_receipts':gis['raw_receipts']};results[backend]=read(destination/'result.json')
  # Original unchanged parity comparator was pinned prospectively as a dependency.
  oldpath=ROOT/'docs/reviews/gis2024-v03-backends-v1';sys.path.insert(0,str(oldpath));parity=mod('saved_mixed_parity',oldpath/'parity.py')
  frozen=ROOT/'docs/reviews/gis2024-v03-research-freeze-v1';load=parity.load
  comparison=parity.compare(results['native'],results['wasm'],load(frozen/'trajectory-requests.json.gz'),load(frozen/'policy.json')['native_wasm_scaled_parity_max']);assert comparison==read(HERE/'parity-assessment.json')
 # Reference evidence remains unchanged; its separate saved-only audit is replayed.
 audit=mod('saved_reference_audit',ROOT/'docs/reviews/gis2024-v03-backends-v1/reference_audit.py')
 # The reference auditor's public entrypoint is audit(), with no ODE execution.
 reference=audit.audit();assert reference==read(HERE/'reference-audit.json')
 return {'compatibility_pass':True,'backends':summaries,'parity':comparison,'scientific_admission':False,'public_installation':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
