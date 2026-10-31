"""Verify retained failed-study evidence without material execution."""
from pathlib import Path
import hashlib,importlib.util,json,gzip
P=Path(__file__).parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(packet=P,root=ROOT):
    freeze=json.loads((packet/'prospective-freeze.json').read_text())
    for n,h in freeze['files'].items():assert sha(packet/n)==h,n
    for n,h in freeze['references'].items():assert sha(root/n)==h,n
    assert sha(packet/'assess.py')==json.loads((packet/'assessor-freeze.json').read_text())['sha256']
    original=(packet/'generated-original/models.hpp').read_text();modified=(packet/'generated/models.hpp').read_text();assert modified.replace('\ninline int study_branch=-1;','').replace('study_branch=int(value(branch));\n','')==original
    requests=json.loads((packet/'requests.json').read_text())['requests'];assert len(requests)==219
    for backend in ('native','wasm'):
        for phase in ('configure','build'):assert json.loads((packet/(backend+'-'+phase+'-process.json')).read_text())['returncode']==0
        rows=[json.loads(v)for v in (packet/(backend+'-responses.jsonl')).read_text().splitlines()];assert [v['id']for v in rows]==[v['id']for v in requests]
    prefix=(packet/'wasm-prefix-responses.jsonl').read_bytes();tail=(packet/'wasm-tail-responses.jsonl').read_bytes();assembly=json.loads((packet/'wasm-output-assembly.json').read_text());assert prefix+tail==(packet/'wasm-responses.jsonl').read_bytes();assert len(prefix.splitlines())==64 and len(tail.splitlines())==155
    for name,key in [('wasm-prefix-responses.jsonl','prefix_sha256'),('wasm-tail-responses.jsonl','tail_sha256'),('wasm-responses.jsonl','combined_sha256')]:assert sha(packet/name)==assembly[key]
    failed=json.loads((packet/'wasm-execution-process.json').read_text());assert failed['returncode']==2 and failed['stdout_lines']==64 and failed['stderr']=='invalid token\n'
    assert json.loads((packet/'wasm-tail-execution-process.json').read_text())['returncode']==0
    spec=importlib.util.spec_from_file_location('tresca_saved_backend_assessor',packet/'assess.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);observed=module.run(packet,root);assert observed==json.loads((packet/'assessment.json').read_text())
    assert not observed['overall_pass']
    return observed
if __name__=='__main__':
    result=verify();print(json.dumps(dict(saved_evidence_verified=True,qualification_pass=result['overall_pass'],native_failures=len(result['native']['failures']),wasm_failures=len(result['wasm']['failures']))))
