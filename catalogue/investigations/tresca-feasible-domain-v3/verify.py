"""Reopen the mixed v3 result without any compiled material execution."""
from pathlib import Path
import json,hashlib,importlib.util,gzip
P=Path(__file__).parent;ROOT=P.parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify():
    for name,h in json.loads((P/'prospective-freeze.json').read_text())['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    for name,h in json.loads((P/'source-pins.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    assert (P/'assess_corpus.py').read_bytes()==(ROOT/'catalogue/investigations/tresca-pressure-split-v2/assess.py').read_bytes()
    assert (P/'assess_history.py').read_bytes()==(ROOT/'catalogue/investigations/tresca-continuous-history-v1/assess.py').read_bytes()
    assert (P/'corpus-requests.json').read_bytes()==(ROOT/'catalogue/investigations/tresca-pressure-split-v2/requests.json').read_bytes()
    assert (P/'history-requests.txt').read_bytes()==(ROOT/'catalogue/investigations/tresca-continuous-history-v1/requests.txt').read_bytes()
    wires={'corpus':gzip.decompress((P/'corpus-requests.txt.gz').read_bytes()),'history':(P/'history-requests.txt').read_bytes()}
    for n,b in wires.items():assert hashlib.sha256(b).hexdigest()==json.loads((P/'prospective-freeze.json').read_text())['wire_sha256'][n]
    for backend in ('native','wasm'):
        for phase in ('configure','build','corpus-execution','history-execution'):assert json.loads((P/(backend+'-'+phase+'-process.json')).read_text())['returncode']==0
        assert json.loads((P/(backend+'-build-process.json')).read_text())['command'][-4:]==['--target','atlas_tresca_feasible_domain','--parallel','1']
        for mode in ['corpus','history']:assert json.loads((P/(backend+'-'+mode+'-execution-process.json')).read_text())['stdout']==(P/(backend+'-'+mode+'-responses.jsonl')).read_text()
    actual=module('v3_saved_assessor',P/'assess.py').run();assert actual==json.loads((P/'assessment.json').read_text());assert not actual['overall_pass']
    for backend in ['native','wasm']:assert actual[backend]['history']['qualification_pass']and not actual[backend]['corpus']['qualification_pass']
    return actual
if __name__=='__main__':print(json.dumps({'saved_evidence_verified':True,'overall_pass':verify()['overall_pass']}))
