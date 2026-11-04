"""Read-only saved evidence audit. No material processes; no final qualification."""
from pathlib import Path
import importlib.util,json,hashlib
H=Path(__file__).resolve().parent;N=H.parents[1];A=N/'rate-restoration-qualification-actual-v3';P=N/'rate-restoration-qualification-plan-v3';checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def test(name,value):assert value,name;checks.append(name)
def pinverify(r):p=Path(r['path']);test('pin '+str(p),p.stat().st_size==r['bytes']and sha(p)==r['sha256'])
spec=importlib.util.spec_from_file_location('_accepted_v3_data_checks',P/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.validate_execution_freeze(read(A/'execution-freeze.json'));test('exact original execution validator with reviewed C/source/generated adapter (pure)',True)
phases=['build','freeze','numerical-build','md-numerical','native','wasm','pair','extra-native'];receipts=[]
for phase in phases:
 r=read(A/('outer-'+phase)/'receipt.json');receipts.append(r)
 test(phase+' mandatory clean reap',r['mandatory_reap']is True and (r['cleanup_errors']==[]or(phase=='extra-native'and all(e.get('benign_race')is True and e['type']=='ProcessLookupError'for e in r['cleanup_errors'])))and r['reaped_returncode']==r['returncode'])
 test(phase+' truthful terminal',r['returncode']==(1 if phase=='extra-native'else 0) and r['status']==('nonzero'if phase=='extra-native'else'passed'))
 for key in ['stdout','stderr']:pinverify(r[key])
for x,y in zip(receipts,receipts[1:]):test('serial completed outer phases',x['ended_epoch']<=y['started_epoch'])
for rel in ['source-freeze-inner-binding.json']:
 r=read(A/rel);test(rel+' passed',r['passed']is True and r['post_guard_errors']==[])
r=read(A.parent/(A.name+'-source-freeze-outer-binding.json'));test('outer first-phase finally guard',r['passed']is True and r['post_guard_errors']==[])
b=read(A/'build/receipt.json');test('serial explicit targets',b['serial_builds_parallel_1']is True and b['all_processes_success']is True and all(c['returncode']==0 for c in b['commands']))
for key in ['logs','generated_files','compiler_version_logs']:
 for p in b[key]:pinverify(p)
for p in b['artifact_pins'].values():pinverify(p)
for backend in ['native','wasm']:
 r=read(A/backend/'receipt.json');test(backend+' original actual gates/closed transport',r['passed']is True and r['failures']==[] and r['owned_transport_closed']is True and r['post_bindings_unchanged']is True and r['raw_call_count']==1041)
 test(backend+' raw call count',len(read(A/backend/'raw-calls.json'))==1041)
test('independent unchanged original pair Replay exactly matches coordinator',read(H/'original-pair-replay.json')==read(A/'pair.json'))
r=read(A/'md-numerical/result.json');test('MD known-negative plus588 preserved',r['passed']is True and r['binary64_required_failure']is True and r['decimal_assessment_required']is True and r['comparisons']==588 and r['model_count']==17)
r=read(A/'md-numerical/assessment.json');test('saved MD decimal assessor reports588 zero failures',r['passed']is True and len(r['results'])==588 and r['failures']==[])
r=read(A/'extra-native/report.json');test('actual supplemental failure preserved and unqualified',r['status']=='failed'and len(r['rows'])==5 and sum(x.get('passed')is True for x in r['rows'])==4 and r['rows'][4]['result']['ok']is True and r['post_bindings_unchanged']is True)
print(json.dumps({'identity':'C-v3-completed-facts-audit','status':'completed_facts_checked_supplemental_qualification_blocked','author_lifecycle_only':'Reviewer authored v3 lifecycle, not C kernel or original scientific oracles; separate C source approval and E5 remain primary.','checks':checks,'final_qualification_accepted':False,'supplemental_failure_preserved':True,'no_material_execution':True},indent=2))
