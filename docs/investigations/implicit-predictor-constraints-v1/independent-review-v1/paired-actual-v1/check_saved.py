import copy,hashlib,json,math,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1];W=P/'build-wasm-v1';N=P/'build-native-v1';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();receipt=json.loads((W/'receipt.json').read_text());checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
check('all wasm receipt files exact',all(h(W/k)==v for k,v in receipt['files'].items()))
check('all wasm artifacts exact',all(h(Path(k))==v for k,v in receipt['artifacts'].items()))
f=json.loads((W/'freeze.json').read_text());check('native receipt exact frozen',h(N/'receipt.json')==f['native_receipt_sha256'])
for filename,key in [('coordinator-v1/source-freeze.json','source_freeze_sha256'),('coordinator-v1/supplement-manifest-v3.json','supplement_manifest_sha256'),('run_fixture.py','collector_sha256'),('wasm_worker.mjs','worker_sha256')]:check('freeze '+filename,h(P/filename)==f[key])
closure=json.loads((P/'coordinator-v1/source-freeze.json').read_text());check('578 source closure exact',len(closure['source_files'])==578 and all(h(Path(closure['source_directory'])/k)==v for k,v in closure['source_files'].items()))
n=json.loads((N/'report.json').read_text());w=json.loads((W/'report.json').read_text());desc=json.loads((W/'describe.json').read_text());check('native wasm describe identical',desc==json.loads((N/'describe.json').read_text()))
check('wasm report19 bound',w['status']=='passed' and w['backend']=='wasm' and len(w['rows'])==19 and w['engine_sha256']==receipt['artifacts'][w['engine_path']])
req=json.loads((P/'requests.json').read_text());ids={c['id']:c for c in req['cases']};seq=req['cases']+[ids[j] for pair in req['recovery_pairs'] for j in pair];previous=None;maxerr=0;maxparity=0;rejections=0
for i,(row,original,other) in enumerate(zip(w['rows'],seq,n['rows'])):
 c=copy.deepcopy(original)
 if c['id'] in ['unload','reload','hold']:c['initial']=previous['state']
 r=row['response'];check(str(i)+'/request/raw/wire/catalogue',row['request']==c and json.loads(row['stdout'])==r and json.loads(row['wire'])=={'raw':row['stdout']} and r['catalogue_hash']==desc['sha256'])
 z=r['state'];check(str(i)+'/finite-decision',len(z)==8 and all(math.isfinite(v) for v in z) and type(r['ok']) is bool and r['ok']==c['expected']['ok'])
 check(str(i)+'/echo',all(r[k]==c[k] for k in ['model','parameters','initial','strain']) and all(r['integration_settings'][k]==v for k,v in zip(req['settings_order'],c['integration_settings'])))
 if r['ok']:
  K,Y,cap=c['parameters'];trial=sum(c['initial'][:3])/3+K*sum(c['strain'][:3]);p=min(trial,Y);g=max((trial-Y)/K,0);reference=[p]*3+[0]*3+[c['initial'][6]+g,g];err=[abs(a-b) for a,b in zip(z,reference)];maxerr=max(maxerr,max(err));check(str(i)+'/analytic-state',all(e<=(1e-8 if j<6 else 1e-10) for j,e in enumerate(err)))
  check(str(i)+'/physical-partition',r['diagnostics']['partition_committed'] is True and r['diagnostics']['increment_fractions']==[1] and 0<sum(z[:3])/3<=cap and (sum(z[:3])/3-Y)/K<=1e-10 and z[7]>=-1e-12)
 else:
  rejections+=1;check(str(i)+'/rollback',z==c['initial'] and r['diagnostics']['partition_committed'] is False)
 maxparity=max(maxparity,max(abs(a-b) for a,b in zip(z,other['response']['state'])));previous=r
check('fullstate parity',maxparity<=1e-10)
for script,out in [(P/'check_parity.py',D/'rechecked-original-parity.json'),(P/'coordinator-v1/check_fixture_v3.py',D/'rechecked-paired-v3.json')]:
 with patch.object(sys,'argv',[str(script),str(N/'report.json'),str(W/'report.json'),'--output',str(out)]):
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as ex:check(script.name+' exit',ex.code==0)
j=json.loads((D/'rechecked-paired-v3.json').read_text());check('573 paired gates',j['passed'] and len(j['checks'])==573 and j['mode']=='paired')
(D/'checks.json').write_text(json.dumps({'decision':'accepted paired actual synthetic fixture only','reviewer_compiled_calls':0,'max_wasm_state_error':maxerr,'max_native_wasm_difference':maxparity,'expected_rejections':rejections,'checks':checks},indent=2)+'\n');print(maxerr,maxparity,rejections)
