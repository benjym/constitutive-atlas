"""Synthetic guard probes only: no compiled module/Wasm executed."""
import json,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT))
from tests.test_maxwell_package import MaxwellPackage,package
rows=[]
for mode in ['widened_registered_approval','rejected_interface_review','outside_build_module_symlink']:
 t=MaxwellPackage();t.setUp()
 try:
  original=Path.read_bytes
  approval=json.loads(original(ROOT/package.APPROVAL));approval['scope']['use']='UNRESTRICTED synthetic mutation';approval['limitations']=[]
  def changed(path):
   data=original(path)
   if mode=='widened_registered_approval':
    if path==ROOT/package.APPROVAL:return package.encoded(approval)
    if path==ROOT/'catalogue/approved-models.json':
     r=json.loads(data);r['models']=[approval if x['id']==approval['id'] else x for x in r['models']];return package.encoded(r)
   if mode=='rejected_interface_review' and path==ROOT/package.INTERFACE_REVIEW:
    r=json.loads(data);r['decision']='rejected';r['unresolved_in_scope_blockers']=['synthetic unresolved blocker'];return package.encoded(r)
   return data
  if mode=='outside_build_module_symlink':
   p=t.build/'maxwell.js';outside=t.base/'outside.mjs';outside.write_bytes(p.read_bytes());p.unlink();p.symlink_to(outside)
  error=None
  with patch.object(Path,'read_bytes',changed):
   try:package.bundle(t.dest,t.build)
   except (ValueError,FileNotFoundError) as e:error=str(e)
  assert error is not None,(mode,'invalid package accepted')
  assert not t.dest.exists(),(mode,'partial output')
  rows.append({'probe':mode,'rejected':True,'reason':error,'destination_absent':True})
 finally:t.doCleanups()
print(json.dumps({'passed':True,'synthetic_only':True,'compiled_calls':0,'builds':0,'probes':rows},indent=2))
