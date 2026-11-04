from pathlib import Path
import hashlib,json,re,shlex
Q=Path(__file__).resolve().parent;N=Q.parents[1];P=N/'shared640-artifact-binding-v1';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();labels=[]
def ok(v,s):assert v,s;labels.append(s)
def pin(r):p=Path(r['path']);ok(p.is_file()and H(p)==r['sha256']and p.stat().st_size==r['bytes'],'exact observed pin '+r['path'])
ok(H(P/'manifest.json')=='ae6d6f40938d29249fa57d2ecfc18281465ac75ab06f86a172473273122a2b1d','exact76member handoff proposal manifest')
m=json.loads((P/'manifest.json').read_text());ok(len(m['files'])==76,'all76frozenmembers')
for row in m['files']:
 p=P/row['path'];ok(p.is_file()and not p.is_symlink()and H(p)==row['sha256']and p.stat().st_size==row['size_bytes'],'exact manifest member '+row['path'])
ok(H(P/'handoff.json')=='78c7c2b4aeef1abd4cf6894ff66d8a70b1c4179092298c198dc9f6f3d3f11ae9','exact handoff')
h=json.loads((P/'handoff.json').read_text());ok(h['identity']=='baseline-five-current17-existing-build-handoff-v1'and h['revision']=='64002531f0af5c06ad0402d0d80548102f8e6a38','distinct exact current source binding')
source=json.loads((N/'shared-current17-review-v1/runtime-plan-v1/source-checks.json').read_text())['source_map'];ok(h['source_sha256']==source and len(source)==808,'complete exact independently discovered808 source map')
records=json.loads((P/'raw/authority/original-build-terminals.json').read_text());ok(H(P/'raw/authority/original-build-terminals.json')==H(N/'shared640-build-terminals-recovered-v1.json')==h['recovered_original_terminal_authority']['sha256'],'authentic recovered original terminal document exact')
ok(len(records['commands'])==7 and records['source']['retrieval'].startswith('Read-only existing original chat'),'all7 preserved original command records, no inferred rerun')
byid={r['id']:r for r in records['commands']};ok(len(byid)==7,'unique authentic terminal IDs')
for backend in ('native','wasm'):
 b=h['builds'][backend];config=b['original_configure_terminal'];build=b['original_build_terminal'];ok(config==byid[config['id']]and build==byid[build['id']],'configure/build genuine record exact '+backend)
 ok(config['status']==build['status']=='completed'and config['exitCode']==build['exitCode']==b['returncode']==b['configure_returncode']==0,'historical successful status facts '+backend)
 shell=shlex.split(build['command']);tokens=shlex.split(shell[-1]);ok(tokens[:tokens.index('>')]==b['argv'],'recovered exact shell build argv matches binding '+backend)
 ok(b['argv'][-4:]==['--target','atlas_solver','--parallel','1'],'only explicit serial atlas_solver target '+backend)
 ok(any('[100%] Built target atlas_solver' in Path(x['path']).read_text()for x in b['logs']),'genuine target completion log '+backend)
 pin(b['resolved_compiler']);pin(b['current_object']);pin(b['current_scalar_library'])
fail=h['known_original_failed_build_terminal'];ok(fail==byid[fail['id']]and fail['status']=='failed'and fail['exitCode']==2,'original failed cache-lock build retained exact')
ok('PermissionError'in(P/'raw/logs/merged-wasm-build.log').read_text(),'genuine failure exception retained')
head=byid[h['historical_source_HEAD_observation']['terminal_id']];ok(head['output']['text'].startswith('30234bb0dd5995f49d3aaba669aaf9baa1336e3d\n')and not head['output']['truncated'],'historical HEAD30234 preserved distinct from current640')
# Independently enumerate every actual project dependency named by all retained .o.d records.
prefix='/private/tmp/atlas-md1997-publish-20261105/';expected=set()
for backend in ('native','wasm'):
 for p in (P/'raw'/backend).rglob('*.o.d'):
  text=p.read_text().replace('\\\n',' ')
  expected.update((backend,x)for x in re.findall(re.escape(prefix)+r'[^\s\\]+',text))
