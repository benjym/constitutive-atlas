"""Independent final scientific saved-byte/source audit; no compiled processes."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,re
from pathlib import Path
D=Path(__file__).resolve().parent;B=D.parent;ROOT=D.parents[4];S=Path('/private/tmp/atlas-md1997-integrated-v1')
checks=[]
def deny(event,args):
 if event in ('subprocess.Popen','os.system','os.posix_spawn','os.exec','os.fork'):raise RuntimeError('FORBIDDEN: independent scientific source-only review')
sys.addaudithook(deny)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def check(n,ok):
 if not ok:raise RuntimeError(n)
 checks.append({'name':n,'passed':True})
def manifest(p,expected=None):
 p=Path(p)
 if expected:check('manifest '+str(p),sha(p)==expected)
 q=read(p)
 for group in ['files','review_files','inputs']:
  for n,h in q.get(group,{}).items():
   if isinstance(h,str) and re.fullmatch('[a-f0-9]{64}',h):
    target=Path(n) if Path(n).is_absolute() else (ROOT/n if group=='inputs' else p.parent/n)
    check(group+':'+str(target),sha(target)==h)
 for n,h in q.items():
  if isinstance(h,str) and re.fullmatch('[a-f0-9]{64}',h) and (p.parent/n).is_file():check('flat member '+str(p.parent/n),sha(p.parent/n)==h)
 return q
requestdir=B/'final-scientific-review-request-v2'
manifest(requestdir/'manifest.json','42982026f1cdab38489fd276b3923b9a387bf5f63d6bc7366427c64cace97b7b')
request=read(requestdir/'request.json')
for n,h in request['evidence'].items():
 p=ROOT/n
 check('request proof '+n,sha(p)==h)
 if p.name=='manifest.json':manifest(p)
for n,h in request['intended_installation'].items():check('actual isolated installation '+n,sha(S/n)==h)
# Re-run the unchanged prior independent source algebra/hash checks, redirecting
# only its output destination. Never rewrite the immutable pending review.
old=B/'full-model-review-v1/check_review.py'
code=old.read_text().replace('OUT = Path(__file__).resolve().parent','OUT = Path('+repr(str(D))+')').replace('BASE = OUT.parent','BASE = Path('+repr(str(B))+')')
try:exec(compile(code,str(old),'exec'),{'__file__':str(old)})
except SystemExit as exc:
 if exc.code:raise
prior=read(D/'checks.json');check('prior independent222 source/algebra checks',prior['total']==222 and prior['failures']==0)
(D/'source-algebra-rechecked.json').write_text(json.dumps(prior,indent=2)+'\n')
I=ROOT/'docs/investigations/control-partition-derivative-v1'
profile=I/'current-profile-actual-review-v1'
for n,h in [('power-burgers-manifest-v1.json','3529db32e43aa763acd269d3497e88a8d5758c0c7e4ee6ec9a9f54f458f00791'),('sls-manifest-v1.json','ee4220efd55c22392d0e79c9e898da654d1e09f77076fe0292b1cc4530f5215b'),('j2-manifest-v1.json','c197f6c1420eb36ebafe28b6d41f41087629d4d98379f2ebde362edd3a0314fc')]:manifest(profile/n,h)
for n in ['power','burgers','sls','j2']:
 q=read(profile/(n+'-decision.json'));check('actual accepted '+n,str(q['decision']).startswith('ACCEPT') and q['blocking_findings']==[])
for n in ['native-decimal-actual-build-review-v1','native-decimal-observation-source-review-v1','native-decimal-observation-final-pin-review-v1','native-decimal-observation-actual-review-v1']:
 manifest(I/n/'manifest.json')
actual=read(I/'native-decimal-observation-actual-review-v1/decision.json')
check('actual strict11/direct588/child588/CTest8+1',actual['accepted'] is True and actual['strict_negative_contracts']==11 and actual['direct_comparisons']==actual['ctest_numerical_child_comparisons']==588 and actual['ctest_main_registrations']==8 and actual['ctest_recorded_registrations']==1)
blocked=read(I/'native-decimal-production-ci-implementation-review-v1/decision.json')
check('production wrapper B1 retained as BLOCKED',blocked['accepted'] is False and blocked['status']=='BLOCKED')
# Actual generation receipt is data from parent; independently hash each output.
g=read(B/'current-base-generation-v1/receipt.json')
for n,v in g['generated'].items():
 check('byte-identical normal generation '+n,sha(Path('/private/tmp/atlas-md1997-current-generation-v1')/n)==v['current_generation_sha256']==v['qualified_generation_sha256'] and v['exact'] is True)
q=read(S/'models/manzari-dafalias-1997-constant-m-be-v1.json')
check('complete v0.3 selected model',q['schema_version']=='0.3' and q['id']=='manzari-dafalias-1997-constant-m-be-v1' and 'integration' not in q and len(q['parameters'])==17)
f=q['formulation'];check('explicit fixed-frame effective Mandel small strain',f['time_dependence']=='strain_path' and f['equation_form']=='incremental_residual' and f['kinematics']=='small_strain_3d' and f['frame']=='fixed_spatial' and f['objective_rate']=='none' and f['tensor_representation']=='mandel' and f['stress']['scope']=='effective')
check('isotropic160kPa e.65 alpha0 explicit',q['state'][0]['initial']==[160000.,160000.,160000.,0,0,0] and q['state'][1]['initial']==.65 and q['state'][2]['initial']==[0]*6)
# Bind the actual installed scientific core to the qualified582 frozen source.
qualified=read(I/'implementation-v1/source-freeze.json')['source_files']
for group in ['cpp/','atlas/','schemas/','models/']:
 selected=[(n,h) for n,h in qualified.items() if n.startswith(group)]
 for n,h in selected:
  if n=='atlas/measurement_units.py':
   check('sole Python units delta explicitly reviewed',read(B/'current-profile-source-equivalence-review-v1/verdict.json')['blocking_findings']==[])
  else:check('qualified scientific core '+n,sha(S/n)==h)
manifest(B/'current-profile-guard-replay-actual-v1/manifest.json','b568dd6aaeb27f714d559aa40ce88904e724d4ed683949da5ac30205cee2d184')
check('current actual guard supplement independently accepted',read(D/'current-guard-actual-checks.json')['accepted'] is True)
# Preserve original review and request pins after all source-only work.
check('pending review immutable',sha(B/'full-model-review-v1/manifest.json')=='5df49768c9b91d140c8591a57fab49a345733274c0a2c3c09dfd47f731223bcc')
(D/'checks.json').write_text(json.dumps({'identity':'independent-final-scientific-v2-source-and-saved-binding-checks','reviewer_run':'/root/md1997_final_review','checks':checks,'passed':len(checks),'prior_source_algebra_checks':222,'compiled_calls':0,'builds':0,'decision':'Source/saved checks complete; see separate final checklist decision'},indent=2)+'\n')
print(json.dumps({'passed':len(checks),'prior_source_algebra_checks':222,'compiled_calls':0}))
