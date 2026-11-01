"""Replay read-only invalid-receipt checks; never invokes a backend."""
from pathlib import Path
import importlib.util,json
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('binding_preflight',D.parent/'preflight.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
expected=json.loads((D/'results.json').read_text())['results']
for row in expected:
 try:p.build_binding(D/(row['case']+'.json'),'native',D/'nonexecutable-artifact.txt')
 except AssertionError as error:assert type(error).__name__==row['exception'] and str(error)==row['message']
 else:raise AssertionError('invalid receipt accepted: '+row['case'])
print(json.dumps({'status':'passed-negative-receipt-checks','rejections':len(expected),'compiled_calls':0}))
