#!/usr/bin/env python3
"""Check generic native/Wasm transport rows against frozen independent references."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def assess(report):
 req=ROOT/'backend-requests.json';p=json.loads(req.read_text());expect=json.loads((ROOT/'backend-expectations.json').read_text());assert report['request_sha256']==hashlib.sha256(req.read_bytes()).hexdigest()==expect['requests_sha256']
 assert len(report['rows'])==len(p['requests'])
 rows={r['id']:r for r in report['rows']};assert len(rows)==len(report['rows']);details=[]
 for q in p['requests']:
  r=rows[q['id']];e=expect['expected'][q['id']];assert r['status']==e['status'],q['id']
  if not e['status']:
   assert r['state']==[-1234567.]*len(q['state']) and r['observables']==[-1234567.]*q['observable_count'] and r['coordinate']==-7654321.,q['id']
   details.append({'id':q['id'],'expected_failure_preserved':True});continue
  delta=max(abs(x-y)/s for x,y,s in zip(r['state'],e['state'],expect['state_scales']))
  obsdelta=max(abs(x-y)/s for x,y,s in zip(r['observables'],e['observables'],[100000.]*7+[1.]))
  assert len(r['state'])==5 and len(r['observables'])==8 and delta<=expect['scaled_tolerance'] and obsdelta<=expect['scaled_tolerance'],(q['id'],delta,obsdelta)
  assert r['coordinate']==e['coordinate'],q['id']
  details.append({'id':q['id'],'state_scaled_error':delta,'observable_scaled_error':obsdelta})
 for a,b in expect['repeat_pairs']:
  assert all(rows[a][key]==rows[b][key] for key in ['state','coordinate','observables']),('repeat mismatch',a,b)
 # Separate successful recovery is compared to the identical normal x-shear request.
 a=rows['recovery-after-trial-budget'];b=rows['x_shear-segment1-repeat1']
 assert all(a[k]==b[k] for k in ['state','coordinate','observables'])
 return {'passed':True,'requests':len(rows),'repeat_pairs':len(expect['repeat_pairs']),'negative_cases':sum(not x['status'] for x in expect['expected'].values()),'full_state_and_stress_checked':True,'rollback_sentinels_and_recovery_checked':True,'rows':details,'scope':'Bounded source-reconciled behavior qualification; not independent scientific approval.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('reports',nargs='+',type=Path);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();results=[]
 for f in a.reports:results.append({'report':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'assessment':assess(json.loads(f.read_text()))})
 a.output.write_text(json.dumps({'passed':True,'results':results},indent=2)+'\n');print('All frozen backend checks passed')
if __name__=='__main__':main()
