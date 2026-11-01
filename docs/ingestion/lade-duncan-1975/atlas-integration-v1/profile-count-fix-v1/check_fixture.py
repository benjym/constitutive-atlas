"""Source/metadata-only fixture verification and Node test relocation harness."""
from pathlib import Path
import hashlib,json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[4];sha=lambda b:hashlib.sha256(b).hexdigest()
before=(H/'test-before.mjs').read_bytes();candidate=(H/'test-proposed.mjs').read_bytes()
assert candidate==before.replace(b'complete thirteen model',b'complete fourteen model').replace(b'.cases.length,35)',b'.cases.length,36)')
assert before.count(b'complete thirteen model')==1 and before.count(b'.cases.length,35)')==2
policy=json.loads((R/'catalogue/laboratory-profile-policy.json').read_bytes());cases=json.loads((R/policy['cases']['path']).read_bytes());models=sorted((R/'models').glob('*.json'))
assert policy['case_count']==len(cases)==36 and len(models)==14
text=candidate.decode().replace("from'../tools/laboratory_profile_policy.mjs'",'from'+json.dumps((R/'tools/laboratory_profile_policy.mjs').as_uri())).replace("const root=resolve(import.meta.dirname,'..')",'const root='+json.dumps(str(R)))
(H/'test-harness.mjs').write_text(text)
result=subprocess.run(['node','--test',str(H/'test-harness.mjs')],capture_output=True,text=True)
(H/'test-results.log').write_text(result.stdout+result.stderr)
assert result.returncode==0,result.stdout+result.stderr
inputs={n:sha((R/n).read_bytes()) for n in ['tests/test_laboratory_profile_policy.mjs','tools/laboratory_profile_policy.mjs','catalogue/laboratory-profile-policy.json',policy['cases']['path'],policy['supported_policy']['path'],'atlas/evidence.py']}
inputs.update({p.relative_to(R).as_posix():sha(p.read_bytes()) for p in models})
(H/'FIXTURE_RESULTS.json').write_text(json.dumps(dict(passed=True,exact_token_changes=3,model_count=14,policy_case_count=36,pure_node_tests=16,relocation_harness_substitutions=2,production_writes=0,source_pins=[dict(original_path=n,old_sha256=h) for n,h in inputs.items()]),indent=2)+'\n')
print('PASS exact three-token change; metadata counts14/36;16pureNode tests')
