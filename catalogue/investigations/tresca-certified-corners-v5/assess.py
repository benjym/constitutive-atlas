"""Conjunction of all unchanged material subgates plus exact failed-parent replay."""
from pathlib import Path
import importlib.util,json,gzip,struct
P=Path(__file__).parent;ROOT=P.parents[2]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def reversal(row,reference,root):
 exact=module('v5_reversal_membership',root/'docs/reviews/certified-spectral-range-v1/exact.py');failures=[]
 for key in ['ok','raw_ok','jet_ok','input_unchanged','recovery']:
  if row[key]is not True:failures.append(key)
 if row['ok']:
  if not exact.range_le(row['state'][:6],16.):failures.append('inadmissible-state')
  assert exact.range_le(row['state'][:6],16.)==exact.sturm_range_le(row['state'][:6],16.)
  for i,(got,wanted)in enumerate(zip(row['state'],reference['nearest_binary64_solution'])):
   if abs(got-wanted)/max(1.,abs(wanted))>2e-9:failures.append('update-'+str(i))
 assert len(row['state'])==12
 return {'qualification_pass':not failures,'failures':failures,'iterations':row['iterations'],'substeps':row['substeps'],'raw_and_jet_evaluable':row['raw_ok']and row['jet_ok']}
def run(packet=P,root=ROOT):
 c=module('v5_corpus',packet/'assess_corpus.py');h=module('v5_history',packet/'assess_history.py');l=module('v5_laboratory',packet/'assess_laboratory.py');out={}
 requests=json.loads((packet/'corpus-requests.json').read_text())['requests'];cp=json.loads((packet/'corpus-policy.json').read_text());ref=json.loads(gzip.decompress((root/'docs/reviews/tresca-pressure-split-v1/reference-full-row-p280.json.gz').read_bytes()));hi=json.loads((packet/'history-inputs.json').read_text());li=json.loads((packet/'laboratory-inputs.json').read_text());lr=json.loads((packet/'laboratory-references.json').read_text());lp=json.loads((packet/'laboratory-policy.json').read_text());rr=json.loads((packet/'reversal-reference.json').read_text())
 for b in ['native','wasm']:
  corpus=c.assess([json.loads(x)for x in(packet/(b+'-corpus-responses.jsonl')).read_text().splitlines()],requests,ref,cp)
  history=h.assess([json.loads(x)for x in(packet/(b+'-history-responses.jsonl')).read_text().splitlines()],hi,root)
  lab=l.assess([json.loads(x)for x in(packet/(b+'-laboratory-responses.jsonl')).read_text().splitlines()],li,lr,lp,root)
  checks=json.loads((packet/(b+'-checks-responses.jsonl')).read_text());rev=reversal(json.loads((packet/(b+'-reversal-responses.jsonl')).read_text()),rr,root)
  out[b]={'corpus':corpus,'history':history,'laboratory':lab,'checks':checks,'reversal':rev,'qualification_pass':corpus['qualification_pass']and history['qualification_pass']and lab['qualification_pass']and checks['pass']and rev['qualification_pass']}
 out['overall_pass']=all(out[b]['qualification_pass']for b in ['native','wasm']);return out
if __name__=='__main__':print(json.dumps(run(),indent=2))
