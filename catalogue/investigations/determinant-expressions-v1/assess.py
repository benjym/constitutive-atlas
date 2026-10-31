"""Frozen exact generated-context gate; no constitutive or determinant equations."""
import argparse,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def unique(pairs):
 out={}
 for k,v in pairs:
  if k in out:raise ValueError('duplicate JSON key')
  out[k]=v
 return out
def read(p):return json.loads(Path(p).read_text(),object_pairs_hook=unique)
def decoded(text):return json.loads(text,object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def exact(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 return a==b
def check_row(row,case,identity,history=False):
 expected=dict(case['expectation'],id=case['id'],model_id=identity[0],catalogue_hash=identity[1])
 assert exact(row,expected),'closed exact response/status/bits/derivatives/transaction'
def assessment():
 freeze=read(HERE/'prospective-freeze.json')
 for name,pin in freeze['files'].items():assert sha(ROOT/name)==pin,name
 cases=read(HERE/'cases.json');histories=read(HERE/'history-cases.json');programs=read(HERE/'history-programs.json');protocol=read(HERE/'protocol.json');catalogue=read(HERE/'generated/models.json')
 lines=(HERE/'requests.tsv').read_text().splitlines();assert lines==['M\t'+str(i)for i in range(len(cases))]+['H\t'+str(i)for i in range(len(histories))]
 assert len(cases)==protocol['model_cases']==1719 and len(histories)==protocol['history_cases']==18
 assert len({c['id']for c in cases+histories})==len(lines)
 parsed={};failures=[]
 for role in ('native','wasm'):
  build=read(HERE/(role+'-build.json'));execution=read(HERE/(role+'-execution.json'));rawpath=HERE/(role+'-raw.json')
  assert build['freeze_sha256']==execution['freeze_sha256']==sha(HERE/'prospective-freeze.json')
  assert execution['build_sha256']==sha(HERE/(role+'-build.json'))and type(execution['returncode'])is int and execution['returncode']==0
  for name,pin in build['artifacts'].items():assert sha(Path(pin['path']))==pin['sha256'],name
  for c in build['commands']:
   assert sha(ROOT/c['path'])==c['sha256'];d=read(ROOT/c['path']);assert d['returncode']==0
  assert sha(rawpath)==execution['raw_sha256'];raw=read(rawpath)
  if role=='native':
   argv=[build['artifacts']['native']['path']]
   assert execution['argv']==argv and set(raw)=={'argv','stdin','stdout','stderr','returncode'}
   assert raw['argv']==argv and raw['stdin']=='\n'.join(lines)+'\n'and raw['returncode']==0 and raw['stderr']==''
   responses=raw['stdout'].splitlines()
  else:
   argv=['node',str(HERE/'collect_wasm.mjs'),build['artifacts']['loader']['path'],str(HERE/'requests.tsv'),str(rawpath)]
   assert execution['argv']==argv and execution['stderr']==''
   assert len(raw)==len(lines)
   for row,line in zip(raw,lines):assert set(row)=={'input','raw'}and row['input']==line
   responses=[row['raw']for row in raw]
  assert len(responses)==len(lines);rows=[];controls={}
  for index,(text,case)in enumerate(zip(responses,cases+histories)):
   row=decoded(text);history=index>=len(cases)
   if history:
    p=programs[case['program']];identity=(p['id'],hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest())
   else:
    model=catalogue['models'][case['model']];assert model['id']==case['model_id'];identity=(model['id'],catalogue['sha256'])
   try:
    check_row(row,case,identity,history)
    if'recovery_of'in case:
     assert index>0 and(cases+histories)[index-1]['id']==case['after_rejection'],'immediate recovery order'
     assert controls[case['after_rejection']]['ok']is False,'recovery follows rejection'
     assert exact(row,dict(controls[case['recovery_of']],id=case['id'])),'complete same-instance baseline recovery'
    if history and case['id'].endswith('/recover'):
     assert exact(row,dict(controls[case['id'].removesuffix('/recover')+'/good'],id=case['id'])),'history recovery'
   except AssertionError as exc:failures.append({'role':role,'case':case['id'],'gate':str(exc)})
   controls[case['id']]=row;rows.append(row)
  parsed[role]=rows
 for a,b in zip(parsed['native'],parsed['wasm']):
  if not exact(a,b):failures.append({'case':a['id'],'gate':'complete native/Wasm parity'})
 return {'outcome':'failed'if failures else'passed','failures':failures,'model_cases':len(cases),'history_cases':len(histories),'calls_per_backend':len(lines),'synthetic_models':protocol['models'],'model_contexts':sorted({c['context']for c in cases}),'scalar_AD_columns':38,'explicit_recovery_pairs':sum('recovery_of'in c for c in cases),'history_recovery_triplets':6,'all_decoded_responses_exact':not failures,'protocol_sha256':sha(HERE/'protocol.json'),'freeze_sha256':sha(HERE/'prospective-freeze.json'),'constitutive_model_integrated':False,'scientific_admission':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();d=assessment();a.output.write_text(json.dumps(d,indent=2)+'\n');print(d['outcome']);raise SystemExit(d['outcome']!='passed')
