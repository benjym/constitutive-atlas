"""Synthetic subprocess controls; no compiled execution or scalar observations."""
from pathlib import Path
from unittest.mock import patch
import runpy,subprocess,sys,tempfile,json
p=Path(__file__).parent;out=p/'wrapper-controls-v1';assert not out.exists();out.mkdir();script=p/'proposed-v4/tools/test_scalar_functions.py';results=[]
for name,fail_at,keep in [('collector-failure',1,False),('assessor-failure',2,False),('successful-temporary',0,False),('successful-explicit',0,True)]:
 d=(out/name).resolve();calls=[]
 def mkdir(**kw):d.mkdir();return str(d)
 def run(cmd,**kw):
  calls.append(cmd);target=Path(cmd[-1]);target.write_text(json.dumps({'synthetic_control_only':True,'call':len(calls)})+'\n')
  if len(calls)==fail_at:raise subprocess.CalledProcessError(1,cmd)
  return subprocess.CompletedProcess(cmd,0)
 argv=[str(script),'synthetic-unused-library']+(['--output-dir',str(d)] if keep else []);before=sys.argv;failed=False
 try:
  sys.argv=argv
  with patch.object(tempfile,'mkdtemp',side_effect=mkdir),patch.object(subprocess,'run',side_effect=run):
   try:runpy.run_path(str(script),run_name='__main__')
   except subprocess.CalledProcessError:failed=True
 finally:sys.argv=before
 assert failed==bool(fail_at);assert d.exists()==bool(fail_at or keep);assert len(calls)==(fail_at or 2)
 if d.exists():assert (d/'raw.json').exists()
 results.append(dict(control=name,passed=True,failed_as_expected=failed,evidence_retained=d.exists()))
(out/'summary.json').write_text(json.dumps({'scope':'Wrapper software controls only; mocked child calls, no compiled execution','controls':results},indent=2)+'\n');print('4wrapperretention controls PASS')
