"""Reproduce saved-only review in isolated historical context; requires private sources."""
from pathlib import Path
import collections,hashlib,json,shutil,subprocess,tempfile
import sys
R=Path(__file__).resolve().parents[3];A=R/'docs/reviews/production-admission-agent-v1'
if len(sys.argv)!=2:raise SystemExit('usage: replay.py NEW_OUTPUT_DIRECTORY (requires original private sources)')
P=Path(sys.argv[1]);P.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def save(n,d):(P/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
# Verify, without rewriting, the delivered output set.
outputs=load(A/'output-hashes.json')['files']
for n,h in outputs.items():assert sha(A/n)==h,n
inv=load(A/'inputs.json');resolved=[]
for row in inv['files']:
 n,h=row['path'],row['sha256'];f=R/n
 if sha(f)==h:source=n;status='unchanged'
 elif n=='IMPLEMENTATION_PLAN.md':source=None;status='missing_original_coordination_snapshot'
 else:
  archive=R/'catalogue/source-snapshots'/h/n;assert archive.is_file()and sha(archive)==h,n
  source=archive.relative_to(R).as_posix();status='exact_archived_bytes'
 resolved.append({'path':n,'sha256':h,'resolved_path':source,'status':status})
assert sum(x['resolved_path']is None for x in resolved)==1
private=inv['private_sources']+inv.get('external_instructions',[])
for row in private:assert sha(Path(row['path']))==row['sha256'],row['path']
save('input-resolution.json',{'review_inputs':resolved,'private_bindings_verified':len(private),'strict_inventory_pass':False,'missing_coordination_snapshot_not_waived':True})
# Reproduce unchanged reviewer algebra in an isolated historical tree. The original
# coordination board is unavailable; copy current context, keeping the original pin
# and expected exit 2. No rewritten checker, relaxed assertion or regenerated input.
with tempfile.TemporaryDirectory(prefix='atlas-admission-review-')as temp:
 t=Path(temp)
 for row in resolved:
  dest=t/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/(row['resolved_path']or row['path']),dest)
 for base in ['docs/admission/production-readiness-v1','docs/ingestion/barodesy-clay-2017/production-closure-v1','docs/ingestion/terracotta-2024/production-closure-v1','docs/ingestion/sanisand-2004/production-closure-v1','docs/reviews/production-admission-agent-v1']:
  for f in (R/base).rglob('*'):
   if f.is_file():
    dest=t/f.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==f.read_bytes(),str(dest)
    else:shutil.copyfile(f,dest)
 commands=[('review',['python3','-B','docs/reviews/production-admission-agent-v1/check.py'],2),('negative-historical-tests',['python3','-B','docs/admission/production-readiness-v1/test_check.py','-q'],0),('baseline',['python3','-B','docs/admission/production-readiness-v1/check.py'],0),('barodesy',['python3','-B','docs/ingestion/barodesy-clay-2017/production-closure-v1/preflight.py'],0),('terracotta',['python3','-B','docs/ingestion/terracotta-2024/production-closure-v1/verify.py'],0)]
 for name,cmd,expected in commands:
  proc=subprocess.run(cmd,cwd=t,capture_output=True,text=True);save(name+'-replay-process.json',{'command':cmd,'context':'isolated exact historical inputs; current board only, with original board pin retained','returncode':proc.returncode,'expected_returncode':expected,'stdout':proc.stdout,'stderr':proc.stderr});assert proc.returncode==expected,(name,proc.stderr)
  if name=='review':
   actual=json.loads(proc.stdout);prior=load(A/'checks.json')
   assert actual['input_hashes']['strict_integrity_gate']=='failed_live_board_drift'
   assert [x['path']for x in actual['input_hashes']['mismatches']]==['IMPLEMENTATION_PLAN.md']
   assert {k:v for k,v in actual.items()if k!='input_hashes'}=={k:v for k,v in prior.items()if k!='input_hashes'}
   save('replayed-checks.json',actual)
decisions=load(A/'decisions.json');counts=dict(collections.Counter(d['judgment']for d in decisions['decisions']))
assert len(decisions['decisions'])==41 and counts=={'supported':23,'conditional':11,'unresolved':7}
assert decisions['canonical_admission']is False and decisions['scientific_signature']is None
save('assessment.json',{'task':'INT-production-admission-review-v1','technical_delivery_accepted':True,'source_review_signed':False,'canonical_admission':False,'decision_counts':counts,'original_public_input_bindings':len(resolved),'resolved_exact':sum(v['resolved_path']is not None for v in resolved),'unavailable_original_board':True,'historical_scientific_algebra_reproduces':True,'original_checker_exit':2,'strict_inventory_pass':False,'compiled_calls':0,'new_source_acquired':False})
print(counts,'192 exact input bindings, original board failure retained; algebra reproduces.')
