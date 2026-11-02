"""Read saved dependency files only; all child-process execution prohibited."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess
from unittest.mock import patch
H=Path(__file__).resolve().parent;R=H.parents[3];B=Path('/private/tmp/atlas-time-profile-v2/build-time-v2');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=load('v1',R/'tools/record_cmake_profile_build.py');new=load('v2',H/'candidates/tools/record_cmake_profile_build_v2.py');rows=[];calls=[]
def blocked(*a,**k):calls.append(1);raise AssertionError('No process/compiler/tool/material calls permitted')
patches=[patch.object(owner,name,blocked) for owner,name in [(subprocess,'Popen'),(subprocess,'run'),(subprocess,'check_call'),(subprocess,'check_output'),(os,'system'),(os,'posix_spawn')]]
for p in patches:p.start()
try:
 for target in ['atlas_schedule_predictor_tests','atlas_time_tests','atlas_time_solver']:
  ds=list((B/'CMakeFiles'/(target+'.dir')).rglob('*.o.d'));assert len(ds)==1;d=ds[0];obj=Path(str(d)[:-2]);old_error=None
  try:old.dependencies(d,B,obj)
  except ValueError as e:old_error=str(e)
  assert old_error=='Duplicate dependency member',old_error
  identity={};paths=new.dependencies(d,B,obj,identity);v=identity[str(d)];assert len(v['canonical_alias_groups'])==1;assert len(v['ordered_members'])==len(paths)+1
  copy=H/'saved-depfiles'/target/d.name;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(d.read_bytes())
  rows.append({'target':target,'source':str(d),'raw_depfile_sha256':sha(d),'saved_copy':copy.relative_to(H).as_posix(),'old_v1_error':old_error,'lexical_tokens':len(v['ordered_members']),'canonical_files':len(paths),'identity':v})
finally:
 for p in reversed(patches):p.stop()
assert not calls
report={'passed':True,'scope':'Local retained depfiles corroborate the CI duplicate failure. Exact failing CI depfile/header alias evidence has not been acquired; no assertion about its precise tokens. No new compilation or engine call.','depfiles':rows,'compiler_tool_material_calls':0}
(H/'SAVED-DEPFILE-PROOF.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'targets':[{k:v for k,v in r.items() if k!='identity'} for r in rows]},indent=2))
