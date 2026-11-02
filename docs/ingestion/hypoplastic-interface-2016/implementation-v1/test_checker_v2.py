#!/usr/bin/env python3
"""Synthetic checker fault injection, with no constitutive/backend calls."""
import copy,hashlib,json
from pathlib import Path
from check_backend_results_v2 import assess
ROOT=Path(__file__).resolve().parent

def main():
 e=json.loads((ROOT/'backend-expectations.json').read_text())
 rows=[{'id':k,'status':v['status'],'state':v.get('state',[-1234567.]*5),'coordinate':v.get('coordinate',-7654321.),'observables':v.get('observables',[-1234567.]*8)} for k,v in e['expected'].items()]
 report={'request_sha256':e['requests_sha256'],'rows':rows};assess(report);idx=next(i for i,x in enumerate(rows) if x['id']=='zero-progress-identity');tests=[]
 def rejects(label,mutator):
  r=copy.deepcopy(report);mutator(r)
  try:assess(r)
  except AssertionError as exc:tests.append({'case':label,'rejected':True,'reason':str(exc)});return
  raise AssertionError('unexpected acceptance '+label)
 for field,n in [('state',5),('observables',8)]:
  for j in range(n):
   for bad in [float('nan'),float('inf'),-float('inf')]:rejects(f'{field}{j}_{str(bad)}',lambda r,field=field,j=j,bad=bad:r['rows'][idx][field].__setitem__(j,bad))
 for label,mutator in [
 ('coordinate_nan',lambda r:r['rows'][idx].__setitem__('coordinate',float('nan'))),
 ('short_state',lambda r:r['rows'][idx].__setitem__('state',[1.])),
 ('long_observables',lambda r:r['rows'][idx]['observables'].append(0.)),
 ('bool_component',lambda r:r['rows'][idx]['state'].__setitem__(4,True)),
 ('string_component',lambda r:r['rows'][idx]['state'].__setitem__(4,'0.67')),
 ('bool_status',lambda r:r['rows'][idx].__setitem__('status',True)),
 ('duplicate_id',lambda r:r['rows'][idx].__setitem__('id',r['rows'][0]['id'])),
 ('missing_row',lambda r:r['rows'].pop()),
 ('unknown_id',lambda r:r['rows'][idx].__setitem__('id','unknown')),
 ('wrong_binding',lambda r:r['rows'][idx]['observables'].__setitem__(7,r['rows'][idx]['observables'][7]+1e-7)),
 ('outside_frozen_bound',lambda r:r['rows'][idx]['state'].__setitem__(4,r['rows'][idx]['state'][4]+3e-6)),
 ]:rejects(label,mutator)
 out={'synthetic_reference_report_accepted':True,'faults_rejected':len(tests),'checker_sha256':hashlib.sha256((ROOT/'check_backend_results_v2.py').read_bytes()).hexdigest(),'tests':tests,'compiled_or_material_calls':0}
 (ROOT/'checker-v2-fault-results.json').write_text(json.dumps(out,indent=2)+'\n');print('V2 baseline accepted;',len(tests),'synthetic fault injections rejected')
if __name__=='__main__':main()
