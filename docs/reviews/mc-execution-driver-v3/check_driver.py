"""Check execution gates and compatibility assessor on saved/manufactured data."""
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import copy,json,tempfile
import execute as driver
from assess_compatibility import assess,read,P,R,C
checks=[]
with tempfile.TemporaryDirectory()as tmp:
 d=Path(tmp)
 with patch.object(driver,'P',d),patch.object(driver,'STAGE',d/'stage'),patch.object(driver.subprocess,'run')as run:
  (d/'manifest.json').write_text('{"files":{}}')
  try:driver.execute('native')
  except FileNotFoundError:checks.append('missing execution freeze blocks all commands')
  else:raise AssertionError('missing freeze passed')
  assert not(d/'stage').exists();run.assert_not_called()
 with patch.object(driver,'STAGE',d/'stage'),patch.object(driver,'verify_inputs',return_value={}),patch.object(driver.subprocess,'run')as run:
  try:driver.execute('wasm')
  except FileNotFoundError:checks.append('unqualified native blocks Wasm before creation or commands')
  else:raise AssertionError('missing native passed')
  assert not(d/'stage').exists();run.assert_not_called()
 # A generated header mismatch must stop before configure/build, retaining failure.
 c=d/'collector';c.mkdir();(c/'source-pins.json').write_text('{"sources":{}}');(c/'catalogue.json').write_text('{}');(c/'generation.json').write_text('{"generated_header_sha256":"wrong"}')
 setup=d/'setup';setup.mkdir();(setup/'CMakeLists.txt').write_text('# manufactured test input')
 def generate_only(argv,**kwargs):
  assert 'atlas.compiler'in argv;out=Path(argv[-2]);out.mkdir();(out/'models.json').write_text('{}');(out/'models.hpp').write_text('manufactured wrong header');return SimpleNamespace(stdout=b'',stderr=b'',returncode=0)
 with patch.object(driver,'P',setup),patch.object(driver,'C',c),patch.object(driver,'STAGE',d/'bad-header'),patch.object(driver,'verify_inputs',return_value={}),patch.object(driver,'sha',side_effect=lambda f:'freeze' if Path(f).name=='freeze.json' else 'bad-header'),patch.object(driver.subprocess,'run',side_effect=generate_only)as run:
  try:driver.execute('native')
  except AssertionError:checks.append('generated mismatch blocks configure and build with retained failure')
  else:raise AssertionError('header mismatch passed')
  assert run.call_count==1;assert read(d/'bad-header/native/receipt.json')['completed']is False
 for role in ['synthetic','post','unknown']:
  try:driver.plan(role)
  except ValueError:checks.append('invalid executable role '+role)
  else:raise AssertionError(role)
 # Interrupted commands retain partial output and never become a completed run.
 with patch.object(driver,'P',setup),patch.object(driver,'C',c),patch.object(driver,'STAGE',d/'timeout'),patch.object(driver,'verify_inputs',return_value={}),patch.object(driver,'sha',return_value='freeze'),patch.object(driver.subprocess,'run',side_effect=driver.subprocess.TimeoutExpired(['manufactured'],180,output=b'partial',stderr=b'interrupted')):
  try:driver.execute('native')
  except driver.subprocess.TimeoutExpired:checks.append('timeout retains partial stdout stderr and failed receipt')
  else:raise AssertionError('timeout passed')
  stage=d/'timeout/native';assert (stage/'generate.stdout').read_bytes()==b'partial'and(stage/'generate.stderr').read_bytes()==b'interrupted'
  receipt=read(stage/'receipt.json');assert receipt['completed']is False and receipt['commands'][0]['timeout']is True
 # Staged bytes are checked separately from the pinned live source tree.
 c2=d/'staged-collector';c2.mkdir();(c2/'source-pins.json').write_text('{"sources":{"cpp/test.hpp":"expected-original-hash"}}')
 staged=d/'tampered';(staged/'frozen/cpp').mkdir(parents=True);(staged/'frozen/cpp/test.hpp').write_text('tampered')
 with patch.object(driver,'C',c2):
  try:driver.verify_stage(staged)
  except AssertionError:checks.append('tampered staged C++ rejected independently of live source')
  else:raise AssertionError('staged source mutation passed')
 wasm_labels=[x[0]for x in driver.plan('wasm')];assert wasm_labels.index('replays')<wasm_labels.index('parity')<wasm_labels.index('compatibility-collect')
 assert 'parity'not in[x[0]for x in driver.plan('native')];checks.append('Wasm requires source-accuracy replay and physical parity before compatibility')
 # Compatibility: full historical responses, changing only new catalogue identity/time.
 base=R/'catalogue/investigations/declared-loading-mixed-v1';reqs=read(base/'requests.json');old=read(base/'baseline-native.json');cat=read(C/'catalogue.json')
 calls=[{'name':'atlas_describe','args':[],'raw':json.dumps(cat),'process':{'status':0,'signal':None,'error':None,'stderr':''}}];rows=[]
 for req,row in zip(reqs,old['rows']):
  s=req['specification'];v=copy.deepcopy(row['result']);v['catalogue_hash']=cat['sha256'];v['elapsed_ms']=0
  args=[s['model'],','.join(map(str,s['parameters'])),','.join(map(str,s['initial'])),s['protocol'],','.join(s['loading']['controls_bits']),','.join(str(s['integration_settings'][k])for k in ['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'])]
  raw=json.dumps(v);rows.append({'id':req['id'],'raw':raw});calls.append({'name':'atlas_run_controls_scope_with_settings','args':args,'raw':raw,'process':{'status':0 if v['ok']else 1,'signal':None,'error':None,'stderr':''}})
 original={'role':'native','rows':rows,'calls':calls};file=d/'compat.json';file.write_text(json.dumps(original));assert assess(file,'native')['passed'];checks.append('twelve full historical compatibility frames accepted')
 def reject(label,mutation):
  x=copy.deepcopy(original);mutation(x);assert json.dumps(x)!=json.dumps(original),label;file.write_text(json.dumps(x))
  try:assess(file,'native')
  except (AssertionError,ValueError,KeyError):checks.append(label)
  else:raise AssertionError('false pass '+label)
 def response(x,change,index=0):
  v=json.loads(x['rows'][index]['raw']);change(v);raw=json.dumps(v);x['rows'][index]['raw']=raw;x['calls'][index+1]['raw']=raw
 reject('full state drift rejected',lambda x:response(x,lambda v:v['points'][0]['state'].__setitem__(0,100001)))
 reject('diagnostic drift rejected',lambda x:response(x,lambda v:v['points'][0].__setitem__('iterations',1)))
 reject('scope drift rejected',lambda x:response(x,lambda v:v['stress'].__setitem__('scope','total')))
 reject('old catalogue identity rejected',lambda x:response(x,lambda v:v.__setitem__('catalogue_hash','old')))
 reject('Boolean control rejected',lambda x:response(x,lambda v:v['points'][0].__setitem__('control',False)))
 reject('GIS original failure cannot be promoted',lambda x:response(x,lambda v:v.__setitem__('ok',True),11))
 reject('native process omissions rejected',lambda x:[c.pop('process')for c in x['calls']])
 reject('wrong backend role rejected',lambda x:x.__setitem__('role','wasm'))
result={'passed':True,'checks':checks,'check_count':len(checks),'compiled_calls':0,'compatibility_frames':'manufactured from prior saved backend responses; no new observations'}
(P/'driver-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
