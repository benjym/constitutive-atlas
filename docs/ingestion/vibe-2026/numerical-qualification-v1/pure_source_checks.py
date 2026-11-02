"""Small source/preparation checks; no CDLL, Wasm or constitutive equations."""
from pathlib import Path
import importlib.util,json,tempfile,ctypes as C,math
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('qualify_source',ROOT/'tools/qualify_vibe2026.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
plan=json.loads((Path(__file__).parent/'plan-v2.json').read_text());m=json.loads((ROOT/'models/research/vibe/vibe-2026-explicit-appendix-a.json').read_text())
assert len(plan['points'])==32 and len(plan['histories'])==8 and len(plan['invalid_cases'])==7
for case in plan['histories']:
 pre,post=q.split_request(m,case['request'])
 assert sum(s['samples'] for s in pre['segments']+post['segments'])==sum(s['samples'] for s in case['request']['segments'])
 assert sum(s['duration'] for s in pre['segments']+post['segments'])==sum(s['duration'] for s in case['request']['segments'])
 assert post['segments'][-1]['controls_end']==case['request']['segments'][-1]['controls_end']
assert q.close(1.,'1.00000001',[1e-8,1e-7],'witness')['error']>0
try:q.close(1.,'2',[1e-8,1e-7],'reject')
except AssertionError:pass
else:raise AssertionError('Independent gate was bypassed')
assert q.rawsafe(float('nan'))=={'nonfinite':'nan'}
with tempfile.TemporaryDirectory() as d:
 journal=q.Journal(Path(d));journal.emit({'value':float('inf')});journal.f.close();assert json.loads((Path(d)/'events.jsonl').read_text())['value']=={'nonfinite':'inf'}
print('PASS:32points+8requests,8 restart partitions, frozen comparison bounds, durable tagged raw journal;0compiledcalls')
