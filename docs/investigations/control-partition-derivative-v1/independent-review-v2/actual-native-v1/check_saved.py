import contextlib,hashlib,io,json,math,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1];B=P/'build-native-v1';I=P/'implementation-v1';A=P/'coordinator-v1/audit-v2';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
manifest=json.loads((B/'manifest.json').read_text());check('all retained build/evidence files',all(h(B/k)==v for k,v in manifest.items()))
r=json.loads((B/'report.json').read_text());receipt=json.loads((B/'receipt.json').read_text());freeze=json.loads((B/'freeze.json').read_text());check('freeze inputs exact',all(h(P/k)==v for k,v in freeze['inputs'].items()))
check('artifact raw and freeze identity',h(Path(receipt['artifact_path']))==receipt['artifact_sha256']==r['identity']['artifact_sha256'] and h(B/'report.json')==receipt['raw_report_sha256'] and h(B/'freeze.json')==receipt['freeze_sha256'])
source=json.loads((I/'source-freeze.json').read_text());check('582 source hashes exact',len(source['source_files'])==582 and all(h(Path(source['source_directory'])/k)==v for k,v in source['source_files'].items()))
check('generated two models exact prospective',all((B/('generated-'+n)).read_bytes()==(I/'source-check-generated'/n).read_bytes() for n in ['models.json','models.hpp']) and len(json.loads((B/'generated-models.json').read_text())['models'])==2)
check('generated build metadata exact saved copies',all((B/('generated-'+n)).read_bytes()==(Path(freeze['build_directory'])/'generated'/n).read_bytes() for n in ['models.json','models.hpp']))
bp=json.loads((B/'build-process.json').read_text());cp=json.loads((B/'configure-process.json').read_text());check('explicit serial target/build release',bp['returncode']==cp['returncode']==0 and bp['command'][-4:]==['--target','atlas_control_partition_derivative_fixture','--parallel','1'] and '-DCMAKE_BUILD_TYPE=Release' in cp['command'])
check('two actual calls byte identical raw',len(r['calls'])==2 and r['calls'][0]['stdout']==r['calls'][1]['stdout'])
policy=json.loads((I/'cases.json').read_text());maxstress=0;maxvoid=0
for repeat,call in enumerate(r['calls']):
 data=json.loads(call['stdout']);check(str(repeat)+'/raw parsed and full25order',data==call['response'] and data['passed'] is True and [x['id'] for x in data['cases']]==[x['id'] for x in policy['cases']])
 for x,c in zip(data['cases'],policy['cases']):
  n=str(repeat)+'/'+c['id'];check(n+'/positive verdict',x['passed'] is True)
  if c['kind']=='helper':
   check(n+'/exact outcomes counts selectedh',x['ok']==c['ok'] and x['evaluator_calls']==c['evaluator_calls'] and len(x['probes'])==c['probe_records'] and x['selected_h']==c['selected_h'])
   if c['ok']:
    pair=x['probes'][-2:];observe=lambda z:z[0]-.5*(z[1]+z[2]) if c['id']=='protocol3-direction' else .5*(z[1]+z[2]);slopes=[(observe(v['advance']['state'])-observe(x['base']['state']))/v['h'] for v in pair]
    check(n+'/independent selected slopes',x['value']==slopes[-1] and abs(x['value']-c['value'])<=c['value_atol'] and abs(slopes[0]-slopes[1])<=.001*max(1,abs(slopes[0]),abs(slopes[1])))
  if c['kind']=='elastic':
   z=x['advance']['state'];errs=[abs(u-v) for u,v in zip(z,c['state'])];maxstress=max(maxstress,max(errs[:6]));maxvoid=max(maxvoid,errs[6]);check(n+'/independent analytic fullstate',len(z)==7 and all(e<=(1e-6 if j<6 else 1e-12) for j,e in enumerate(errs)) and abs(x['increment'][1]+.00025)<=1e-12 and abs(x['increment'][2]+.00025)<=1e-12)
   for label in ['affine_base','affine_probe']:
    total=x['increment'][:]
    if label=='affine_probe':total[1]+=1e-6;total[2]+=1e-6
    diag=x[label]['diagnostics'];fractions=diag['increment_fractions'];check(n+'/'+label+'/actual increments sum input',all(abs(sum(v[j]for v in diag['accepted_increments'])-total[j])<=1e-18 for j in range(6)) and len(fractions)==(2 if c['id']=='analytic-rate-control' else 1))
  if c['kind']=='recovery':check(n+'/exact failedparent and validrecovery',x['failure']['ok'] is False and x['failure']['state']==x['invalid_parent']==c['initial'][:6]+[-1] and x['recovery']['ok'] is True)
for script,saved,out in [(I/'check_saved.py','original-checks.json','rechecked-original.json'),(A/'check_audit.py','independent-audit-checks.json','rechecked-audit.json')]:
 with patch.object(sys,'argv',[str(script),str(B/'report.json'),'--output',str(D/out)]),contextlib.redirect_stdout(io.StringIO()):
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as ex:check(script.name+'/exit',ex.code==0)
 j=json.loads((D/out).read_text());check(script.name+'/identical check results',j['passed'] and j['checks']==json.loads((B/saved).read_text())['checks'])
(D/'checks.json').write_text(json.dumps({'decision':'accepted bounded actual native fixture only','reviewer_compiled_calls':0,'max_analytic_stress_error':maxstress,'max_analytic_void_error':maxvoid,'checks':checks},indent=2)+'\n');print(maxstress,maxvoid)
