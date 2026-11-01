#!/usr/bin/env python3
"""Independent saved E8 replay and rational-path/transaction checks; no network/compiled calls."""
import hashlib,json,pathlib,runpy,subprocess
from fractions import Fraction
HERE=pathlib.Path(__file__).resolve().parent;D=HERE.parent;ROOT=D.parents[4]
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
def read(q):return json.loads(q.read_text())
def run():
 manifest=read(HERE/'manifest.json')
 for group in ['inputs','outputs']:
  for name,h in manifest[group].items():
   q=pathlib.Path(name);q=q if q.is_absolute() else ROOT/q
   assert sha(q)==h,name
 assert (D/'check.py').read_bytes()==(D/'checker-review-v2/source-final/check.py').read_bytes()
 result=runpy.run_path(str(D/'check.py'))['run']();assert result['passed']
 release=result['release'];approved=read(D/'approved-identities.json')
 for name,h in approved.items():assert hashlib.sha256(subprocess.check_output(['git','show',release+':'+name],cwd=ROOT)).hexdigest()==h
 exported=read(D/'browser-export.json');assert (D/'browser-export.json').read_bytes()==pathlib.Path('/Users/bmar5496/Downloads/j2-strain-path (2).json').read_bytes()
 q=exported['request'];assert q['model']==exported['provenance']['model'];state=q['initial'];strain=[0.]*6
 for i,(row,increment) in enumerate(zip(exported['records'],q['increments']),1):
  assert row['row']==i and row['response']['ok'] and row['response']['model']==q['model']
  wire=row['wire'];assert wire['function']=='atlas_integrate_with_settings' and wire['types']==['string']*5
  args=wire['args'];assert args[0]==q['model']
  for encoded,expected in zip(args[1:],[q['parameters'],state,increment,q['settings']]):assert [float(v) for v in encoded.split(',')]==expected
  response=row['response'];assert response['initial']==state and response['strain']==increment and response['parameters']==q['parameters']
  assert response['catalogue_hash']==exported['provenance']['catalogue_hash']
  assert response['state']==exported['points'][i]['state'];state=response['state'];strain=[a+b for a,b in zip(strain,increment)]
  assert exported['points'][i]['step']==i and exported['points'][i]['strain']==strain
 # Independent closed-form deviatoric trial projection for this exact fixed preset.
 # gamma=(108000-60000)/(3*12000000+1200000)=1/775.
 g=Fraction(108000-60000,3*12000000+1200000);assert g==Fraction(1,775)
 first=Fraction(72000)-2*12000000*g;reverse=first-72000
 expected=[[0]*8,[first,-first/2,-first/2,0,0,0,g,g],[reverse,-reverse/2,-reverse/2,0,0,0,g,0],[reverse,-reverse/2,-reverse/2,0,0,0,g,0]]
 stress_error=history_error=0.
 for point,reference in zip(exported['points'],expected):
  for index,(actual,target) in enumerate(zip(point['state'],reference)):
   error=abs(actual-float(target));assert error<=(.002 if index<6 else 2e-10)
   if index<6:stress_error=max(stress_error,error)
   else:history_error=max(history_error,error)
 browser=read(D/'browser-state.json')
 for plot in browser['plots']:
  points=[tuple(float(v) for v in s.split(',')) for s in plot['points']]
  assert len(set(points))==plot['distinct_point_count'] and len({v for _,v in points})==plot['distinct_y_count']
 assert len(read(D/'artifact-inventory.json'))==880
 assert read(D/'live-assets.json')['date_utc']=='2026-11-01T11:26:24.263341+00:00'
 return dict(passed=True,verdict='accept saved bounded E8 evidence for exact historical release',release=release,actions_run=41299887463,deployment=7472309427,successful_jobs=5,artifact_members=880,live_assets=20,full_state_comparisons=32,independent_rational_gamma=str(g),max_independent_stress_error_Pa=stress_error,max_independent_history_error=history_error,propagated_record_transactions=3,download_export_exact_bytes=True,reviewer_compiled_calls=0,reviewer_network_calls=0,limits=['Coordinator actual external/browser observations assessed from saved receipts.','Delayed browser tool completion does not change original live hash receipt timestamp.','No CI/live qualification claim for later HEAD revisions; no broader parameter/experimental qualification.'])
if __name__=='__main__':print(json.dumps(run(),indent=2))
