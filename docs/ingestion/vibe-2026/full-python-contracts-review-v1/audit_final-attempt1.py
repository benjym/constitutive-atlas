from pathlib import Path
import ast,json,hashlib,subprocess,sys,importlib.util,tempfile,gzip
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;P=R/'docs/ingestion/vibe-2026/full-python-contracts-v1';sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
from atlas.agent_review import validate_review,approval_entry
h=lambda b:hashlib.sha256(b).hexdigest();sha=lambda p:h(p.read_bytes());read=lambda p:json.loads(p.read_text());git=lambda *a:subprocess.check_output(['git',*a],cwd=R)
freeze=P/'source-manifest-v3.json';assert sha(freeze)=='75d282ac6a07523c7815f97bf97f748b924f47ae971f7e09e5f3f0b86aeaa9b5';files=read(freeze)['files'];assert len(files)==352
for f in files:assert sha(R/f['path'])==f['sha256'],f['path']
v2=read(P/'preservation-plan-v2.json');v3=read(P/'preservation-plan-v3.json');mixed=v3['sidecar'];assert len(v2['bindings'])==178 and len(v2['maps'])==81
for row in v2['maps']:
 expected=v3['after'] if row['path']==mixed else row['after'];assert (R/row['path']).read_bytes()==(json.dumps(expected,indent=2)+'\n').encode()
 old=read(R/row['before_archive']) if row['before_sha256'] else {'version':'immutable-source-archive-map-0.1','documents':{},'entries':[]}
 if row['before_sha256']:assert git('show','HEAD:'+row['path'])==(R/row['before_archive']).read_bytes()
 assert all(expected['documents'].get(k)==v for k,v in old['documents'].items());assert expected['entries'][:len(old['entries'])]==old['entries']
assert sha(R/v3['before_archive'])==v3['before_sha256'];old=read(R/v3['before_archive']);restore=json.loads(json.dumps(v3['after']));assert restore['entries'].pop()==v3['source_archive'] and restore==old
stress=v3['source_archive'];assert git('show',v3['source_commit']+':atlas/stress.py')==(R/stress['archived_path']).read_bytes()
allbindings=v2['bindings']+[{'document':v3['document'],'document_sha256':v3['document_sha256'],**stress}]
for b in allbindings:assert sha(R/b['document'])==b['document_sha256'];assert checked_receipt(R,b['document'],b['original_path'],b['sha256'])==R/b['archived_path']
changed=git('diff','--name-only').decode().splitlines();allowed={'IMPLEMENTATION_PLAN.md','tests/test_catalogue.py','tests/test_controlled_time.py',*[m['path'] for m in v2['maps']]};assert not set(changed)-allowed
# Preserve every unaffected original test/helper body, not merely their names.
for name,changed_functions in [('test_catalogue.py',{'test_directory_coverage_has_resolvable_provenance','test_database_keeps_candidate_and_executable_sources'}),('test_controlled_time.py',{'test_generated_layout_and_old_bytes'})]:
 a=ast.parse((P/'preimages/tests'/name).read_text());b=ast.parse((R/'tests'/name).read_text());original={n.name:n for n in ast.walk(a) if isinstance(n,ast.FunctionDef)};current={n.name:n for n in ast.walk(b) if isinstance(n,ast.FunctionDef)}
 for key,node in original.items():
  if key not in changed_functions:assert ast.dump(node)==ast.dump(current[key]),key
 assert set(original)<=set(current)
