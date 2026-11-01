"""Saved-only full qualification replay; original inputs and subgates remain immutable."""
from pathlib import Path
import importlib.util,json,hashlib,gzip,sys
P=Path(__file__).parent;ROOT=P.parents[2]
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify():
 for n,h in json.loads((P/'prospective-freeze.json').read_text())['files'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
 for n,h in json.loads((P/'source-pins.json').read_text()).items():checked_receipt(ROOT,str((P/'source-pins.json').relative_to(ROOT)),n,h)
 v4=ROOT/'catalogue/investigations/tresca-solution-constraints-v4';lab=ROOT/'catalogue/investigations/tresca-laboratory-v1'
 for n in ['corpus.inc','history.inc','checks.inc','assess_corpus.py','assess_history.py','corpus-policy.json','corpus-requests.json','corpus-requests.txt.gz','history-inputs.json','history-policy.json','history-requests.txt']:assert (P/n).read_bytes()==(v4/n).read_bytes(),n
 for original,copied in [('assess.py','assess_laboratory.py'),('inputs.json','laboratory-inputs.json'),('references.json','laboratory-references.json'),('policy.json','laboratory-policy.json'),('requests.txt','laboratory-requests.txt'),('reference.py','laboratory_reference.py')]:assert (P/copied).read_bytes()==(lab/original).read_bytes(),copied
 wires={'corpus':gzip.decompress((P/'corpus-requests.txt.gz').read_bytes()),'history':(P/'history-requests.txt').read_bytes(),'laboratory':(P/'laboratory-requests.txt').read_bytes()}
 for mode,data in wires.items():assert hashlib.sha256(data).hexdigest()==json.loads((P/'prospective-freeze.json').read_text())['wire_sha256'][mode]
 catalogue=json.loads((P/'generated-original/models.json').read_text());model=catalogue['models'][0]
 for b in ['native','wasm']:
  for phase in ['configure','build','corpus-execution','history-execution','checks-execution','laboratory-execution','reversal-execution']:assert json.loads((P/(b+'-'+phase+'-process.json')).read_text())['returncode']==0
  assert json.loads((P/(b+'-build-process.json')).read_text())['command'][-4:]==['--target','atlas_tresca_certified_corners','--parallel','1']
  for mode in ['corpus','history','checks','laboratory','reversal']:assert json.loads((P/(b+'-'+mode+'-execution-process.json')).read_text())['stdout']==(P/(b+'-'+mode+'-responses.jsonl')).read_text()
  for row in map(json.loads,(P/(b+'-laboratory-responses.jsonl')).read_text().splitlines()):
   for response in [row['response'],row['recovery']]:
    if 'model'in response:assert response['model']==model['id']and response['catalogue_hash']==catalogue['sha256']
 report=module('v5_full_replay',P/'assess.py').run();assert report==json.loads((P/'assessment.json').read_text())and report['overall_pass']
 for b in ['native','wasm']:
  a=report[b];assert a['corpus']['requests']==219 and a['corpus']['derivative_components']==27816 and a['history']['accepted']==12
  assert a['laboratory']['requests']==29 and a['laboratory']['reference_components']==1746 and a['laboratory']['admissibility_checks']==97 and a['laboratory']['recoveries']==29
  assert a['reversal']['qualification_pass']and a['checks']['pass']
 return report
if __name__=='__main__':print(json.dumps({'saved_evidence_verified':True,'overall_pass':verify()['overall_pass'],'public_installation':False}))
