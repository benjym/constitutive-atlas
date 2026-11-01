#!/usr/bin/env python3
"""Read-only old-byte archive plan from bounded audit; never writes source/maps."""
import json,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;B='3873a48b256ed37cbc78378ee6b41d73139676f8';OLD='d1c3a19409adaa32791c105429a4167e5bac9d9d'
def blob(p):return subprocess.check_output(['git','show',B+':'+p])
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 r=json.loads((P/'audit.json').read_text());actions=r['direct_and_sidecar_closure'];sources={}
 for a in actions:
  path=a['original_path'];h=a['sha256'];k=(path,h)
  if k in sources:continue
  data=blob(path);assert digest(data)==h
  item={'original_path':path,'sha256':h,'bytes':len(data),'canonical_archive':a['canonical_archive'],'exists_in_base':a['archive_exists_in_base'],'git_source':B+':'+path}
  if item['exists_in_base']:assert digest(blob(item['canonical_archive']))==h;item['existing_archive_verified']=True
  sources[k]=item
 groups={}
 for a in actions:
  if a['document'].endswith('/source-archive-map.json'):continue
  group=groups.setdefault(a['sidecar'],{'exists_in_base':a['sidecar_exists'],'documents':{},'entries':{}})
  group['documents'][a['document']]=a['document_sha256'];key=a['original_path']+'@'+a['sha256'];group['entries'][key]={'original_path':a['original_path'],'sha256':a['sha256'],'archived_path':a['canonical_archive']}
 for group in groups.values():group['entries']=list(group['entries'].values())
 plan={'kind':'generic-control-latest-prospective-old-byte-plan-v2','source_commit':B,'canonical_old_bytes':list(sources.values()),'sidecar_candidates':groups,'limits':['Candidate closure only; classify exact checker before installation.','Current qualification raw hashes cannot be redirected into historical evidence.','No source/maps/archives installed.']}
 (P/'archive-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 prior=json.loads((P.parents[1]/'implicit-predictor-constraints-v1/release-bindings-v1/consumer-inputs.json').read_text())
 paths=list(prior['files'])+['tools/build_hill_laboratory.py','tools/test_hill_package.mjs','tools/test_hill_native.py','tools/test_hill_wasm.mjs','cmake/hill/CMakeLists.txt','docs/ingestion/hill-abaqus2025/execution-v1/build-receipt.json','docs/ingestion/hill-abaqus2025/execution-v1/source-freeze-v2.json','catalogue/agent-reviews/hill-abaqus2025-agent-v1.json']
 consumers={}
 for path in paths:
  data=blob(path);consumers[path]={'sha256':digest(data),'bytes':len(data),'same_as_prior_inspected_commit':prior['files'].get(path,{}).get('sha256')==digest(data) if path in prior['files'] else None}
 dependencies=['docs/ingestion/manzari-dafalias-1997/delivery-v1/release-bindings-v1/audit.py','docs/investigations/implicit-predictor-constraints-v1/release-bindings-v1/audit.json','docs/investigations/implicit-predictor-constraints-v1/release-bindings-v1/archive-plan.json','docs/investigations/implicit-predictor-constraints-v1/original/solver.hpp']
 (P/'consumer-inputs.json').write_text(json.dumps({'source_commit':B,'files':consumers,'read_only_workspace_dependencies':{f:digest(Path(f).read_bytes()) for f in dependencies}},indent=2)+'\n')
 diff=subprocess.check_output(['git','diff','--name-only',OLD,B,'--','tools','cmake','cpp','atlas','schemas','models','CMakeLists.txt'],text=True).splitlines()
 summary={'source_commit':B,'prior_source_commit':OLD,'solver':r['targets']['cpp/include/atlas/solver.hpp'],'tracked':r['tracked_blob_count'],'scanned_text':r['scanned_text_blob_count'],'parsed_json':r['parsed_json_document_count'],'direct_solver_documents':len({a['document'] for a in actions if a['original_path']=='cpp/include/atlas/solver.hpp'}),'closure_occurrences':len(actions),'candidate_sidecars':len(groups),'new_candidate_sidecars':sum(not g['exists_in_base'] for g in groups.values()),'canonical_old_byte_targets':len(sources),'existing_canonical_verified':sum(x['exists_in_base'] for x in sources.values()),'canonical_missing':sum(not x['exists_in_base'] for x in sources.values()),'older_solver_pin_occurrences':len(r['older_target_pins']),'compared_source_consumer_changes':diff,'no_source_maps_archives_installed':True,'no_build_or_compiled_calls':True}
 (P/'static-checks.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
