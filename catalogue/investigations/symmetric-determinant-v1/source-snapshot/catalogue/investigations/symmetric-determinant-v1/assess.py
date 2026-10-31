"""Exact frozen primitive gate; no determinant/source equations."""
import argparse,hashlib,json,math,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));HERE=Path(__file__).resolve().parent
from atlas.numerics.determinant import determinant,VERSION

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bits(x):return struct.pack('>d',x).hex()
def hex_bits(x):return bits(float.fromhex(x))
def expected_jet(case):
 e=case['expectation']
 return [hex_bits(e['value_hex'])]+[hex_bits(v)for v in e['derivatives_hex']]if e['ok']else[bits(17.25)]+[bits(-64.+j/2)for j in range(38)]
def check_row(row,case):
 assert set(row)=={'id','version','double_ok','double_bits','double_unchanged','jet_ok','jet_unchanged','jet_bits'},'raw response shape'
 assert row['id']==case['id']and row['version']==VERSION,'response identity'
 assert type(row['jet_ok'])is bool and row['jet_ok']is case['expectation']['ok'],'Jet status'
 assert row['jet_bits']==expected_jet(case),'exact Jet output bits'
 assert type(row['jet_unchanged'])is bool and(row['jet_ok']or row['jet_unchanged']),'unchanged rejected Jet output'
 e=case['primal_expectation'];assert type(row['double_ok'])is bool and row['double_ok']is e['ok'],'primal status'
 assert row['double_bits']==(hex_bits(e['hex'])if e['ok']else bits(-123.5)),'exact primal output bits'
 assert type(row['double_unchanged'])is bool and(row['double_ok']or row['double_unchanged']),'unchanged rejected primal output'

def assess():
 f=json.loads((HERE/'prospective-freeze.json').read_text())
 for name,pin in f['files'].items():assert sha(ROOT/name)==pin,name
 protocol=json.loads((HERE/'protocol.json').read_text());lines=(HERE/'requests.tsv').read_text().splitlines();cases=protocol['cases'];assert len(lines)==len(cases)==124
 parsed={};failures=[]
 for role in ('native','wasm'):
  build=json.loads((HERE/(role+'-build.json')).read_text());execution=json.loads((HERE/(role+'-execution.json')).read_text())
  assert build['freeze_sha256']==execution['freeze_sha256']==sha(HERE/'prospective-freeze.json')
  assert execution['build_sha256']==sha(HERE/(role+'-build.json'))and execution['returncode']==0
  for name,pin in build['artifacts'].items():assert sha(Path(pin['path']))==pin['sha256'],name
  for command in build['commands']:
   assert sha(ROOT/command['path'])==command['sha256'];assert json.loads((ROOT/command['path']).read_text())['returncode']==0
  rawpath=HERE/(role+'-raw.json');assert sha(rawpath)==execution['raw_sha256']
  raw=json.loads(rawpath.read_text())
  if role=='native':
   assert set(raw)=={'argv','stdin','stdout','stderr','returncode'}and raw['returncode']==0
   assert raw['argv']==[build['artifacts']['native']['path']]and raw['stdin']=='\n'.join(lines)+'\n'
   responses=raw['stdout'].splitlines()
  else:
   assert len(raw)==len(lines)
   for row,line in zip(raw,lines):assert set(row)=={'input','raw'}and row['input']==line
   responses=[row['raw']for row in raw]
  assert len(responses)==len(cases);rows=[];controls={}
  for text,case in zip(responses,cases):
   row=json.loads(text)
   try:
    check_row(row,case)
    if'recovery_of'in case:
     prior=controls[case['recovery_of']];expected=dict(prior,id=case['id']);assert row==expected,'same-instance recovery'
   except AssertionError as exc:failures.append({'role':role,'case':case['id'],'gate':str(exc)})
   controls[case['id']]=row;rows.append(row)
  parsed[role]=rows
 for a,b in zip(parsed['native'],parsed['wasm']):
  if a!=b:failures.append({'case':a['id'],'gate':'complete native/Wasm response parity'})
 python=[]
 for case in cases:
  try:value=determinant([float(x)for x in case['values']]);row={'id':case['id'],'ok':True,'bits':bits(value)}
  except ValueError as exc:row={'id':case['id'],'ok':False,'error':str(exc)}
  e=case['primal_expectation']
  if row['ok']is not e['ok']or(row['ok']and row['bits']!=hex_bits(e['hex'])):failures.append({'role':'python','case':case['id'],'gate':'exact primal result'})
  python.append(row)
 return {'outcome':'failed'if failures else'passed','failures':failures,'unique_reference_cases':78,'ordered_calls_per_backend':124,'rejection_recovery_pairs':46,'accepted_Jet_calls':sum(c['expectation']['ok']for c in cases),'derivative_columns':38,'all_outputs_bit_exact':not failures,'python':python,'protocol_sha256':sha(HERE/'protocol.json'),'freeze_sha256':sha(HERE/'prospective-freeze.json'),'DSL_integrated':False,'model_integrated':False,'scientific_admission':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();result=assess();a.output.write_text(json.dumps(result,indent=2)+'\n');print(result['outcome']);raise SystemExit(result['outcome']!='passed')
