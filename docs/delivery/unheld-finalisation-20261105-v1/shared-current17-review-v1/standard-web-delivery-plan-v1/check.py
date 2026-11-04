"""Independent standard website source recipe review; no assets or engines loaded."""
from pathlib import Path
import ast,contextlib,hashlib,importlib.util,io,json,runpy,sys
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;P=HERE.parents[1]/'standard-web-delivery-plan-v1'
EXPECTED='b31cbd5299903175d0ca4d7bb86caa3c00c7acabc0e542442008a8287259b63e'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):assert v,n;checks.append(n)
ok(sha(P/'manifest.json')==EXPECTED,'exact source proposal manifest')
manifest=json.loads((P/'manifest.json').read_text())
for row in manifest['files']:
 q=P/row['path'];ok(not q.is_symlink()and sha(q)==row['sha256']and q.stat().st_size==row['size_bytes'],'frozen member '+row['path'])
write=Path.write_text
def redirect_write(path,data,*args,**kwargs):
 if path.parent==P and path.name in ('profiles.stdout','profiles.stderr','check.stdout.json'):path=HERE/('author-replay-'+path.name)
 return write(path,data,*args,**kwargs)
stdout=io.StringIO()
with patch.object(Path,'write_text',redirect_write),contextlib.redirect_stdout(stdout):runpy.run_path(str(P/'check.py'),run_name='independent_exact_source_replay')
ok(json.loads((P/'check.stdout.json').read_text())==json.loads((HERE/'author-replay-check.stdout.json').read_text()),'exact118 original source checks replay')
for row in manifest['files']:ok(sha(P/row['path'])==row['sha256'],'author bytes unchanged '+row['path'])
spec=importlib.util.spec_from_file_location('independent_standard_recipe',P/'recipe.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
recipe=r.commands('/qualified/python','/qualified/node','1'*40);ops={x['id']:x['argv']for x in recipe['operations']}
ok(recipe['ready_for_actual']is False and recipe['no_automatic_rebuild_provision_network'],'recipe supplies no actual operation authority')
ok(recipe['publication_environment_addition']=={'GITHUB_SHA':'1'*40},'explicit new source identity no Git fallback')
for revision in ('','64002531f0af5c06ad0402d0d80548102f8e6a38','1'*39,'g'*40,'1'*40+' '):
 try:r.commands('/qualified/python','/qualified/node',revision)
 except ValueError:checks.append('reject invalid/old revision '+repr(revision))
 else:raise AssertionError('bad revision accepted')
web=ops['standard-web-package'];source=r.SOURCE
parser=ast.parse((source/'tools/build_web.py').read_text());flags={n.args[0].value for n in ast.walk(parser)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='add_argument'and n.args and isinstance(n.args[0],ast.Constant)and isinstance(n.args[0].value,str)and n.args[0].value.endswith('-wasm-dir')}
actualflags={x for x in web if x.endswith('-wasm-dir')}
ok(actualflags==flags and len(flags)==15,'every existing builder engine argument supplied exactly')
ok('--preview-experiments'not in web and '--database-only'not in web,'full approved release builder route')
ok(web[web.index('--wasm-dir')+1]==str(r.WORK/'wasm'),'ordinary engine exclusively fresh C artifact directory')
roles=json.loads((P/'retained-auxiliary-roles.json').read_text());assets=[x for role in roles['roles']for x in role['assets']]
ok(len(roles['roles'])==6 and len(assets)==18,'six retained roles exact18 expected assets')
sls=next(role for role in roles['roles']if role['role']=='sls');wasm=next(x for x in sls['assets']if x['path'].endswith('.wasm'))
ok(wasm['sha256']=='62a24736aeaef9c0feec460716eeafdfd5df7a12f51eced86e84fe0ffbb49903'and wasm['bytes']==5304942,'published SLS identity retained without repin')
prereq=json.loads((P/'launch-prerequisites.json').read_text())
ok(prereq['ready_for_actual']is False and prereq['new_local_commit']is None and prereq['complete_C_independent_accepted_review']is None,'genuine future authority/commit inputs remain pending')
ok(prereq['complete_C_observation_manifest']['sha256']=='99be54a79e461c250fb818a5a0b943cfc30e0408674385372d6eeb61772e4bc8','correct genuine completed C observation identity')
text=json.dumps(prereq)
for token in ('before and after','ordinary_artifacts','C_source_compatibility','other_roles','process','mandatoryreap','FullCI','independent E8'):
 ok(token in text,'mandatory actual launch/release prerequisite '+token)
guards=json.loads((P/'builtin-package-guards.json').read_text());webtext=(source/'tools/build_web.py').read_text()
for item in guards['mandatory_subprocesses']:ok(item['source']in webtext,'original builtin exact statement '+str(item['line']))
ok(all(item['source'].endswith('check=True)')for item in guards['mandatory_subprocesses']),'every listed original builtin remains blocking')
ok('--built-assets'in ops['all994-built-dataset-transport'],'all approved994 transport gate requested')
ok('--native'in ops['package-engine-smoke']and '--wasm'in ops['package-engine-smoke'],'native and packaged Wasm smoke paired')
ok('--directory'in ops['supported17-public-inputs']and '--policy'in ops['supported17-public-inputs'],'strict supported policy unchanged')
ok(ops['original-package-contracts'][:2]==['/qualified/node','--test']and [Path(x).name for x in ops['original-package-contracts'][2:]]==['test_database_download_gate.mjs','test_web_package.mjs','test_supported_package.mjs','test_laboratory_profile_policy.mjs'],'all four exact original Node contract modules present')
ok(recipe['serial_parent_observer']['timeout_seconds']==1800 and recipe['serial_parent_observer']['mandatory_reap']and recipe['serial_parent_observer']['preserve_first_failure'],'original observer1800 mandatory reap firstfailure')
(HERE/'checks.json').write_text(json.dumps({'status':'PASS','independent_checks':len(checks),'labels':checks,'exact_author_source_checks':118,'compiled_or_asset_byte_reads':0,'engine_or_build_browser_network_Git_calls':0,'pure_profile_source_checker_only':True,'temporary_resources_created':False},indent=2)+'\n')
print(json.dumps({'status':'PASS','independent_checks':len(checks),'author_source_checks':118}))
