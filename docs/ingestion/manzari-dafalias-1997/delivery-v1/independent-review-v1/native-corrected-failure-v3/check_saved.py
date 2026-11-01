import collections,gzip,hashlib,importlib.util,json,runpy,sys
from pathlib import Path
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1];B=P/'build-native-v3';ROOT=P.parents[3];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
build=json.loads((B/'build-receipt.json').read_text());failure=json.loads((B/'failure-receipt.json').read_text());freeze=json.loads((B/'freeze.json').read_text());report=json.loads((B/'qualification-report.json').read_text());qc=json.loads((B/'qualification-checks.json').read_text());ordinary=json.loads((B/'ordinary-report.json').read_text());binding=json.loads((B/'runtime-binding.json').read_text())
check('all build files',all(h(B/k)==v for k,v in build['files'].items()))
check('all build artifacts',all(h(Path(k))==v for k,v in build['artifacts'].items()))
check('all prefreeze inputs',all(h(ROOT/k)==v for k,v in freeze['inputs'].items()))
check('all failed study receipts',all(h(B/k)==v for k,v in failure['files'].items()))
for key in ['raw_files','ordinary_raw_files']:check(key+' all hashes',all(h(Path(k))==v for k,v in failure[key].items()))
closure=json.loads((P/'runtime-rebind-v1/source-freeze.json').read_text());check('578 exact source hashes',len(closure['source_files'])==578 and all(h(Path(closure['source_directory'])/k)==v for k,v in closure['source_files'].items()))
check('candidate exact',h(P/'manzari-dafalias-1997-constant-m-be-v1.json')==report['identity']['model_sha256']=='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064')
check('artifact/report/runtime binding',h(Path(report['identity']['artifact_path']))==report['identity']['artifact_sha256']==binding['artifact_sha256'] and binding['report_sha256']==h(B/'qualification-report.json'))
check('16 generated model identities',json.loads((B/'describe.json').read_text())==json.loads((Path(freeze['build_directory'])/'generated/models.json').read_text()) and len(json.loads((B/'describe.json').read_text())['models'])==16)
rawcount=0
for path in failure['raw_files']:
 if not path.endswith('.jsonl.gz'):continue
 with gzip.open(path,'rt') as stream:
  for line in stream:
   row=json.loads(line);check('raw '+str(row['call_index']),json.loads(row['raw_stdout'])==row['response']);rawcount+=1
check('4951 raw calls accounted',rawcount==report['call_count']==4951)
check('all35 cases one incomplete',len(report['cases'])==35 and [k for k,v in report['cases'].items() if not v['ok']]==['drained-dense-compression-128'])
failed=[c for c in qc['results'] if not c['passed']];prefix=collections.Counter(c['channel'].split('-')[0] for c in failed);check('109/12596 retained',len(failed)==qc['failures']==109 and len(qc['results'])==qc['checks']==12596 and qc['passed'] is False)
check('special/restart/covariance main channels all pass',all(c['passed'] for c in qc['results'] if c['case'] in ['special','restart-replay','tensor-covariance']))
# Independently apply only the native-side v6 branch/partition conditions, not fake paired reports.
spec=importlib.util.spec_from_file_location('parity',P/'parity-v6/check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);plan=json.loads((P/'execution-v3/requests.json').read_text());special=report['special'];base=module.branch(special['linearize']['state'],plan['special']['parameters']);check('native AD branch away boundaries',base is not None)
for name in ['linearize']+['fd-'+str(j)+'-'+str(sign) for j in range(6) for sign in [-1,1]]:
 s=special[name];check('native '+name+' branch and partition',s['ok'] is True and module.branch(s['state'],plan['special']['parameters'])==base and s['diagnostics']['increment_fractions']==[1] and s['diagnostics'].get('partition_committed',True) is True)
restart=report['cases']['restart-replay'];planned=next(c for c in plan['cases'] if c['id']=='restart-replay');idx=planned['restart_index'];parent=report['cases'][planned['compare_to']]['points'][idx-1]['state'][:13];receipt=restart['restart_receipt'];check('native restart receipt exact index and parent',receipt['index']==idx and receipt['all_persistent_state']==parent and restart['points'][idx-1]['state'][:13]==parent)
check('ordinary16 outcomes pass',ordinary['passed'] and len(ordinary['cases'])==16 and all(c['passed'] for c in ordinary['cases']) and ordinary['artifact_sha256']==report['identity']['artifact_sha256'])
sys.path.insert(0,str(P/'execution-v3'));out=D/'rechecked-main.json'
with patch.object(sys,'argv',[str(P/'execution-v3/check_reports.py'),str(B/'qualification-report.json'),'--output',str(out)]):
 try:runpy.run_path(str(P/'execution-v3/check_reports.py'),run_name='__main__')
 except SystemExit as ex:check('main recheck retains failed exit',ex.code==1)
check('main recheck identical gates',json.loads(out.read_text())['results']==qc['results'])
summary={'decision':'qualification failed; E5 not accepted','reviewer_compiled_calls':0,'calls':rawcount,'operational_successes':34,'main_failure_prefixes':dict(prefix),'failures_by_case':dict(collections.Counter(c['case'] for c in failed)),'native_branch_signature':base,'ordinary16_expected_outcomes_passed':True,'checks':checks}
(D/'checks.json').write_text(json.dumps(summary,indent=2)+'\n');print({k:v for k,v in summary.items() if k not in ['checks','failures_by_case']})
