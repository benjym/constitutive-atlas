import json,hashlib,copy
from pathlib import Path
R=Path(__file__).resolve().parents[4]; O=Path(__file__).parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text())
P='docs/ingestion/vibe-2026/controlled-path-refresh-v1/'
m=read(P+'source-manifest-v4.json'); assert h(R/P/'source-manifest-v4.json')=='33ac5c611231d6fc59c1c67a70cef50672971bff58d45f32ed3582f4d5b7dbf9'
for f in m['files']:
 p=R/f['path'];assert h(p)==f['sha256'];assert p.stat().st_size==f['bytes']
a=read(P+'plan-v4.json');b=read(P+'plan-v5.json'); assert len(a['source_closure'])==248 and len(b['source_closure'])==250
for p,v in b['source_closure'].items():assert h(R/p)==v,p
projection=read('docs/ingestion/vibe-2026/main-integration-v1/controlled-path-projection-v1.json')
s=(R/'tools/qualify_controlled_path_refresh.py').read_text()
for x in reversed(projection['helper_literal_projection']):
 assert s.count(x['after'])==x['occurrences'];s=s.replace(x['after'],x['before'])
assert hashlib.sha256(s.encode()).hexdigest()==projection['live_helper_sha256']
old=copy.deepcopy(b);old['identity']=a['identity']
for f in projection['added_closure_inputs']:
 assert old['source_closure'].pop(f['path'])==f['sha256']
old['source_closure']['tools/qualify_controlled_path_refresh.py']=projection['live_helper_sha256']
# Only output/build locations changed in all remaining strings.
def restore(x):
 if isinstance(x,str):return x.replace('controlled-path-refresh-v2/','controlled-path-refresh-v1/').replace('controlled-path-refresh-v1/execution-v2','controlled-path-refresh-v1/execution-v1')
 if isinstance(x,list):return [restore(y) for y in x]
 if isinstance(x,dict):return {k:restore(v) for k,v in x.items()}
 return x
assert restore(old)==a
result={'status':'accepted-prospective-source-only','source_manifest_sha256':h(R/P/'source-manifest-v4.json'),'plan_sha256':h(R/P/'plan-v5.json'),'source_files':len(m['files']),'closure_pins':len(b['source_closure']),'helper_reverse_byte_identity':True,'plan_reverse_structure_identity':True,'all_original_cases_bounds_settings_gates':True,'compiled_calls':0,'requires_new_actual_execution_and_independent_build_review':True,'blocking_findings':[]}
(O/'controlled-path-v5-decision.json').write_text(json.dumps(result,indent=2)+'\n')
manifest={'files':[{'path':str((O/n).relative_to(R)),'sha256':h(O/n)} for n in ['check_controlled_path_v5.py','controlled-path-v5-decision.json']]};(O/'controlled-path-v5-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(result);print('manifest',h(O/'controlled-path-v5-manifest.json'))
