"""Replay frozen source and recorded assessments; never execute candidate binaries."""
from pathlib import Path
import sys,json,hashlib,tempfile,shutil,subprocess
P=Path(__file__).resolve().parent
def checked_freeze(root):
 d=json.loads((root/'prospective-freeze.json').read_text())
 for name,r in d['files'].items():
  b=(root/name).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256'],name
 return len(d['files'])
count=checked_freeze(P)
out=Path(tempfile.mkdtemp(prefix='mc-complete-source-replay-',dir='/private/tmp'));capsule=out/'study'
# Complete frozen capsule plus its freeze; no recorded compiled output is an input to source tests.
for name in list(json.loads((P/'prospective-freeze.json').read_text())['files'])+['prospective-freeze.json']:
 p=capsule/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/name,p)
for program in('static_checks.py','preflight.py','verify_source.py'):
 r=subprocess.run([sys.executable,'-B',str(capsule/program)],capture_output=True)
 (out/(program+'.stdout')).write_bytes(r.stdout);(out/(program+'.stderr')).write_bytes(r.stderr)
 assert r.returncode==0,(program,r.stderr.decode())
 assert json.loads(r.stdout).get('passed',json.loads(r.stdout).get('ideal_passed'))is True,program
checked_freeze(capsule)
for backend in('native','wasm'):
 r=subprocess.run([sys.executable,'-B',str(capsule/'assess.py'),str(P/backend/'run.stdout')],capture_output=True)
 assert r.returncode==0,(backend,r.stderr.decode());observed=json.loads(r.stdout);expected=json.loads((P/backend/'assessment.json').read_text());assert observed==expected,backend
count_artifacts=0
for name,record in json.loads((P/'artifacts.json').read_text())['files'].items():
 p=Path(record['path'])
 if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'];count_artifacts+=1
checked_freeze(P)
print(json.dumps({'passed':True,'frozen_files':count,'copied_source_replay':True,'source_static_preflight_policy_and_supplemental_references_pass':True,'both_recorded_assessments_exact':True,'available_local_artifact_hashes_checked':count_artifacts,'candidate_calls_during_replay':0,'compiled_executions_during_replay':0,'logs':str(out)},indent=2))
