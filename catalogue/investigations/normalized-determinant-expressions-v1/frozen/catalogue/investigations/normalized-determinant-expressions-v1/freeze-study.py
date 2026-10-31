"""Freeze cache-free source closure and independent expectations before execution."""
import datetime,hashlib,json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT))
from atlas.evidence_sources import selected_files
SUFFIXES={'.py','.hpp','.cpp','.md','.json','.txt','.mjs','.tsv'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def freeze():
 out=HERE/'prospective-freeze.json';assert not out.exists()and not(HERE/'frozen').exists()
 replay=Path('/private/tmp/atlas-normalized-det-context-generator-replay-v1');checked=[]
 for p in selected_files(replay,SUFFIXES):
  name=p.relative_to(replay);assert (HERE/name).read_bytes()==p.read_bytes(),name;checked.append(str(name))
 assert checked
 receipt=HERE/'generator-replay.json';assert not receipt.exists();receipt.write_text(json.dumps({'files_compared':checked,'all_exact':True,'compiled_observations':0},indent=2)+'\n')
 files=set(selected_files(HERE,SUFFIXES))
 files.update(selected_files(ROOT/'atlas',{'.py'}));files.update(selected_files(ROOT/'schemas',{'.json'}));files.update(selected_files(ROOT/'cpp/include/atlas',{'.hpp'}))
 files.update(selected_files(ROOT/'docs/reviews/normalized-determinant-reference-v1',SUFFIXES))
 files.update(ROOT/p for p in ('docs/NORMALIZED_DETERMINANT.md','docs/EVIDENCE_FREEZES.md','tests/test_normalized_determinant_context_study.py','tests/test_normalized_determinant_dsl.py','tests/test_evidence_sources.py','models/barodesy-clay-2017.json'))
 pins={str(p.relative_to(ROOT)):sha(p)for p in sorted(files)}
 assert not any('__pycache__'in name or name.endswith(('.pyc','.pyo'))for name in pins)
 out.write_text(json.dumps({'version':'normalized-determinant-expression-freeze-v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiled_observations_at_freeze':0,'acceptance':'CONTRACT.md: exact status/output/38column AD/transaction/recovery/nativeWasm parity','files':pins,'cache_or_bytecode_included':False},indent=2)+'\n')
 for name,pin in pins.items():
  p=HERE/'frozen'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p);assert sha(p)==pin
 print('frozen',len(pins),'files',sha(out))
if __name__=='__main__':freeze()
