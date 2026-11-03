"""Portable pin-path projection only; no model/runtime imports or evaluation."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,difflib
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'docs/ingestion/vibe-2026/numerical-qualification-v1/plan-v2.json'
SOURCE_SHA='b70950d1981602d9bc053f708214fde7c93efda1dde97420b10295c015d890da'
ROOTS=('/Users/bmar5496/code/constitutive-atlas/','/private/tmp/atlas-vibe2026-controlled-time-v1/')
IDENTITY='vibe2026-backend-qualification-v3-portable-pin-paths'
def projection():
 raw=SOURCE.read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
 old=json.loads(raw);new=deepcopy(old);new['identity']=IDENTITY;changes=[]
 for i,pin in enumerate(new['source_files']):
  original=pin['path']
  if original.startswith('/'):
   matches=[prefix for prefix in ROOTS if original.startswith(prefix)];assert len(matches)==1,original
   pin['path']=original[len(matches[0]):];changes.append(dict(index=i,before=original,after=pin['path']))
  assert not Path(pin['path']).is_absolute() and '..' not in Path(pin['path']).parts
  assert hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],pin['path']
 reverse=deepcopy(new);reverse['identity']=old['identity']
 for delta in changes:reverse['source_files'][delta['index']]['path']=delta['before']
 assert reverse==old
 assert (json.dumps(reverse,indent=2)+'\n').encode()==raw,'Reverse projection must recover exact original bytes'
 return raw,new,dict(original_sha256=SOURCE_SHA,portable_identity=IDENTITY,allowed_changes=['identity','source_files[*].path'],path_changes=changes,case_count=len(old['points']),history_count=len(old['histories']),all_numeric_cases_inputs_settings_bounds_and_input_hashes_unchanged=True,reverse_original_byte_identity=True,compiled_calls=0)
if __name__=='__main__':
 raw,new,proof=projection();target=HERE/'plan-v3.json'
 with target.open('x') as f:json.dump(new,f,indent=2);f.write('\n')
 proof['portable_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
 with (HERE/'portable-plan-proof.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
 with (HERE/'portable-plan.diff').open('x') as f:f.write(''.join(difflib.unified_diff(raw.decode().splitlines(True),target.read_text().splitlines(True),fromfile='plan-v2.json',tofile='plan-v3.json')))
 print('Portable plan:',len(proof['path_changes']),'pin paths; identity-only other delta; exact reversal;0compiledcalls')
