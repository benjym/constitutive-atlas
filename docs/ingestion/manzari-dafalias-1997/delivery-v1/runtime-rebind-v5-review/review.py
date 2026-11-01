"""Independent source-only adversarial review. Synthetic stand-ins never execute artifacts."""
import argparse,contextlib,copy,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent;R=P/'runtime-rebind-v5'
parser=argparse.ArgumentParser();parser.add_argument('--fixture-name',default='synthetic');parser.add_argument('--report-name',default='results.json');options=parser.parse_args()
assert Path(options.fixture_name).name==options.fixture_name and Path(options.report_name).name==options.report_name
sys.dont_write_bytecode=True;sys.path.insert(0,str(R))
import preflight as pf
import check_binding as cb
import check_coarse as cc
import check_rebind as cr
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
results=[]
def test(name,fn,should_reject):
 try:fn();rejected=False;err=None
 except Exception as e:rejected=True;err=type(e).__name__+': '+str(e)
 results.append(dict(name=name,rejected=rejected,expected_rejection=should_reject,matched_expectation=rejected==should_reject,error=err))
current=pf.check();comparison=cr.check()
original=json.loads((P/'ordinary-regression-policy-v2.json').read_text());latest=json.loads((P/'ordinary-regression-v7/policy.json').read_text())
assert original.keys()==latest.keys() and {k for k in original if original[k]!=latest[k]}=={'identity','source_freeze_sha256'}
comparison['original_v2_ordinary_all16_cases_outcomes_and_fields_exact']=True
assert sha(R/'manifest.json').startswith('e1123475')
assert sha(P/'ordinary-regression-v7/manifest.json').startswith('c24a48d4')
assert sha(R/'full-freeze.json').startswith('b03d818d')
assert len(json.loads((R/'full-freeze.json').read_text())['files'])==77
for f in sorted((R/'receipt-mocks').glob('*.json')):
 row=json.loads(f.read_text());test('external-receipt/'+f.name,lambda f=f,row=row:pf.build_binding(f,row.get('backend','native'),row.get('artifact_path',str(f))),True)
# Isolate saved verifier's own report/raw checks from external provenance checks.
# Only check/build_binding are replaced with deterministic stand-ins; hashes and delegate/coverage validation stay live.
cb.check=lambda:current
fixtures=D/options.fixture_name;fixtures.mkdir(exist_ok=False)
assert not (D/options.report_name).exists(),'preserve prior review results'
artifact=fixtures/'NONEXECUTABLE.txt';artifact.write_text('source-only mock; never executed\n')
actual=dict(backend='native',artifact_path=str(artifact),artifact_sha256=sha(artifact),generated_catalogue_sha256=json.loads((P/'ordinary-regression-v7/policy.json').read_text())['generated_catalogue_sha256'],wasm_sha256=None,build_log_sha256='mock-only')
cb.build_binding=lambda *args:actual
for study in ['md','ordinary']:
 folder=fixtures/study;folder.mkdir(exist_ok=True);receipt=folder/'coordinator-build-receipt.json';save(receipt,{'synthetic_external_validation_standin':True})
 if study=='ordinary':
  policy=json.loads((P/'ordinary-regression-v7/policy.json').read_text())
  report=dict(identity='md1997-ordinary-regression-v7',backend='native',artifact_sha256=actual['artifact_sha256'],policy_sha256=sha(P/'ordinary-regression-v7/policy.json'),manifest_sha256=sha(P/'ordinary-regression-v7/manifest.json'),passed=True,cases=[dict(model=c['model'],passed=True,response={'deliberately_not_a_real_response':True})for c in policy['cases']])
  delegate=P/'ordinary-regression-v7/run.py'
 else:
  base=P/'resolution-study-v4';plan=json.loads((base/'requests.json').read_text());report=dict(identity=dict(backend='native',artifact_sha256=actual['artifact_sha256'],model_sha256=plan['model_sha256'],requests_sha256=sha(base/'requests.json'),policy_sha256=sha(base/'POLICY.md'),manifest_sha256=sha(base/'manifest.json')),cases={c['id']:{}for c in plan['cases']});delegate=base/'run_native.py'
 binding=dict(current,**actual,study=study,delegate_returncode=0,coordinator_build_receipt_sha256=sha(receipt),delegate_sha256=sha(delegate),delegate_path=str(delegate),subset=[])
 def write(report=report,binding=binding,folder=folder):
  save(folder/'report.json',report);binding['report_sha256']=sha(folder/'report.json');save(folder/'runtime-binding.json',binding)
 write();test(study+'/missing-all-raw-transport-logs',lambda:cb.verify(folder,study),False)
 # Saved binding must reject report tampering, runtime/artifact mismatch, incomplete case order.
 (folder/'report.json').write_text((folder/'report.json').read_text()+' ')
 test(study+'/report-byte-drift',lambda:cb.verify(folder,study),True);write()
 bad=copy.deepcopy(binding);bad['artifact_sha256']='bad';save(folder/'runtime-binding.json',bad)
 test(study+'/artifact-mismatch',lambda:cb.verify(folder,study),True);write()
 bad=copy.deepcopy(report)
 if study=='ordinary':bad['cases'].pop()
 else:bad['cases'].pop(next(iter(bad['cases'])))
 save(folder/'report.json',bad);binding['report_sha256']=sha(folder/'report.json');save(folder/'runtime-binding.json',binding)
 test(study+'/missing-case',lambda:cb.verify(folder,study),True);write()
 # Explicit contradictory raw record remains ignored by saved binding.
 with gzip.open(folder/'contradictory.jsonl.gz','wt')as f:f.write(json.dumps({'request':{'mode':'WRONG'},'returncode':99,'raw_stdout':'garbage','response':{'ok':False}})+'\n')
 test(study+'/contradictory-raw-transport',lambda:cb.verify(folder,study),False)
