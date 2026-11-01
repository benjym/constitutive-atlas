import copy,hashlib,json,math,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1];B=P/'build-native-v1';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(name,passed,detail=None):
 checks.append({'name':name,'passed':bool(passed),'detail':detail});assert passed,name
receipt=json.loads((B/'receipt.json').read_text());freeze=json.loads((B/'freeze.json').read_text());report=json.loads((B/'report.json').read_text());req=json.loads((P/'requests.json').read_text());catalogue=json.loads((B/'describe.json').read_text())
check('receipt files exact',all(h(B/k)==v for k,v in receipt['files'].items()))
check('pre-observation inputs exact',all(h(P/k)==v for k,v in freeze['inputs'].items()))
closure=json.loads((P/'coordinator-v1/source-freeze.json').read_text());S=Path(freeze['source']);check('578 source hashes exact',len(closure['source_files'])==578 and all(h(S/k)==v for k,v in closure['source_files'].items()))
artifact=Path(receipt['artifact_path']);check('actual artifact exact identity',h(artifact)==receipt['artifact_sha256']==report['engine_sha256'] and str(artifact)==report['engine_path'])
build=Path(freeze['build_directory']);check('generated metadata byte equal prospective',all((build/'generated'/n).read_bytes()==(P/'source-check-generated'/n).read_bytes() for n in ['models.json','models.hpp']))
check('saved describe exact generated object',catalogue==json.loads((build/'generated/models.json').read_text()))
check('generated catalogue file receipt exact',h(build/'generated/models.json')==receipt['generated_catalogue_sha256'])
check('native only passed19',report['backend']=='native' and report['status']=='passed' and report['failures']==[] and len(report['rows'])==19)
byid={c['id']:c for c in req['cases']}; seq=req['cases']+[byid[n] for pair in req['recovery_pairs'] for n in pair];previous=None;max_stress=0;max_internal=0;max_residual=0; successes=0;failures=0
for i,(row,original) in enumerate(zip(report['rows'],seq)):
 c=copy.deepcopy(original)
 if c['id'] in ['unload','reload','hold']:c['initial']=previous['state']
 check(str(i)+'/exact request and raw',row['request']==c and json.loads(row['stdout'])==row['response'] and row['stderr']=='' and row['errors']==[])
 z=row['response']['state'];response=row['response'];previous=response;expected=c['expected']['ok'];check(str(i)+'/decision/fullstate',type(response['ok']) is bool and response['ok']==expected and len(z)==8 and all(math.isfinite(v) for v in z))
 check(str(i)+'/catalogue/echo',response['catalogue_hash']==catalogue['sha256'] and all(response[k]==c[k] for k in ['model','parameters','initial','strain']))
 check(str(i)+'/settings',all(response['integration_settings'][k]==v for k,v in zip(req['settings_order'],c['integration_settings'])))
 diag=response['diagnostics'];check(str(i)+'/commit',diag['partition_committed'] is expected)
 if expected:
  successes+=1;K,Y,cap=c['parameters'];zn=c['initial'];pn=sum(zn[:3])/3;trial=pn+K*sum(c['strain'][:3]);p=min(trial,Y);g=max((trial-Y)/K,0);reference=[p]*3+[0]*3+[zn[6]+g,g]
  errors=[abs(v-w) for v,w in zip(z,reference)];max_stress=max(max_stress,max(errors[:6]));max_internal=max(max_internal,max(errors[6:]));pressure=sum(z[:3])/3;f=(pressure-Y)/K
  residual=max(max(abs(z[j]-zn[j]-K*(sum(c['strain'][:3])-z[7]))/K for j in range(3)),abs(z[6]-zn[6]-z[7]),abs(math.sqrt(z[7]**2+f**2)-z[7]+f));max_residual=max(max_residual,residual)
  check(str(i)+'/independent fullstate/physical',all(e<=(1e-8 if j<6 else 1e-10) for j,e in enumerate(errors)) and pressure>0 and pressure<=cap and f<=1e-10 and z[7]>=-1e-12)
  check(str(i)+'/single partition',diag['increment_fractions']==[1] and diag['substeps']==1)
 else:
  failures+=1;check(str(i)+'/exact full parent rollback',z==c['initial'] and diag['substeps']==0)
# Recheck saved report using reviewed Python verifier only; does not invoke engine.
script=P/'coordinator-v1/check_fixture_v3.py';out=D/'rechecked-v3.json'
with patch.object(sys,'argv',[str(script),str(B/'report.json'),'--native-only','--output',str(out)]):
 try:runpy.run_path(str(script),run_name='__main__')
 except SystemExit as ex:check('v3 saved report recheck exit',ex.code==0)
j=json.loads(out.read_text());check('277 native gates reproduced',j['passed'] and len(j['checks'])==277 and j['mode']=='native-only')
(D/'checks.json').write_text(json.dumps({'status':'accepted-native-fixture-only','reviewer_compiled_calls':0,'successes':successes,'expected_failures':failures,'max_stress_error_vs_actual_parent_projection':max_stress,'max_internal_error':max_internal,'max_scaled_equation_residual':max_residual,'checks':checks},indent=2)+'\n')
print(successes,failures,max_stress,max_internal,max_residual)
