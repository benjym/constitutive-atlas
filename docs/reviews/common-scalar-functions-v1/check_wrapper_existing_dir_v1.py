from pathlib import Path
from unittest.mock import patch
import runpy,sys,subprocess,json
p=Path(__file__).parent;out=p/'wrapper-existing-dir-control-v1';out.mkdir(exist_ok=False);sentinel=out/'retained.txt';sentinel.write_text('pre-existing evidence\n');script=p/'proposed-v4/tools/test_scalar_functions.py';before=sys.argv
try:
 sys.argv=[str(script),'unused','--output-dir',str(out.resolve())]
 with patch.object(subprocess,'run') as child:
  try:runpy.run_path(str(script),run_name='__main__')
  except FileExistsError:pass
  else:raise AssertionError('existing directory accepted')
  child.assert_not_called()
finally:sys.argv=before
assert sentinel.read_text()=='pre-existing evidence\n'
(out/'summary.json').write_text(json.dumps({'status':'passed','existing_directory_rejected':True,'child_calls':0,'prior_evidence_unchanged':True})+'\n')
print('Existing-dir rejection PASS; zero child calls')
