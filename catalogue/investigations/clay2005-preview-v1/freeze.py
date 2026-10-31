"""Prospective cache-free freeze after references and structural checks, before builds."""
import datetime,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT))
from atlas.evidence_sources import selected_files
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def freeze():
 assert not(HERE/'manifest.json').exists()and not(HERE/'native').exists()and not(HERE/'wasm').exists()
 assert (HERE/'reference/references.json').exists()and(HERE/'isotropic_adapter.py').exists()
 for name,pin in json.loads((HERE/'input-pins.json').read_text()).items():assert sha(ROOT/name)==sha(HERE/'frozen'/name)==pin,name
 files=selected_files(HERE,{'.py','.hpp','.cpp','.mjs','.md','.txt','.json'})
 pins={str(p.relative_to(HERE)):sha(p)for p in files}
 (HERE/'manifest.json').write_text(json.dumps(pins,indent=2)+'\n')
 (HERE/'prospective-freeze.json').write_text(json.dumps({'version':'clay2005-preview-prospective-freeze-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiled_observations_at_freeze':0,'manifest_sha256':sha(HERE/'manifest.json'),'files':len(pins),'models':9,'requests_per_backend':27,'cache_or_bytecode_included':False},indent=2)+'\n')
 print('frozen',len(pins),'files',sha(HERE/'manifest.json'))
if __name__=='__main__':freeze()
