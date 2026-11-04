from pathlib import Path
import ast,json,hashlib,importlib.util,subprocess
O=Path(__file__).resolve().parent;R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ok(v,n):assert v,n;checks.append(n)
for q in O.glob('*.py'):ast.parse(q.read_text());checks.append('syntax '+q.name)
for row in json.loads((O/'source-pins.json').read_text()):ok(h(Path(row['path']))==row['sha256'],'exact source '+row['path'])
x=json.loads((O/'source-identity.json').read_text());ok(len(x['ordinary_models'])==17 and x['catalogue_entries']==51 and len(x['named_ids'])==9,'strict17/51/9 source membership');ok(x['saved_global_dataset_count']==994 and x['saved_decoded_exact'],'retained994 globalproof explicitly historical')
for id,row in x['ordinary_models'].items():ok(h(Path(row['path']))==row['sha256'],'original model exact '+id)
oldpolicy=Path('docs/delivery/unheld-finalisation-20261102-v1/baseline-qualification-plan-v5/policy.json');p=json.loads(oldpolicy.read_text())
for id,sha in p['candidate_sha256'].items():ok(x['ordinary_models'][id]['sha256']==sha,'originalfive model source unchanged '+id)
roles=json.loads((O/'retained-auxiliary-roles.json').read_text());authority=roles['saved_upload_authority'];ok(h(Path(authority['path']))==authority['sha256'],'actual640 saved upload authority');rows={r['path']:r for r in json.loads(Path(authority['path']).read_text())['files']}
for role in roles['roles']:
 for pin in role['assets']:ok((pin['sha256'],pin['bytes'])==(rows[pin['published_path']]['sha256'],rows[pin['published_path']]['size_bytes']),'retained expected bytes '+role['role']+' '+pin['published_path'])
spec=importlib.util.spec_from_file_location('inert_recipe',O/'recipe.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);recipe=m.commands('/qualified/python','/qualified/node','a'*40);ops=recipe['operations'];ok(not recipe['ready_for_actual']and recipe['no_automatic_rebuild_provision_network'],'no actual authority/automatic rebuild/network');ok([o['id']for o in ops]==['fast-source-contracts','retained-source-guards','standard-web-package','package-engine-smoke','all994-built-dataset-transport','original-package-contracts','supported17-public-inputs','original-scoped-parity'],'concrete standard ordering')
web=ops[2]['argv'];ok(web.count('--wasm-dir')==1 and str(m.WORK/'wasm')in web and '--preview-experiments'not in web,'only freshC ordinary/published approved release');ok(len([a for a in web if a.endswith('-wasm-dir')])==15,'all15 explicit webengine dir flags includingordinary')
for role in roles['roles']:ok(web[web.index(role['flag'])+1]==role['directory'],'retained no-copy role '+role['role'])
ok(recipe['publication_environment_addition']=={'GITHUB_SHA':'a'*40},'explicit source stamp avoids Git fallback')
for python,node,revision in [('relative','/absolute/node','x'),('/absolute/python','node','x'),('/absolute/python','/absolute/node','')]:
 try:m.commands(python,node,revision)
 except ValueError:ok(True,'reject unbound tools/revision '+repr((python,node,revision)))
 else:raise AssertionError('bad tools/revision')
guards=json.loads((O/'builtin-package-guards.json').read_text());ok(guards['all_check_true']and len(guards['mandatory_subprocesses'])>=12,'all builtin guard checkTrue retained');ok('test_implicit_path_package.py'in json.dumps(guards)and'interface_checker'in json.dumps(guards),'dynamic interface + implicit checks retained')
run=subprocess.run(['node',str(R/'tools/check_model_profiles.mjs'),str(R)],capture_output=True,text=True);(O/'profiles.stdout').write_text(run.stdout);(O/'profiles.stderr').write_text(run.stderr);ok(run.returncode==0 and '51/51'in run.stdout,'pure source51profiles checker no enginecall')
(O/'check.stdout.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'source_only':True,'compiled_material_browser_network_build_calls':0,'artifact_byte_reads':0},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
