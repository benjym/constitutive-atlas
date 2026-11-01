"""Verify archived raw evidence by replaying frozen assessors; no binaries/ODEs."""
import gzip,hashlib,json,tarfile,tempfile
from pathlib import Path,PurePosixPath
from assess import HERE,ROOT,FROZEN,assess,load
from parity import compare
from reference_audit import audit as reference_audit

def main():
 for receipt in ['execution-freeze.json','parity-freeze.json','manifest.json']:
  for path,expected in load(HERE/receipt)['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
 assert reference_audit()==load(HERE/'reference-audit.json')
 with tempfile.TemporaryDirectory()as directory:
  folders=[]
  for backend in ['native','wasm']:
   target=Path(directory)/backend;target.mkdir();folders.append(target)
   with tarfile.open(HERE/f'{backend}-evidence.tar.gz','r:gz')as archive:
    for member in archive:
     path=PurePosixPath(member.name);assert not path.is_absolute()and'..'not in path.parts and member.isfile()and member.size<=10000000
     destination=target/member.name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(archive.extractfile(member).read())
   report=assess(target);assert report==load(HERE/f'{backend}-assessment.json')==load(target/'assessment.json')
  parity=compare(load(folders[0]/'result.json'),load(folders[1]/'result.json'),load(FROZEN/'trajectory-requests.json.gz'),load(FROZEN/'policy.json')['native_wasm_scaled_parity_max']);assert parity==load(HERE/'parity-assessment.json')
 print(json.dumps({'saved_raw_evidence_integrity':True,'native_qualification_pass':True,'wasm_qualification_pass':True,'native_wasm_parity_pass':True,'new_integrations':0,'new_builds':0,'scientific_admission':False},indent=2))
if __name__=='__main__':main()
