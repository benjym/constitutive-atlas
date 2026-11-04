"""Author-only source freeze; no approval is created by this script."""
from pathlib import Path
import ast,hashlib,json,importlib.util
ROOT=Path(__file__).resolve().parents[4]
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('current_ci',ROOT/'tools/check_controlled_time_ci.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=(P/'preimages/tools/check_controlled_time_ci.py').read_text();new=(ROOT/'tools/check_controlled_time_ci.py').read_text()
a=ast.parse(old);b=ast.parse(new)
def segment(tree,text,name):return ast.get_source_segment(text,next(x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.Assign)) and (getattr(x,'name',None)==name or any(isinstance(t,ast.Name) and t.id==name for t in getattr(x,'targets',[])))))
unchanged={name:segment(a,old,name)==segment(b,new,name) for name in ['INPUTS','SELECTED','safe_relative','sha','capture','write_new','main']};assert all(unchanged.values())
# Original verify body changes are exactly the prospective narrow routing additions.
original=segment(a,old,'verify');expected=original.replace(' checks=[]',' amendment=amendment_sources();current=amendment[\'current_sources\']\n checks=[]',1).replace("for pin in pins:assert sha(safe_relative(pin['path']))==pin['sha256'],pin['path']","for pin in pins:verify_pin(name,pin,current)").replace("for pin in frozen['files']:assert sha(safe_relative(pin['path']))==pin['sha256'],pin['path']","for pin in frozen['files']:verify_pin(str(manifest.relative_to(ROOT)),pin,current)").replace(" result=dict(status='pass-source-only'"," accepted_decision(AMENDMENT_REVIEW,AMENDMENT,sha(safe_relative(AMENDMENT)))\n result=dict(status='pass-source-only'")
assert expected==segment(b,new,'verify')
checks=[];paths=set()
for name,expectedsha in m.INPUTS.items():
 assert sha(ROOT/name)==expectedsha;paths.add(name);d=json.loads((ROOT/name).read_text());selected=m.SELECTED.get(name)
 for pin in d['files']:
  if selected is not None and pin['path'] not in selected:continue
  paths.add(pin['path']);triple=(name,pin['path'],pin['sha256'])
  if triple in m.HISTORICAL_EXCEPTIONS:
   from atlas.evidence import checked_receipt
   archive=checked_receipt(ROOT,name,pin['path'],pin['sha256']);paths.add(str(archive.relative_to(ROOT)));checks.append({'document':name,'path':pin['path'],'route':'exact oldarchive plus separate current accepted source'})
  else:assert sha(ROOT/pin['path'])==pin['sha256'];checks.append({'document':name,'path':pin['path'],'route':'strict current bytes'})
ci='docs/ingestion/vibe-2026/controlled-time-ci-v1/source-manifest-v1.json';paths.add(ci)
for pin in json.loads((ROOT/ci).read_text())['files']:
 paths.add(pin['path'])
 if (ci,pin['path'],pin['sha256']) not in m.HISTORICAL_EXCEPTIONS:assert sha(ROOT/pin['path'])==pin['sha256']
plan='docs/ingestion/vibe-2026/controlled-time-ci-v1/plan-v3.json'
for pin in json.loads((ROOT/plan).read_text())['source_files']:assert sha(ROOT/pin['path'])==pin['sha256'];paths.add(pin['path'])
proof={'unchanged_source_segments':unchanged,'verify_body_exact_transform':True,'input_manifest_loop_checks':checks,'portable_source_pins_direct_current':True,'new_sidecar_prior_state':'absent; no reverse consumers','collector_sha_hits':{'actual_repo_relative_pair_consumer':ci,'absolute_path_provenance':'docs/ingestion/vibe-2026/review-ci-v1/manifest.json','scalar_hash_provenance':'docs/ingestion/vibe-2026/review-ci-v1/workflow-results.json'},'compiled_calls':0}
(P/'source-invariance-proof-v1.json').write_text(json.dumps(proof,indent=2)+'\n')
for doc,name,oldhash in m.HISTORICAL_EXCEPTIONS:
 paths.update([doc,str(Path(doc).with_name('source-archive-map.json')),f'catalogue/source-snapshots/{oldhash}/{name}',name])
paths.update([m.TEST_ACCEPTANCE['manifest'],m.TEST_ACCEPTANCE['decision']])
for f in P.rglob('*'):
 if f.is_file() and '__pycache__' not in f.parts and f.name!='source-manifest-v1.json':paths.add(str(f.relative_to(ROOT)))
manifest={'identity':'controlled-time-current-source-amendment-v1','author_run':'/root/vibe_capability:controlled-time-source-resolution-v1','historical_exceptions':[list(x) for x in sorted(m.HISTORICAL_EXCEPTIONS)],'current_sources':{name:sha(ROOT/name)for name in ['tests/test_controlled_time.py','tools/check_controlled_time_ci.py']},'files':[{'path':s,'sha256':sha(ROOT/s)}for s in sorted(paths)],'acceptance':'Pending genuine independently authored fixed-path review; author creates no acceptance decision.'}
(P/'source-manifest-v1.json').write_text(json.dumps(manifest,indent=2)+'\n');print(len(paths),sha(P/'source-manifest-v1.json'))
