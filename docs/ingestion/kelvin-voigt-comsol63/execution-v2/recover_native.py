"""Parent-only CLI binding repair: reuse trajectories, recollect observations only."""
import argparse,copy,hashlib,json,subprocess
from pathlib import Path
import study
B=Path(__file__).resolve().parent;OLD=B.parent/'execution-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def load():
 study.verify_freeze();cases=json.loads((B/'cases.json').read_text())['cases'];oldcases=json.loads((OLD/'cases.json').read_text())['cases'];rows=json.loads((OLD/'native-raw.json').read_text());assert [c['id']for c in cases]==[c['id']for c in oldcases]==[r['id']for r in rows]
 for new,old in zip(cases,oldcases):
  expected=copy.deepcopy(old)
  if old['kind']=='observe':expected['argv']=['--initial'if v=='--current'else v for v in expected['argv']]
  assert new==expected,new['id']
 for c,r in zip(oldcases,rows):
  assert len(r['calls'])==2 and r['calls'][0]['stdout']==r['calls'][1]['stdout'],c['id']
  if c['kind']=='observe':assert all(json.loads(q['stdout'])=={'ok':False,'message':'option unsupported by timed mode: --current'}for q in r['calls']),c['id']
  if c['ok']and c['kind']=='direct':assert json.loads(r['observation'])=={'ok':False,'message':'option unsupported by timed mode: --current'},c['id']
 return cases,rows

def requests(cases,rows):
 planned=[]
 for c,r in zip(cases,rows):
  if c['kind']=='observe':planned.append(dict(id=c['id'],part='calls',repeats=2,argv=c['argv']))
  elif c['ok']and c['kind']=='direct':
   d=json.loads(r['calls'][0]['stdout']);assert d['ok'],c['id']
   argv=['--mode','observe-time','--model',study.M,'--parameters',study.csv(c['parameters']),'--initial',study.csv(d['state']),'--strain-rate',study.csv(c['rate']),'--start-time',str(c['time'])]
   planned.append(dict(id=c['id'],part='observation',repeats=1,argv=argv))
 return planned

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['inspect','recover']);p.add_argument('--solver',type=Path);p.add_argument('--solver-sha256');a=p.parse_args();cases,original=load();plan=requests(cases,original)
 if a.mode=='inspect':
  print(json.dumps({'compiled_calls_performed':0,'trajectory_call_records_reused':2*sum(c['kind']!='observe'for c in cases),'observe_cases_to_recollect':sum(c['kind']=='observe'for c in cases),'direct_observations_to_recollect':sum(c['ok']and c['kind']=='direct'for c in cases),'algebraic_calls_planned':sum(x['repeats']for x in plan),'requests':plan},indent=2));return
 assert a.solver and a.solver_sha256,'Parent must provide exact qualified solver path and SHA-256'
 assert sha(a.solver.read_bytes())==a.solver_sha256,'Solver identity mismatch'
 raw=B/'native-raw.json';provenance=B/'native-recovery-provenance.json';assert not raw.exists()and not provenance.exists(),'Refuse overwrite of retained recovery artifacts'
 rows=copy.deepcopy(original);record={'identity':'kelvin-native-observe-binding-recovery-v2','v1_raw_sha256':sha((OLD/'native-raw.json').read_bytes()),'v1_cases_sha256':sha((OLD/'cases.json').read_bytes()),'v2_cases_sha256':sha((B/'cases.json').read_bytes()),'v2_freeze_sha256':sha((B/'freeze.json').read_bytes()),'recollector_sha256':sha(Path(__file__).read_bytes()),'solver_sha256':a.solver_sha256,'policy':'Only failed algebraic observations recollected; every integration/schedule call stdout/stderr/returncode reused exactly','rows':[]}
 by={p['id']:p for p in plan}
 for c,r,old in zip(cases,rows,original):
  row_record={'id':c['id'],'original_row_sha256':sha(json.dumps(old,sort_keys=True,separators=(',',':')).encode()),'calls_reused':c['kind']!='observe','observation_recollected':c['ok']and c['kind']=='direct'}
  if c['id']in by:
   request=by[c['id']];new=[]
   for _ in range(request['repeats']):
    result=subprocess.run([str(a.solver),*request['argv']],capture_output=True,text=True,timeout=30);new.append({'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
   row_record['corrected_argv']=request['argv'];row_record['new_call_records']=new
   if request['part']=='calls':r['calls']=new
   else:r['observation']=new[0]['stdout']
  if c['kind']!='observe':assert r['calls']==old['calls'],c['id']
  row_record['recovered_row_sha256']=sha(json.dumps(r,sort_keys=True,separators=(',',':')).encode());record['rows'].append(row_record)
  raw.write_text(json.dumps(rows[:len(record['rows'])],indent=2)+'\n');provenance.write_text(json.dumps(record,indent=2)+'\n')
 record['complete']=True;record['recovered_raw_sha256']=sha(raw.read_bytes());provenance.write_text(json.dumps(record,indent=2)+'\n');print('Saved corrected observations and retained trajectory calls in',raw)
if __name__=='__main__':main()
