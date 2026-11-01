import contextlib,hashlib,io,json,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1];B=P/'build-wasm-v1';N=P/'build-native-v1';I=P/'implementation-v1';A=P/'coordinator-v1/audit-v2'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)});assert v,n
load=lambda p:json.loads(p.read_text())
for parent in [B,N]:check(parent.name+'/retained file manifest',all(h(parent/k)==v for k,v in load(parent/'manifest.json').items()))
f=load(B/'freeze.json');s=load(I/'source-freeze.json');r=load(B/'report.json');n=load(N/'report.json');receipt=load(B/'receipt.json')
check('frozen source and implementation/supplement/native receipt bindings',h(I/'source-freeze.json')==f['source_freeze_sha256']==receipt['source_freeze_sha256'] and h(I/'manifest.json')==f['implementation_manifest_sha256'] and h(A/'manifest.json')==f['supplement_manifest_sha256'] and h(N/'receipt.json')==f['native_receipt_sha256'])
check('all 582 current source hashes exact',len(s['source_files'])==582 and all(h(Path(s['source_directory'])/k)==v for k,v in s['source_files'].items()))
check('freeze and retained report identities',h(B/'freeze.json')==receipt['freeze_sha256'] and h(B/'report.json')==receipt['raw_report_sha256'] and Path(receipt['raw_report_path']).read_bytes()==(B/'report.json').read_bytes())
for key in ['artifact','wasm']:check(key+'/actual payload identity',h(Path(receipt[key+'_path']))==receipt[key+'_sha256']==r['identity'][key+'_sha256'])
check('generated catalogue/header native prospective and build match',all((B/('generated-'+x)).read_bytes()==(N/('generated-'+x)).read_bytes()==(I/'source-check-generated'/x).read_bytes()==(Path(receipt['artifact_path']).parent/'generated'/x).read_bytes() for x in ['models.json','models.hpp']))
bp=load(B/'build-process.json');cp=load(B/'configure-process.json');check('Release explicit target serial build',bp['returncode']==cp['returncode']==0 and bp['command'][-4:]==['--target','atlas_control_partition_derivative_fixture','--parallel','1'] and '-DCMAKE_BUILD_TYPE=Release' in cp['command'])
ps=load(B/'processes.json');check('one persistent worker process exact command exit and linked report',len(ps)==1 and ps[0]['returncode']==0 and ps[0]['command']==['node',str(I.resolve()/'collect_wasm.mjs'),receipt['artifact_path']] and ps==r['processes'] and h(B/'processes.json')==r['identity']['processes_sha256'])
lines=[json.loads(x) for x in ps[0]['stdout'].splitlines()];check('two worker outputs bound to calls',all(all(call[k]==row[k] for k in row) for row,call in zip(lines,r['calls'])) and len(lines)==len(r['calls'])==2 and [x['repeat'] for x in lines]==[0,1] and all(x['returncode']==0 for x in lines))
check('within Wasm repeated raw outputs identical',r['calls'][0]['stdout']==r['calls'][1]['stdout'])
policy=load(I/'cases.json');lengths=[]
for j,(wc,nc) in enumerate(zip(r['calls'],n['calls'])):
 w=json.loads(wc['stdout']);nn=json.loads(nc['stdout']);lengths.append([len(nc['stdout']),len(wc['stdout'])])
 check(str(j)+'/full25 raw response exact and successful',w==wc['response'] and w['passed'] is True and [v['id'] for v in w['cases']]==[v['id'] for v in policy['cases']])
 check(str(j)+'/full parsed fixture native Wasm exact',w==nn==nc['response'])
 check(str(j)+'/raw differs solely native trailing newline',nc['stdout']==wc['stdout']+'\n' and nc['stdout']!=wc['stdout'])
check('receipt honestly denies raw byte parity',receipt['full_fixture_byte_parity'] is False)
for script,saved,out in [(I/'check_saved.py','paired-original-checks.json','rechecked-original.json'),(A/'check_audit.py','paired-independent-audit-checks.json','rechecked-audit.json')]:
 with patch.object(sys,'argv',[str(script),str(N/'report.json'),str(B/'report.json'),'--output',str(D/out)]),contextlib.redirect_stdout(io.StringIO()):
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as ex:check(script.name+'/exit',ex.code==0)
 j=load(D/out);check(script.name+'/all saved paired checks reproduced',j['passed'] and j['checks']==load(B/saved)['checks'])
(D/'checks.json').write_text(json.dumps({'decision':'accepted bounded actual paired fixture only','reviewer_compiled_calls':0,'raw_lengths_native_wasm':lengths,'parsed_value_differences':0,'checks':checks},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'paired_original':len(load(D/'rechecked-original.json')['checks']),'paired_audit':len(load(D/'rechecked-audit.json')['checks']),'lengths':lengths}))
