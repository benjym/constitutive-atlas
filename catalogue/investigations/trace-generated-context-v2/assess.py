"""Assess frozen generated-context evidence without executing artifacts."""
from pathlib import Path
import hashlib,json
from atlas.evidence import checked_receipt
ROOT=Path(__file__).resolve().parents[3]
STUDY=Path(__file__).resolve().parent
REL=STUDY.relative_to(ROOT).as_posix()
def assess():
 protocol=json.loads((STUDY/'protocol.json').read_text())
 freeze=json.loads((STUDY/'prospective-freeze.json').read_text())
 for name,pin in freeze['files'].items():
  if hashlib.sha256((STUDY/name).read_bytes()).hexdigest()!=pin:raise ValueError('changed prospective document:'+name)
 for name,pin in protocol['inputs'].items():checked_receipt(ROOT,REL+'/protocol.json',name,pin)
 expected={'version':'trace-generated-context-observations-v1','material':json.loads((STUDY/'expected.json').read_text()),'history':json.loads((STUDY/'history-expected.json').read_text())}
 results={};errors=[];observations={}
 for backend in ['native','wasm']:
  directory=STUDY/backend;receipt=json.loads((directory/'receipt.json').read_text())
  if receipt['inputs']!=protocol['inputs']:raise ValueError('wrong source receipt:'+backend)
  if [x['label']for x in receipt['commands']]!=['configure','build','observe'] or any(x['exit_code']!=0 for x in receipt['commands']):raise ValueError('incomplete or failed commands:'+backend)
  if (directory/'observe.stderr.txt').read_bytes():raise ValueError('observation stderr:'+backend)
  actual=json.loads((directory/'observe.stdout.txt').read_text());observations[backend]=actual
  missing=set(expected)-set(actual)
  mismatches=[]
  if missing or set(actual)!=set(expected) or actual.get('version')!=expected['version']:mismatches.append('root shape/version')
  for family in ['material','history']:
   got=actual.get(family,[]);want=expected[family]
   if len(got)!=len(want):mismatches.append(family+': count')
   for i,(a,b)in enumerate(zip(got,want)):
    if a!=b:mismatches.append(family+':'+str(i)+':'+b['id'])
  results[backend]={'material_rows':len(actual.get('material',[])),'history_rows':len(actual.get('history',[])),'mismatches':mismatches,'pass':not mismatches}
  errors.extend(backend+':'+x for x in mismatches)
 parity=observations['native']==observations['wasm']
 if not parity:errors.append('native/Wasm semantic/bit parity')
 return {'version':'trace-generated-context-assessment-v1','backends':results,'native_wasm_bit_parity':parity,'pass':not errors,'errors':errors,'scope':'generated expression/Jet/history contexts; no constitutive, finite solver, material AD or scientific admission'}
if __name__=='__main__':
 result=assess();print(json.dumps(result,indent=2));raise SystemExit(0 if result['pass']else 1)
