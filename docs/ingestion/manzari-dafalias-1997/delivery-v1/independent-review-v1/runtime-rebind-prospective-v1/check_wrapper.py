import hashlib,json,runpy,subprocess,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1];R=P/'runtime-rebind-v1';sys.path.insert(0,str(R));h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();results=[]
for code in [0,1]:
 out=D/('mock-delegate-'+str(code));commands=[]
 def fake(cmd,**kwargs):
  commands.append(cmd);out.mkdir();(out/'report.json').write_text(json.dumps({'synthetic':True,'status':'passed' if code==0 else 'failed'})+'\n');return subprocess.CompletedProcess(cmd,code)
 with patch.object(sys,'argv',[str(R/'run_md.py'),'--solver',str(R/'README.md'),'--output',str(out),'--case','synthetic-case']),patch('subprocess.run',fake):
  try:runpy.run_path(str(R/'run_md.py'),run_name='__main__')
  except SystemExit as ex:assert ex.code==code
 binding=json.loads((out/'runtime-binding.json').read_text());assert binding['delegate_returncode']==code and binding['report_sha256']==h(out/'report.json') and binding['artifact_sha256']==h(R/'README.md') and binding['delegate_command']==commands[0] and binding['subset']==['synthetic-case'] and commands[0][-2:]==['--case','synthetic-case']
 results.append({'delegate_exit':code,'wrapper_exit_preserved':True,'raw_report_bound':True,'subset_explicit':True})
assert json.loads((D/'reproduced-comparisons.json').read_text())==json.loads((R/'comparisons.json').read_text())
(D/'wrapper-checks.json').write_text(json.dumps({'compiled_calls':0,'results':results,'saved_comparisons_exactly_reproduced':True},indent=2)+'\n')