# Isolate coarse operational/transport checks; source provenance tested above.
cc.verify=lambda *a:{'passed':True,'synthetic_standin':True}
policy=json.loads((R/'coarse-diagnostic-policy.json').read_text());c=policy['case'];folder=fixtures/'coarse';folder.mkdir(exist_ok=True)
points=[dict(coordinate=x,state=c['initial'],strain=[0.]*6)for x in c['controls']]
report={'cases':{c['id']:{'ok':True,'points':points,'response_metadata':{'loading':{'controls_bits':c['controls_bits']}}}}}
response={'ok':True,'points':[dict(control=x['coordinate'],state=x['state'],strain=x['strain'])for x in points]}
request=dict(mode='run-controls',model=policy['model'],parameters=c['parameters'],initial=c['initial'],settings=policy['settings'],protocol=c['protocol'],controls_bits=c['controls_bits'])
raw=dict(request=request,response=response,raw_stdout=json.dumps(response),returncode=0)
for label,mutation in [('positive-shape-only',None),('wrong-request',lambda r:r['request'].update(mode='WRONG')),('raw-response-mismatch',lambda r:r.update(raw_stdout='{}'))]:
 record=copy.deepcopy(raw)
 if mutation:mutation(record)
 save(folder/'report.json',report)
 with gzip.open(folder/(c['id']+'.jsonl.gz'),'wt')as f:f.write(json.dumps(record)+'\n')
 output=folder/(label+'.json');sys.argv=['check_coarse',str(folder),'--output',str(output)]
 with contextlib.redirect_stdout(io.StringIO()):
  try:cc.main()
  except SystemExit:pass
 outcome=json.loads(output.read_text())
 results.append(dict(name='coarse/'+label,passed=outcome['passed'],expected_pass=mutation is None,matched_expectation=outcome['passed']==(mutation is None)))
save(D/options.report_name,dict(identity='runtime-rebind-v5-independent-prospective-review',compiled_calls=0,builds=0,comparison=comparison,input_hashes={str(x.relative_to(P)):sha(x)for x in [R/'manifest.json',R/'full-freeze.json',R/'source-freeze.json',P/'ordinary-regression-v7/manifest.json']},tests=results,all_test_expectations_met=all(x['matched_expectation']for x in results),blocking_findings=['Saved MD/ordinary binding accepts absent or contradictory raw logs; full numerical checkers inspect report only. Additional raw request/response/transport closure required before execution readiness.']))
print(json.dumps({'checks':len(results),'expectations_met':all(x['matched_expectation']for x in results),'prospective_ready':False}))
