"""Freeze exact sources and independent expectations before compiled observations."""
import datetime,hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def freeze():
 out=HERE/'prospective-freeze.json';assert not out.exists()
 replay=Path('/private/tmp/atlas-det-context-generator-replay-v1');checked=[]
 for p in sorted(replay.rglob('*')):
  if p.is_file():
   name=p.relative_to(replay);assert (HERE/name).read_bytes()==p.read_bytes(),name;checked.append(str(name))
 receipt=HERE/'generator-replay.json';assert not receipt.exists();receipt.write_text(json.dumps({'files_compared':checked,'all_exact':True,'compiled_observations':0},indent=2)+'\n')
 files=[p for p in HERE.rglob('*')if p.is_file()]
 files+=list((ROOT/'atlas').glob('*.py'))+list((ROOT/'atlas/numerics').glob('*.py'))+list((ROOT/'schemas').glob('*.json'))
 files+=[ROOT/'cpp/include/atlas'/name for name in ('tensor.hpp','trace_accuracy.hpp','checked_trace.hpp','checked_expression.hpp','checked_determinant.hpp','expm.hpp','history_runtime.hpp','numerics/determinant.hpp')]
 files+=list((ROOT/'docs/reviews/symmetric-determinant-reference-v1').glob('*'))
 files += [ROOT/'tests/test_determinant_context_study.py',ROOT/'models/barodesy-clay-2017.json']
 pins={str(p.relative_to(ROOT)):sha(p)for p in sorted(set(files))if p.is_file()}
 out.write_text(json.dumps({'version':'determinant-expression-freeze-0.1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compiled_observations_at_freeze':0,'acceptance':'CONTRACT.md: exact status/output/38column AD/transaction/recovery/nativeWasm parity','files':pins},indent=2)+'\n')
 for name,pin in pins.items():
  p=HERE/'frozen'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p);assert sha(p)==pin
 print('frozen',len(pins),'files',sha(out))
if __name__=='__main__':freeze()
