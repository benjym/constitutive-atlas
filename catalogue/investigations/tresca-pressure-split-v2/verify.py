"""Reopen prospective v2 evidence without executing any material."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
P=Path(__file__).parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(packet=P,root=ROOT):
    for n,h in json.loads((packet/'prospective-freeze.json').read_text())['files'].items():assert sha(root/n)==h,n
    for n,h in json.loads((packet/'source-pins.json').read_text()).items():assert sha(root/n)==h,n
    wire=gzip.decompress((packet/'requests.txt.gz').read_bytes());assert hashlib.sha256(wire).hexdigest()==json.loads((packet/'prospective-freeze.json').read_text())['wire_sha256']
    assert (packet/'requests.json').read_bytes()==(root/'catalogue/investigations/tresca-rounded-backends-v1/requests.json').read_bytes()
    assert (packet/'requests.txt.gz').read_bytes()==(root/'catalogue/investigations/tresca-rounded-backends-v1/requests.txt.gz').read_bytes()
    modified=(packet/'generated/models.hpp').read_text();assert modified.replace('\ninline int study_branch=-1;','').replace('study_branch=int(value(branch));\n','')==(packet/'generated-original/models.hpp').read_text()
    requests=json.loads((packet/'requests.json').read_text())['requests']
    for backend in ('native','wasm'):
        for phase in ('configure','build','execution'):
            process=json.loads((packet/(backend+'-'+phase+'-process.json')).read_text());assert process['returncode']==0
            if phase=='build':assert process['command'][-4:]==['--target','atlas_tresca_pressure_split','--parallel','1']
        rows=[json.loads(v)for v in (packet/(backend+'-responses.jsonl')).read_text().splitlines()];assert len(rows)==219
        assert [row['id']for row in rows]==[row['id']for row in requests]
        assert all(row['substeps']==1 for row in rows if row['mode']=='solve'and row['ok'])
        assert json.loads((packet/(backend+'-execution-process.json')).read_text())['stdout']==(packet/(backend+'-responses.jsonl')).read_text()
    spec=importlib.util.spec_from_file_location('tresca_v2_saved_assessor',packet/'assess.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    report=m.run(packet,root);assert report==json.loads((packet/'assessment.json').read_text());assert report['overall_pass']
    return report
if __name__=='__main__':print(json.dumps(verify(),indent=2))
