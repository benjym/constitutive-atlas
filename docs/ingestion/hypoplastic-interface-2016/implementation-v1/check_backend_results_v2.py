#!/usr/bin/env python3
"""V2: explicit finite/full-shape/component bounds; original V1 remains retained."""
import argparse,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def require(condition,message):
 if not condition:raise AssertionError(message)
def number(x):return type(x) in (int,float) and math.isfinite(x)
def array(x,n,label):
 require(type(x) is list and len(x)==n,label+' shape')
 for i,v in enumerate(x):require(number(v),f'{label}[{i}] must be finite numeric')
def compare(actual,expected,scales,tolerance,label):
 array(actual,len(scales),label);array(expected,len(scales),label+' expected')
 errors=[]
 for i in range(len(scales)):
  require(number(scales[i]) and scales[i]>0,label+' scale')
  delta=abs(actual[i]-expected[i])/scales[i]
  require(number(delta) and delta<=tolerance,f'{label}[{i}] exceeds frozen tolerance: {delta}')
  errors.append(delta)
 return max(errors,default=0.)
def assess(report):
 req=ROOT/'backend-requests.json';expectpath=ROOT/'backend-expectations.json'
 p=json.loads(req.read_text());expect=json.loads(expectpath.read_text())
 digest=hashlib.sha256(req.read_bytes()).hexdigest()
 require(type(report) is dict and report.get('request_sha256')==digest==expect['requests_sha256'],'request identity')
 require(expect['source_reference_sha256']==hashlib.sha256((ROOT/'references.json').read_bytes()).hexdigest(),'reference identity')
 require(type(report.get('rows')) is list,'rows shape')
 requests=p['requests'];expectedids={q['id'] for q in requests}
 require(len(expectedids)==len(requests),'duplicate frozen request ids')
 require(len(report['rows'])==len(requests),'row count')
 require(all(type(r) is dict and type(r.get('id')) is str for r in report['rows']),'row/id type')
 ids=[r['id'] for r in report['rows']]
 require(len(set(ids))==len(ids) and set(ids)==expectedids,'exact unique request ID set')
 require(set(expect['expected'])==expectedids,'frozen expectation ID set')
 tolerance=expect['scaled_tolerance'];require(number(tolerance) and tolerance>0,'frozen tolerance')
 rows={r['id']:r for r in report['rows']};details=[]
 for q in requests:
  label=q['id'];r=rows[label];e=expect['expected'][label]
  require(type(r.get('status')) is int and r['status'] in (0,1) and r['status']==e['status'],label+' status')
  array(r.get('state'),5,label+' state');array(r.get('observables'),8,label+' observables')
  require(number(r.get('coordinate')),label+' coordinate must be finite numeric')
  if e['status']==0:
   require(r['state']==[-1234567.]*5 and r['observables']==[-1234567.]*8 and r['coordinate']==-7654321.,label+' failure sentinel mutation')
   details.append({'id':label,'expected_failure_preserved':True});continue
  stateerror=compare(r['state'],e['state'],expect['state_scales'],tolerance,label+' state')
  obserror=compare(r['observables'],e['observables'],[100000.]*7+[1.],tolerance,label+' observables')
  require(number(e['coordinate']) and r['coordinate']==e['coordinate'],label+' coordinate mismatch')
  # Check the component binding itself, in addition to independent endpoint bounds.
  sn,sp,tx,tz,void=r['state']
  bound=[sn,sp,sp,math.sqrt(2)*tx,0.,math.sqrt(2)*tz,(sn+2*sp)/3,void]
  array(bound,8,label+' bound observables')
  for i in range(8):require(r['observables'][i]==bound[i],f'{label} exact state/observable binding[{i}]')
  details.append({'id':label,'state_scaled_error':stateerror,'observable_scaled_error':obserror})
 for a,b in expect['repeat_pairs']:
  for key in ['state','coordinate','observables']:require(rows[a][key]==rows[b][key],f'exact repeat {a} {key}')
 for key in ['state','coordinate','observables']:
  require(rows['recovery-after-trial-budget'][key]==rows['x_shear-segment1-repeat1'][key],'exact rollback recovery '+key)
 return {'passed':True,'checker_version':2,'requests':len(rows),'repeat_pairs':len(expect['repeat_pairs']),'negative_cases':sum(not x['status'] for x in expect['expected'].values()),'full_finite_state_stress_and_bindings_checked':True,'rollback_sentinels_and_recovery_checked':True,'rows':details,'scope':'Bounded source-reconciled behavior qualification; not independent scientific approval.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('reports',nargs='+',type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();results=[]
 for f in a.reports:results.append({'report':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'assessment':assess(json.loads(f.read_text()))})
 a.output.write_text(json.dumps({'passed':True,'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'results':results},indent=2,allow_nan=False)+'\n');print('All frozen backend checks passed (finite/full-component V2)')
if __name__=='__main__':main()