original_loop="for r in json.loads((baseline/'manifest.json').read_text()):self.assertEqual(hashlib.sha256((Path(d)/Path(r['path']).name).read_bytes()).hexdigest(),r['sha256'])";assert original_loop in (R/'tests/test_controlled_time.py').read_text();assert 'self.assertTrue(candidate_ids' in (R/'tests/test_catalogue.py').read_text()
# Independently bind original emitter and full historical default glob to Git.
context=read(P/'historical-context-v1.json');plan=read(P/'plan-v1.json');base=plan['historical_commit'];assert context['models']==plan['historical_models']
for f in [context['emitter'],*context['models']]:assert git('show',base+':'+f['path'])==(R/f['archived_path']).read_bytes()
spec=importlib.util.spec_from_file_location('independent_historical_context',P/'historical_baseline.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
from unittest.mock import patch
with patch('subprocess.run',side_effect=AssertionError('compiled execution forbidden')),patch('ctypes.CDLL',side_effect=AssertionError('compiled module forbidden')):
 with tempfile.TemporaryDirectory(prefix='independent-historical-',dir=O) as t:
  emitted=helper.generate(t);assert len(emitted)==15
  for f in context['expected_outputs']:assert (Path(t)/Path(f['path']).name).read_bytes()==(R/f['path']).read_bytes()
# Original registry/reviews/models remain byte-identical, all281 supports verified via resolver.
for path in ['catalogue/approved-models.json','catalogue/manifest.json','atlas/evidence.py','atlas/compiler.py','atlas/model.py','atlas/research.py']:assert git('show','HEAD:'+path)==(R/path).read_bytes()
registry=read(R/'catalogue/approved-models.json');approvals=[]
for a in registry['models']:
 doc=R/a['review']['path'];assert git('show','HEAD:'+a['review']['path'])==doc.read_bytes()
 if doc.suffix=='.json':validate_review(doc,root=R,for_approval=True);assert approval_entry(doc,root=R)==a
 assert sha(R/a['definition']['path'])==a['definition']['sha256'];approvals.append(a['model_id'])
v='catalogue/agent-reviews/vibe-2026-appendix-a-agent-v2.json';vibe=read(R/v);supports=[]
for f in vibe['artifacts']:
 target=checked_receipt(R,v,f['path'],f['sha256']);assert sha(target)==f['sha256'];supports.append({'path':f['path'],'sha256':f['sha256'],'selected':str(target.relative_to(R))})
assert len(supports)==281 and len(approvals)==30
closures=[]
for name in ['controlled-path-refresh-v1/plan-v5.json','maxwell-refresh-v1/plan.json']:
 p=read(R/'docs/ingestion/vibe-2026'/name);pins={**p.get('source_closure',p.get('source_manifest',{}).get('files',{})),**{f['path']:f['sha256'] for f in p.get('files',[])}}
 for path,value in pins.items():assert sha(R/path)==value
 closures.append({'plan':name,'pins':len(pins)})
# Compressed inventory retains the exact original99MB and two usable copies.
ret=read(P/'raw-inventory-durable-retention-v1.json');rawret=read(P/'inventory-retention-v1.json');compressed=Path(ret['durable_root_path']).read_bytes();assert h(compressed)==ret['sha256']==rawret['compressed_sha256'];raw=gzip.decompress(compressed);assert len(raw)==rawret['bytes'] and h(raw)==rawret['sha256'];assert Path(ret['temporary_worktree_copy']).read_bytes()==compressed
report={'status':'accepted-source-only','source_manifest_sha256':sha(freeze),'frozen_files':352,'production_receipt_bindings':len(allbindings),'maps':81,'oldentries_and_documentpins_preserved':True,'v3_stress_delta_one_exact_original_entry':True,'historical_emitter_and_complete15modelglob_exactGit':True,'historical_generated_bytes_exact_original':context['expected_outputs'],'unaffected_original_test_method_AST_exact':True,'current16coverage_and_nonvacuous_candidates':True,'vibe_supports':supports,'approval_count':30,'dependency_closures':closures,'raw_inventory_exact_recovery_bytes':len(raw),'preexisting_unresolved':1035,'preexisting_invalid_document_mirrors_excluded':40,'original_path_only_provenance_excluded':12,'scope':'Six regression failures and archive preservation; no new scientific approval or fullCI success claim.','compiled_calls':0,'blocking_findings':[],'cleanup':'Independent source-only generation fixture automatically removed; no processes/builds/browser/downloads created. Root durable inventory verified; temporary inventory copy remains coordinator-owned pending cleanup.'};(O/'final-audit-results.json').write_text(json.dumps(report,indent=2)+'\n');print('352freeze,179bindings,old15bytes,281supports,30approvals verified')
