"""Seal current draft only; no approval, shared installation or material call."""
from pathlib import Path
import hashlib,json,gzip,runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
 with (HERE/name).open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')
checks=runpy.run_path(str(HERE/'check_preparation.py'))['main']();assert checks['pass']
selected=json.loads((HERE/'FINAL-REPLAY-v3.json').read_text());candidates={p.relative_to(HERE/'candidates').as_posix():sha(p) for p in sorted((HERE/'candidates').rglob('*')) if p.is_file()}
assert len(candidates)==28 and candidates==selected['final_candidate_sha256']
assert sha(HERE/'response-symlink-fix-v1/MANIFEST.json')=='3c6fc3663bcca96255cc7be8f2cb53287406d818c6afc56ea8cc6047c8e3dc69'
for n,h in json.loads((HERE/'response-symlink-fix-v1/MANIFEST.json').read_text())['files'].items():assert sha(HERE/'response-symlink-fix-v1'/n)==h
review=ROOT/'docs/ingestion/bingham-comsol63/response-symlink-fix-review-v1/BINDINGS-v1.json';assert json.loads(review.read_text())['decision']=='accepted'
routing={p.relative_to(HERE/'routing-context').as_posix():sha(p) for p in (HERE/'routing-context').rglob('*') if p.is_file()}
(HERE/'routing-context-inventory.json.gz').write_bytes(gzip.compress((json.dumps(routing,indent=2)+'\n').encode(),mtime=0))
write('CHECKS.json',checks)
write('COMPOSITION.json',{'kind':'bingham-current-e6f06114-integration-draft-v3','candidate_files':candidates,'preservation_files':{p.relative_to(HERE/'preservation-candidates').as_posix():sha(p) for p in sorted((HERE/'preservation-candidates').rglob('*')) if p.is_file()},'current_baseline':{'path':'baseline-public-records.json','sha256':sha(HERE/'baseline-public-records.json')},'selected_preservation_replay':{'path':'FINAL-REPLAY-v3.json','sha256':sha(HERE/'FINAL-REPLAY-v3.json')},'selected_private_inventory':{'path':'consumer-context-inventory-final-v3.json.gz','sha256':sha(HERE/'consumer-context-inventory-final-v3.json.gz')},'source_dependencies':json.loads((HERE/'DEPENDENCIES.json').read_text()),'prior_counts':checks['prior_database_counts'],'prospective_counts':checks['prospective_counts'],'preservation':checks['preservation'],'status':'draft current-source composition; independent exact review pending; final complete imported-tree replay mandatory after actual E5/evidence staging','registry_or_profile_admitted':False,'model_or_review_created':False,'compiled_calls':0,'installed':False})
files={p.relative_to(HERE).as_posix():sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.relative_to(HERE).parts[0] not in {'consumer-context','routing-context'} and '__pycache__' not in p.parts and p.relative_to(HERE).as_posix() not in {'MANIFEST.json','seal.log'}}
write('MANIFEST.json',{'kind':'bingham-current-integration-v3-source-draft-manifest','files':files,'composition_sha256':sha(HERE/'COMPOSITION.json'),'raw_contexts_excluded':True,'draft_context_only':True,'future_complete_imported_tree_replay_required':True,'source_only':True,'compiled_calls':0,'installed':False,'approval_created':False})
print(json.dumps({'manifest_sha256':sha(HERE/'MANIFEST.json'),'composition_sha256':sha(HERE/'COMPOSITION.json'),'bound_files':len(files),'candidate_files':len(candidates),'baseline_sha256':sha(HERE/'baseline-public-records.json'),'final_replay_sha256':sha(HERE/'FINAL-REPLAY-v3.json')},indent=2))
