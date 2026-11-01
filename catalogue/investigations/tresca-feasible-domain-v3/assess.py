"""Unchanged copied subgates; no exemption for newly rejected current probes."""
from pathlib import Path
import importlib.util,json,gzip
P=Path(__file__).parent;ROOT=P.parents[2]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def run(packet=P,root=ROOT):
    c=module('v3_corpus_assessor',packet/'assess_corpus.py');h=module('v3_history_assessor',packet/'assess_history.py');out={}
    requests=json.loads((packet/'corpus-requests.json').read_text())['requests'];policy=json.loads((packet/'corpus-policy.json').read_text());reference=json.loads(gzip.decompress((root/'docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz').read_bytes()));inputs=json.loads((packet/'history-inputs.json').read_text())
    for backend in ('native','wasm'):
        corpus=c.assess([json.loads(l)for l in (packet/(backend+'-corpus-responses.jsonl')).read_text().splitlines()],requests,reference,policy)
        history=h.assess([json.loads(l)for l in (packet/(backend+'-history-responses.jsonl')).read_text().splitlines()],inputs,root)
        out[backend]={'corpus':corpus,'history':history,'qualification_pass':corpus['qualification_pass']and history['qualification_pass']}
    out['overall_pass']=all(out[b]['qualification_pass']for b in ('native','wasm'));return out
if __name__=='__main__':print(json.dumps(run(),indent=2))