rows=h['actual_dependency_source_bindings'];observed={(x['backend'],x['original_project_path'])for x in rows};ok(expected==observed and len(expected)==76,'complete all76 actual project dependency observations independently enumerated')
old=json.loads((P/'raw/prior-numerical/source-before.json').read_text());after=json.loads((P/'raw/prior-numerical/source-after.json').read_text());ok(old==after and len(old)==146,'original146 beforeafter byte-object identity')
for r in rows:
 name=r['original_project_path'][len(prefix):];ok(r['retained640_source']['sha256']==source[name],'actual dependency corresponds exact current640 source '+name)
 if name in old:ok(r['historical146_prebuild_covered']is True and old[name]['sha256']==source[name]and r['historical_sha_matches']is True,'genuine historical dependency pin '+name)
 else:ok(name=='cpp/main.cpp'and r['historical146_prebuild_covered']is False and r['historical_sha_matches']is None,'only cppmain historical gap explicit '+r['backend'])
ok(len([n for n,r in old.items()if n in source and r['sha256']==source[n]])==145 and [n for n in old if n not in source]==['tests/test_solver.cpp'],'historical145 matches, numerical-only missing source disclosed')
ok(h['provenance_class'].startswith('late-readonly')and h['cpp_main']['historical146_prebuild_covered']is False and h['unresolved_provenance_fields'],'late-source/artifact/tool observations not historical prebuild claim')
# All exact generated17 model objects equal current source; complete native/Wasm/header/HTTP equality.
generated=[]
ctx=N/'current17-runtime-source-v1/source'
for backend in ('native','wasm'):
 g=h['generated'][backend];pin(g['header']);pin(g['json']);d=json.loads(Path(g['json']['path']).read_text());generated.append(d)
 ok(len(d['models'])==17 and len({x['id']for x in d['models']})==17,'full17 generated membership '+backend)
 for model in d['models']:ok(model==json.loads((ctx/'models'/(model['id']+'.json')).read_text()),'exact generated source definition '+backend+' '+model['id'])
ok(generated[0]==generated[1]and h['generated']['native']['header']['sha256']==h['generated']['wasm']['header']['sha256'],'native/Wasm generated headers and catalogue exact equal')
ok(h['generated']['native']['json']['sha256']==h['actual_http_catalogue']['sha256']=='19be5a4568830e2ac2d5e930ceb2f778a98a37c4bf31f700e6bc7ee3d41ccdac','actual HTTP catalogue bytes match generated17')
ok(generated[0]['sha256']=='4e31188499b5d19e52439451a709775f00e08a1f4d94570e40f43d825cd0e0a1','current17 runtime catalogue identity')
u=json.loads((P/'raw/authority/uploaded-manifest.json').read_text());upload={x['path']:x for x in u['files']};ok(u['file_count']==1564,'shared actual upload1564')
for role in ('module','wasm'):
 r=h['published_wasm_equality'][role];pin(r['borrowed_build']);pin(r['retained_actual_uploaded_asset']);ok(r['upload_manifest_row']==upload[r['upload_manifest_row']['path']],'exact original uploaded row '+role)
 ok(r['borrowed_build']['sha256']==r['retained_actual_uploaded_asset']['sha256']==r['upload_manifest_row']['sha256'],'exact borrowed/shipped asset equality '+role)
for r in h['artifacts'].values():pin(r)
(Q/'checks.json').write_text(json.dumps({'status':'PASS_BINDING_ONLY','checks':len(labels),'labels':labels,'limits':h['unresolved_provenance_fields'],'actual_engine_calls':0},indent=2)+'\n');print(json.dumps({'status':'PASS_BINDING_ONLY','checks':len(labels)}))
