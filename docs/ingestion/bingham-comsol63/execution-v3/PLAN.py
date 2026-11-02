"""Prepare/check/freeze capped v3 candidates; source-only, never runs a material engine."""
import argparse,copy,datetime,hashlib,json,pathlib,shutil
BASE=pathlib.Path(__file__).resolve().parent;ROOT=BASE.parents[3];OLD=BASE.parent/'execution-v2'
M=100000/(2*10000000*.012*1024)
HELPERS=['study.py','collect_wasm.mjs','parity.py','oracle.py','synthetic_checks.py','expected-catalogue.json','reference-convergence.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 p=BASE/name; assert not p.exists(),f'Never overwrite {p}'
 p.write_text(json.dumps(value,indent=2)+'\n')
def prepare():
 for name in HELPERS:
  assert not (BASE/name).exists();shutil.copyfile(OLD/name,BASE/name)
 data=json.loads((OLD/'cases.json').read_text());data['identity']='bingham-be-schedule-v3'
 for c in data['cases']:
  val=min(c['specification']['solver']['maximum_step'],M)
  c['specification']['solver']['maximum_step']=val;c['args'][11]=val
  c['argv'][c['argv'].index('--max-time-step')+1]=str(val)
 write('cases.json',data)
def check():
 old=json.loads((OLD/'cases.json').read_text())['cases'];new=json.loads((BASE/'cases.json').read_text())['cases']
 assert len(old)==len(new)==136 and [c['id'] for c in old]==[c['id'] for c in new]
 rows=[]
 for x,y in zip(old,new):
  z=copy.deepcopy(y);val=min(x['specification']['solver']['maximum_step'],M)
  assert y['specification']['solver']['maximum_step']==y['args'][11]==val
  assert float(y['argv'][y['argv'].index('--max-time-step')+1])==val
  z['specification']['solver']['maximum_step']=x['specification']['solver']['maximum_step']
  z['args'][11]=x['args'][11];z['argv'][z['argv'].index('--max-time-step')+1]=x['argv'][x['argv'].index('--max-time-step')+1]
  assert z==x,(x['id'],'change beyond maximum_step projection')
  rows.append({'id':x['id'],'previous_maximum_step':x['specification']['solver']['maximum_step'],'new_maximum_step':val,'full_record_equal_after_only_three_cap_projections':True})
 for n in HELPERS:assert (BASE/n).read_bytes()==(OLD/n).read_bytes(),n
 return {'passed':True,'cases':136,'same_ids_and_order':True,'all_physics_references_gates_and_other_settings_unchanged':True,'copied_helper_hashes':{n:sha(BASE/n) for n in HELPERS},'v2_case_sha256':sha(OLD/'cases.json'),'v3_case_sha256':sha(BASE/'cases.json'),'maximum_step_formula':'100000/(2*10000000*.012*1024)','maximum_step_s':M,'records':rows,'compiled_calls':0}
def freeze(revision):
 lineage=check();write('lineage-check.json',lineage)
 sources=json.loads((OLD/'source-bindings.json').read_text())['source_files']
 for rel,h in sources.items():assert sha(ROOT/rel)==h,('source changed',rel)
 prior={str(p.relative_to(ROOT)):sha(p) for p in sorted(OLD.iterdir()) if p.is_file()}
 analysis={str(p.relative_to(ROOT)):sha(p) for p in sorted((BASE.parent/'step-bound-analysis-v1').iterdir()) if p.is_file()}
 write('source-bindings.json',{'identity':'bingham-be-schedule-v3-source-bindings','source_files':sources,'copied_helpers':lineage['copied_helper_hashes'],'v2_snapshot':prior,'analysis':analysis,'disclosure':'Post-v1 and post-v2 observations. Snapshot hashes of potentially ongoing v2 outputs are context, not complete campaign claims. Source-derived scalar event bound motivates cap only; no overall accuracy guarantee. Frozen before new v3 requests.'})
 synthetic=json.loads((BASE/'synthetic-checks.json').read_text());assert synthetic['positive_synthetic_cases']==136 and synthetic['negative_mutations_rejected']==25 and synthetic['compiled_calls']==0
 own={str(p.relative_to(ROOT)):sha(p) for p in sorted(BASE.iterdir()) if p.is_file() and not p.name.startswith('freeze-')}
 write('freeze-'+revision+'.json',{'identity':'bingham-be-schedule-execution-v3-'+revision,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_new_v3_compiled_calls':True,'prior_bingham_compiled_observations_exist':True,'cases':136,'repeats_per_case':2,'sole_request_change':'maximum_step=min(previous maximum_step,100000/(2*10000000*.012*1024))','qualified_interface_proposed':'atlas_run_schedule BE only; direct midpoint excluded','files':own,'source_bindings_sha256':sha(BASE/'source-bindings.json'),'independent_prospective_review_required_before_calls':True})
 print(json.dumps({'freeze_sha256':sha(BASE/('freeze-'+revision+'.json')),'cases':136,'helpers_byte_identical':True},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','check','freeze']);p.add_argument('--revision',default='v1');a=p.parse_args()
 if a.action=='prepare':prepare();print(json.dumps(check(),indent=2))
 elif a.action=='check':print(json.dumps(check(),indent=2))
 else:freeze(a.revision)
