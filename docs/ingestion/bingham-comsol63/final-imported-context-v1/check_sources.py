"""Read-only source guards in the fully composed private context. No engines."""
from pathlib import Path
import hashlib,json,runpy,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];CONTEXT=Path('/private/tmp/atlas-bingham-final-context-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Exact accepted source enumeration is reused, replacing only its explicit root.
ns=runpy.run_path(str(ROOT/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/check_preparation.py'))
closure=ns['closure'];closure.__globals__['ROOT']=CONTEXT
index=json.loads(Path('/private/tmp/atlas-bingham-release-v2/docs/ingestion/bingham-comsol63/frozen-engine-packaging-plan-v1/capsules/INDEX.json').read_text())
counts={}
for group,count in [('maxwell',149),('norsand',121)]:
 actual=closure(group);assert actual==index['groups'][group]['source_files'] and len(actual)==count;counts[group]=len(actual)
assert sha(CONTEXT/'CMakeLists.txt')==sha(ROOT/'CMakeLists.txt')=='61f7fb538fcb1f2d03259ed4eda531fc9f41bc6119ffed56f3ea49dd8c762a0d'
for folder in ['atlas','cpp','schemas']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:assert sha(CONTEXT/p.relative_to(ROOT))==sha(p),str(p)
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review,approval_entry
v=validate_review(CONTEXT/'catalogue/agent-reviews/bingham-comsol63-agent-v1.json',root=CONTEXT,for_approval=True)
a=approval_entry(CONTEXT/'catalogue/agent-reviews/bingham-comsol63-agent-v1.json',root=CONTEXT)
registry=json.loads((CONTEXT/'catalogue/approved-models.json').read_text())['models'];assert [x for x in registry if x['model_id']==v['model']['id']]==[a]
doc='docs/ingestion/bingham-comsol63/execution-v5/source-bindings.json';source=json.loads((CONTEXT/doc).read_text());capsule={n:sha(checked_receipt(CONTEXT,doc,n,h)) for n,h in source['source_files'].items()};assert capsule==source['source_files']
print(json.dumps({'passed':True,'current_packaging_context':'e6f06114 plus selected standalone runtime/profile/hooks; common C++/schema/root CMake unchanged','old_source_closures':counts,'E5_artifacts':len(v['artifacts']),'canonical_approval_matches':True,'actual_engine_v5_source_capsule_files':len(capsule),'capsule_current_equivalence_claimed':False,'build_or_material_calls':0},indent=2))
