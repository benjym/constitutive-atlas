"""Checker-only synthetic artifacts; never backend evidence."""
from pathlib import Path
import json,hashlib,copy,tempfile,contextlib,io
from check_backend_results_v2 import main
HERE=Path(__file__).resolve().parent;request=HERE/'backend-requests-v2.json';reqs=json.loads(request.read_text());rows=[]
for r in reqs['requests']:
 status=r['expected_status'];rows.append(dict(id=r['id'],status=status,state=r.get('expected_state',[-1234567]*len(r['state'])) if status else [-1234567]*len(r['state']),coordinate=r['coordinate']+r['progress'] if status else -7654321,observables=r.get('expected_observables',[0]*r['observable_count']) if status else [-1234567]*r['observable_count']))
data=dict(identity='checker-only-synthetic-artifact-not-backend-evidence',request_sha256=hashlib.sha256(request.read_bytes()).hexdigest(),rows=rows);checks=[]
with tempfile.TemporaryDirectory() as d:
 file=Path(d)/'fixture.json'
 def assess(data):
  file.write_text(json.dumps(data))
  with contextlib.redirect_stdout(io.StringIO()):main(str(request),str(file))
 assess(data);checks.append('synthetic well-formed artifact accepted')
 for label,mutate in [('short state',lambda x:x['rows'][0]['state'].pop()),('extra observable',lambda x:x['rows'][0]['observables'].append(0)),('nonfinite state',lambda x:x['rows'][0]['state'].__setitem__(0,float('nan'))),('nonfinite coordinate',lambda x:x['rows'][0].__setitem__('coordinate',float('inf'))),('wrong status',lambda x:x['rows'][0].__setitem__('status',0)),('wrong request hash',lambda x:x.__setitem__('request_sha256','0'*64))]:
  bad=copy.deepcopy(data);mutate(bad)
  try:assess(bad)
  except AssertionError:checks.append(label+' rejected')
  else:raise AssertionError(label+' accepted')
result=dict(scope='Checker-only synthetic fixtures, no compiled output or numerical backend evidence',pass_count=len(checks),checks=checks)
(HERE/'result-checker-tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
