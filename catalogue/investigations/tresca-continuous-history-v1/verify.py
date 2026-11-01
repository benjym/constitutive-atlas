"""Verify retained failed continuous history without material execution."""
from pathlib import Path
import hashlib,importlib.util,json
P=Path(__file__).parent;ROOT=P.parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def verify():
    for name,h in json.loads((P/'prospective-freeze.json').read_text())['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    for name,h in json.loads((P/'source-pins.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    original=json.loads((ROOT/'docs/reviews/tresca-rounded-reference-v1/inputs.json').read_text())['history'];assert json.loads((P/'inputs.json').read_text())==original
    prior=ROOT/'catalogue/investigations/tresca-pressure-split-v2'
    assert (P/'frozen/model.json').read_bytes()==(prior/'frozen/model.json').read_bytes()
    assert (P/'generated/models.hpp').read_bytes()==(prior/'generated-original/models.hpp').read_bytes()
    for backend in ('native','wasm'):
        for phase in ('configure','build','execution'):assert json.loads((P/(backend+'-'+phase+'-process.json')).read_text())['returncode']==0
        assert json.loads((P/(backend+'-build-process.json')).read_text())['command'][-4:]==['--target','atlas_tresca_history','--parallel','1']
        assert json.loads((P/(backend+'-execution-process.json')).read_text())['stdout']==(P/(backend+'-responses.jsonl')).read_text()
    actual=module('history_verify_assessor',P/'assess.py').run();assert actual==json.loads((P/'assessment.json').read_text());assert not actual['overall_pass']
    diagnostic=module('history_verify_rounding',P/'rounding_diagnostic.py').run();assert diagnostic==json.loads((P/'rounding-diagnostic.json').read_text())
    return actual
if __name__=='__main__':
    r=verify();print(json.dumps({'saved_evidence_verified':True,'qualification_pass':r['overall_pass'],'native_accepted':r['native']['accepted'],'wasm_accepted':r['wasm']['accepted']}))
