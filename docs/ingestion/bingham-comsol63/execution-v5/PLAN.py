"""Source-only v5 versioned-profile preparation/check/freeze; no model execution."""
import argparse,datetime,hashlib,json,pathlib,shutil
B=pathlib.Path(__file__).resolve().parent;R=B.parents[3]
OLD=pathlib.Path('/private/tmp/atlas-schedule-predictor-v1');REL=pathlib.Path('docs/ingestion/bingham-comsol63');PROFILE=pathlib.Path('docs/investigations/physical-time-v2-profile-v1/FREEZE.json')
COPIES=['cases.json','study.py','collect_wasm.mjs','parity.py','oracle.py','synthetic_checks.py','expected-catalogue.json','reference-convergence.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,d):
 p=B/name;assert not p.exists(),f'Never overwrite {p}';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def prepare():
 old=OLD/REL/'execution-v4'
 for n in COPIES:assert not (B/n).exists();shutil.copyfile(old/n,B/n)
 for n in ['PLAN.md','source-bindings.json','freeze-v1.json','prior-v3-source-bindings.json']:
  q=B/'prior-v4'/n;q.parent.mkdir(exist_ok=True);assert not q.exists();shutil.copyfile(old/n,q)
 # Missing historical plan documents are exact archival input copies, not active runtime files.
 historical=json.loads((old/'source-bindings.json').read_text())['source_files']
 for p,h in historical.items():
  if not (R/p).exists():
   assert p.startswith('docs/'),('missing executable input',p)
   src=OLD/p;assert sha(src)==h
   dest=B/'archival-inputs'/p;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(src,dest)

def check():
 old=OLD/REL/'execution-v4';oldbinding=json.loads((old/'source-bindings.json').read_text());oldsrc=oldbinding['source_files']
 for n in COPIES:assert (B/n).read_bytes()==(old/n).read_bytes(),n
 priorfreeze=json.loads((old/'freeze-v1.json').read_text())
 for n in COPIES:assert sha(B/n)==priorfreeze['files'][str(REL/'execution-v4'/n)],('prior frozen copy mismatch',n)
 cases=json.loads((B/'cases.json').read_text())['cases'];assert len(cases)==136 and len({c['id'] for c in cases})==136
 profile=json.loads((R/PROFILE).read_text());assert sha(R/PROFILE)=='b308f1e965c9c28affeae89a6a47fb3be944313dc5f3593e51b351d40cddcca6'
 for p,h in profile['files'].items():assert sha(R/p)==h,('profile freeze mismatch',p)
 permitted={'CMakeLists.txt','cmake/bingham/CMakeLists.txt','cpp/include/atlas/schedule.hpp'}
 current={};deltas=[];archives={}
 for p,h in oldsrc.items():
  q=R/p
  if q.exists():
   actual=sha(q);current[p]=actual
   if actual!=h:
    assert p in permitted,(p,'unpermitted existing source delta')
    assert actual==profile['files'][p]
    deltas.append({'path':p,'v4_sha256':h,'v5_sha256':actual})
  else:
   assert p.startswith('docs/')
   archived=B/'archival-inputs'/p;assert sha(archived)==h
   archives[p]={'local_archival_path':str(archived.relative_to(R)),'sha256':h,'classification':'immutable historical input; not live source path'}
 assert {d['path'] for d in deltas}==permitted
 for p,h in profile['files'].items():current[p]=h
 header='runtimes/physical-time-v2/include/atlas/schedule.hpp'
 assert sha(R/header)==oldsrc['cpp/include/atlas/schedule.hpp']
 original=json.loads((old/'prior-v3-source-bindings.json').read_text())['source_files']
 assert sha(R/'cpp/include/atlas/schedule.hpp')==original['cpp/include/atlas/schedule.hpp']
 # Exact prospective include order, before any actual dependency-file proof is available.
 rootcm=(R/'CMakeLists.txt').read_text();bcm=(R/'cmake/bingham/CMakeLists.txt').read_text()
 for target in ['atlas_time_solver','atlas_time_tests','atlas_schedule_predictor_tests']:
  assert f'target_include_directories({target} PRIVATE runtimes/physical-time-v2/include cpp/include ' in rootcm,target
 assert '"${ATLAS_ROOT}/runtimes/physical-time-v2/include" "${ATLAS_ROOT}/cpp/include"' in bcm
 return {'passed':True,'cases':136,'entire_cases_file_byte_identical_to_v4':True,'case_sha256':sha(B/'cases.json'),'helpers_byte_identical':{n:sha(B/n) for n in COPIES[1:]},'source_files':current,'archival_inputs':archives,'permitted_existing_deltas':deltas,'profile_freeze':{'path':str(PROFILE),'sha256':sha(R/PROFILE)},'versioned_header_equals_v4_predictor_header':True,'common_header_equals_original_v3_legacy_header':True,'prospective_include_order_checked':True,'actual_build_selection_proof_pending':True,'compiled_calls':0}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','check','freeze']);ap.add_argument('--revision',default='v1');a=ap.parse_args()
 if a.action=='prepare':prepare();print(json.dumps(check(),indent=2));return
 report=check()
 if a.action=='check':print(json.dumps(report,indent=2));return
 put('lineage-check.json',report)
 syn=json.loads((B/'synthetic-checks.json').read_text());assert syn['positive_synthetic_cases']==136 and syn['negative_mutations_rejected']==25 and syn['compiled_calls']==0
 provenance={str(p.relative_to(B)):sha(p) for folder in ['prior-v4','archival-inputs'] for p in sorted((B/folder).rglob('*')) if p.is_file()}
 put('source-bindings.json',{'identity':'bingham-execution-v5-versioned-profile-source-bindings','source_files':report['source_files'],'archival_inputs':report['archival_inputs'],'prior_inputs':provenance,'permitted_existing_deltas':report['permitted_existing_deltas'],'profile_freeze':report['profile_freeze'],'case_and_helpers_byte_identical_to_v4':True,'source_capsule_note':'Original b529 study compiler/package capsule retained. This is not the current release-wide source closure; later integration must preserve accepted release atlas/cpp/schema and separately verify normal-generator metadata equality and exact retained asset receipts.','no_future_artifacts_repinned':True,'actual_profile_dependency_proof_required_before_calls':True})
 own={str(p.relative_to(R)):sha(p) for p in sorted(B.rglob('*')) if p.is_file() and not p.name.startswith('freeze-')}
 put('freeze-'+a.revision+'.json',{'identity':'bingham-versioned-physical-time-v2-execution-v5-'+a.revision,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_new_v5_compiled_calls':True,'prior_bingham_and_generic_development_observations_exist':True,'v4_accepted_never_tested_as_reported_by_parent':True,'cases':136,'repeats_per_case':2,'case_requests_and_helpers_byte_identical_to_v4':True,'settings_physics_references_gates_unchanged':True,'profile_freeze_sha256':sha(R/PROFILE),'source_bindings_sha256':sha(B/'source-bindings.json'),'independent_prospective_review_required':True,'files':own})
 print(json.dumps({'freeze_sha256':sha(B/('freeze-'+a.revision+'.json')),'source_files':len(report['source_files']),'case_sha256':sha(B/'cases.json')},indent=2))
if __name__=='__main__':main()
