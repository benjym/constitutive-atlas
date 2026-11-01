from pathlib import Path
import json,runpy,io,hashlib
from unittest.mock import patch
from types import SimpleNamespace
D=Path(__file__).resolve().parent;P=D.parents[1];m=runpy.run_path(str(P/'execution-v3/run_native.py'));results=[]
req={'mode':'integrate','model':'synthetic','parameters':[1.],'initial':[1.],'settings':[1.],'strain':[0.]*6}
for token in ['NaN','Infinity','-Infinity','1e999','1e100']:
 b=m['Backend'](SimpleNamespace(wasm_engine=None,solver='SYNTHETIC-NOT-EXECUTED'),D);log=io.StringIO();error=None;r=None;raw='{"ok":false,"state":['+token+']}'
 with patch('subprocess.run',return_value=SimpleNamespace(stdout=raw,stderr='',returncode=1)):
  try:r=b.call(req,log)
  except Exception as ex:error=repr(ex)
 retained=json.loads(log.getvalue())['raw_stdout']==raw if log.getvalue() else False
 results.append({'token':token,'raw_retained':retained,'uncaught_exception':error,'normalized_response':r})
assert all(x['raw_retained'] and x['uncaught_exception'] is None for x in results)
assert all(x['normalized_response'].get('harness_error') for x in results if x['token']!='1e100')
(D/'transport-v3-checks.json').write_text(json.dumps({'scope':'mocked subprocess only, no executable invoked','transport_sha256':hashlib.sha256((P/'execution-v3/run_native.py').read_bytes()).hexdigest(),'tests':results},indent=2)+'\n')
print(json.dumps(results,indent=2))
