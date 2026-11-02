"""Read-only current-source composition/preservation checks; no builds/engines."""
from pathlib import Path
import ast,collections,difflib,gzip,hashlib,json,runpy,sqlite3
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];V2=Path('/private/tmp/atlas-bingham-release-v2');OLD=V2/'docs/ingestion/bingham-comsol63/interface-v4-preparation-v1/ci-build-receipts-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def closure(group):
 if group=='maxwell':
  names={'cmake/maxwell/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'}
  for directory,suffixes in [('atlas',{'.py'}),('cpp',{'.cpp','.hpp'}),('schemas',{'.json'})]:names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts)
 else:
  names={'cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'}
  for directory,pattern in [('cpp/include/atlas','*.hpp'),('atlas','*.py'),('schemas','*.json')]:names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob(pattern) if '__pycache__' not in p.parts)
 names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'cpp/scalar-functions').rglob('*') if p.is_file())
 return {n:sha(ROOT/n) for n in sorted(names)}
def main():
 inputs=json.loads((HERE/'INPUTS.json').read_text())
 for n,h in inputs['release_inputs'].items():assert sha(ROOT/n)==h,n
 for n in inputs['archive_targets']:assert (HERE/'before/shared'/n).read_bytes()==(ROOT/n).read_bytes()
 new=lambda n:(HERE/'candidates'/n).read_text()
 app=new('web/app.js').replace("import {setupBinghamLaboratory} from './bingham-laboratory.mjs';\n",'',1).replace("setupBinghamLaboratory({chart,cancelOrdinary:()=>cancel('')}),",'',1);assert app==(ROOT/'web/app.js').read_text()
 builder=new('tools/build_web.py').replace("    parser.add_argument('--bingham-wasm-dir',type=Path,default=ROOT/'build-bingham-public',help='Exact independently reviewed Bingham physical-time engine')\n",'',1).replace("    from build_bingham_laboratory import bundle as bundle_bingham\n    bundle_bingham(dest,args.bingham_wasm_dir)\n    subprocess.run(['node',str(ROOT/'tools/test_bingham_package.mjs'),str(dest)],check=True)\n",'',1);assert builder==(ROOT/'tools/build_web.py').read_text()
 test=new('tests/test_j2_main_routing.mjs');addition='''assert.equal(setups.filter(name=>name==='setupBinghamLaboratory').length,1);checks++;
assert.ok(registration.includes("setupBinghamLaboratory({chart,cancelOrdinary:()=>cancel('')})"));checks++;
assert.ok(source.includes("import {setupBinghamLaboratory} from './bingham-laboratory.mjs';"));checks++;
''';assert test.replace(addition,'',1)==(ROOT/'tests/test_j2_main_routing.mjs').read_text()
 alias='--controlled-path-wasm-dir docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/qualified-norsand-unit-alias-v1'
 assert new('.github/workflows/verify.yml')==(OLD/'candidates/.github/workflows/verify.yml').read_text().replace('--controlled-path-wasm-dir build-controlled-path-public',alias)
 assert new('.github/workflows/verify.yml').count(alias)==2
 for name in ['web/bingham-laboratory.mjs','web/bingham-atlas-contract.mjs','web/bingham-atlas-worker.mjs','tools/build_bingham_laboratory.py','tools/test_bingham_package.mjs','tools/provision_bingham_assets.py','tools/provision_bingham_dependency_assets.py','tests/test_bingham_laboratory_contract.mjs']:assert sha(HERE/'candidates'/name)==sha(V2/name),name
 assert sha(HERE/'candidates/web/bingham-atlas-contract.mjs')=='7300c57787a353aad071a0b906c7228d4b3a1a91b123eac77704c81e3ee39868'
 assert sha(HERE/'candidates/tools/record_cmake_profile_build.py')=='1b041138ee636e2a3a72b5e04093add12152d97041f9b3b79fc437b85626733b'
 for p in (HERE/'candidates').rglob('*.py'):ast.parse(p.read_text())
 ast.parse((HERE/'prepare_integration.py').read_text());ast.parse((HERE/'check_preservation.py').read_text())
 current=json.loads((HERE/'candidates/docs/ingestion/bingham-comsol63/interface-v4/POLICY.json').read_text());prior=json.loads((OLD/'candidates/docs/ingestion/bingham-comsol63/interface-v4/POLICY.json').read_text());current['pipeline'].pop('current_release_context');current['pipeline']['build_receipts']['tool']['sha256']=prior['pipeline']['build_receipts']['tool']['sha256'];assert current==prior
 profiles=runpy.run_path(str(HERE/'prepare_integration.py'))['profiles']
 base_profiles=profiles((ROOT/'web/model-profile-data.mjs').read_bytes())[0];new_profiles=profiles((HERE/'candidates/web/model-profile-data.mjs').read_bytes())[0]
 assert len(base_profiles)==47 and set(new_profiles)==set(base_profiles)|{'bingham-comsol63-mises-perfect-zero-spin-ode'}
 assert all(new_profiles[n]==value for n,value in base_profiles.items())
 assert sha(HERE/'candidates/web/model-profile-data.mjs')=='31ad08d2f3db9e04aca616c54879b33e87d06b09f6e49e40630b155c60ae6f6b'
 index=json.loads((V2/'docs/ingestion/bingham-comsol63/frozen-engine-packaging-plan-v1/capsules/INDEX.json').read_text())
 for group,count in [('maxwell',149),('norsand',121)]:assert closure(group)==index['groups'][group]['source_files'] and len(closure(group))==count
 assert sha(ROOT/'CMakeLists.txt')=='61f7fb538fcb1f2d03259ed4eda531fc9f41bc6119ffed56f3ea49dd8c762a0d'
 baseline=json.loads((HERE/'baseline-public-records.json').read_text());assert baseline['counts']=={'agent_reviews':21,'model_approvals':25,'models':48,'publication_models':18,'publication_relations':8,'publication_screening':37,'publications':60,'screening_evidence':53,'sources':202}
 assert baseline['ordinary_catalogue_sha256']==sha(HERE/'baseline/models.json') and len(baseline['ordinary_catalogue']['models'])==15
 check=runpy.run_path(str(HERE/'check_preservation.py'))
 for name,rows in baseline['tables'].items():assert check['preserved'](rows,list(reversed(rows)),len(rows))==[]
 for old,newrows in [([{'a':1}],[{'a':2}]),([{'a':1}],[])]:
  try:check['preserved'](old,newrows,len(newrows));raise AssertionError('mutation accepted')
  except ValueError:pass
 with sqlite3.connect((HERE/'baseline/atlas.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as db:
  db.row_factory=sqlite3.Row
  for name,rows in baseline['tables'].items():assert check['bag'](rows)==check['bag']([dict(row) for row in db.execute('SELECT * FROM '+name)])
 proof=json.loads(gzip.decompress((HERE/'PROOF.json.gz').read_bytes()));summary=proof['summary'];assert not proof['failures'] and summary['newly_broken']==0 and summary['before_pass']==summary['unchanged_pass']+summary['redirected_pass'] and summary['before_fail']==summary['retained_failures']
 for n,h in proof['documents'].items():assert sha(ROOT/n)==h,n
 for m in proof['maps']:
  live=ROOT/m['path'];assert (sha(live) if live.exists() else None)==m['before_sha256']
  if not m['changed']:continue
  candidate=HERE/'preservation-candidates'/m['path'];assert sha(candidate)==m['after_sha256'];mapping=json.loads(candidate.read_text())
  if live.exists():
   old=json.loads(live.read_text());assert all(e in mapping['entries'] for e in old['entries']) and all(mapping['documents'][n]==h for n,h in old['documents'].items())
  for doc in live.parent.glob('*.json'):
   if doc.name!='source-archive-map.json':assert mapping['documents'][doc.relative_to(ROOT).as_posix()]==sha(doc)
 return {'pass':True,'current_base':'e6f06114','prior_database_counts':baseline['counts'],'prospective_counts':{**baseline['counts'],'models':49,'model_approvals':26,'agent_reviews':22,'sources':205},'ordinary_models_unchanged':15,'prior_source_closures':{'maxwell':149,'norsand':121},'all_current_hooks_preserved':True,'root_cmake_unchanged':True,'preservation':summary,'compiled_calls':0,'installed':False}
if __name__=='__main__':print(json.dumps(main(),indent=2))
