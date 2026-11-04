"""Read/hash only. Does not run artifacts, Git, compilers or tool probes."""
from pathlib import Path
import hashlib,json,re,shlex,datetime
R=Path('/Users/bmar5496/code/constitutive-atlas');N=R/'docs/delivery/unheld-finalisation-20261105-v1';O=N/'shared640-artifact-binding-v1';B=Path('/private/tmp/atlas-md1997-direct-app-v1');S=N/'current17-runtime-source-v1/source';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');REV='64002531f0af5c06ad0402d0d80548102f8e6a38'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(v):return json.dumps(v,indent=2)+'\n'
def pin(p):p=Path(p);return{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def retain(p,label):
 p=Path(p);dest=O/'raw'/label;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes());return{'original':pin(p),'retained':pin(dest)}
observed=datetime.datetime.now(datetime.timezone.utc).isoformat();source_manifest=N/'current17-runtime-source-v1/manifest.json';manifest=json.loads(source_manifest.read_text());source={row['path']:row['sha256']for row in manifest['files']};assert len(source)==808
for n,h in source.items():assert sha(S/n)==h,n
prior=json.loads((B/'merged-ci-numerical-v1/source-before.json').read_text());matching=[n for n,r in prior.items()if source.get(n)==r['sha256']];missing=[n for n in prior if n not in source];changed=[n for n,r in prior.items()if n in source and source[n]!=r['sha256']];assert len(prior)==146 and len(matching)==145 and missing==['tests/test_solver.cpp']and not changed
artifacts={'native':pin(B/'merged-native/atlas_solver'),'module':pin(B/'merged-wasm/atlas.js'),'wasm':pin(B/'merged-wasm/atlas.wasm'),'node':pin(Path('/opt/homebrew/bin/node').resolve())}
generated={};raw=[];builds={};dependencies=[];projectprefix='/private/tmp/atlas-md1997-publish-20261105/'
for backend in('native','wasm'):
 d=B/('merged-'+backend);generated[backend]={'header':pin(d/'generated/models.hpp'),'json':pin(d/'generated/models.json')}
 meta=json.loads((d/'generated/models.json').read_text());assert len(meta['models'])==17 and meta['sha256']=='4e31188499b5d19e52439451a709775f00e08a1f4d94570e40f43d825cd0e0a1'
 assert generated[backend]['json']['sha256']=='19be5a4568830e2ac2d5e930ceb2f778a98a37c4bf31f700e6bc7ee3d41ccdac'
 for name in ('models.hpp','models.json'):raw.append(retain(d/'generated'/name,'generated/'+name))
 paths=[d/'CMakeCache.txt',d/'CMakeFiles/atlas_solver.dir/flags.make',d/'CMakeFiles/atlas_solver.dir/link.txt',d/'CMakeFiles/atlas_solver.dir/build.make',d/'CMakeFiles/atlas_solver.dir/DependInfo.cmake',d/'CMakeFiles/atlas_solver.dir/cpp/main.cpp.o.d',d/'CMakeFiles/4.4.3/CMakeCXXCompiler.cmake']
 paths += list((d/'CMakeFiles/atlas_scalar_functions.dir').rglob('*.o.d'))
 paths += [p for p in(d/'CMakeFiles/atlas_solver.dir/objects1.rsp',d/'CMakeFiles/atlas_solver.dir/linkLibs.rsp',d/'CMakeFiles/atlas_solver.dir/includes_CXX.rsp',d/'CMakeFiles/atlas_scalar_functions.dir/link.txt',d/'CMakeFiles/atlas_scalar_functions.dir/flags.make')if p.is_file()]
 for p in paths:raw.append(retain(p,backend+'/'+str(p.relative_to(d))))
 project=set();external=set();generated_deps=set()
 for p in paths:
  if p.name.endswith('.o.d'):
   text=p.read_text().replace('\\\n',' ')
   for token in shlex.split(text)[1:]:
    if token.startswith(projectprefix):project.add(token[len(projectprefix):])
    elif token.startswith(str(d)+'/generated/'):generated_deps.add(token)
    else:external.add(token)
 for n in sorted(project):
  assert n in source and sha(S/n)==source[n],n
  dependencies.append({'backend':backend,'original_project_path':projectprefix+n,'retained640_source':pin(S/n),'historical146_prebuild_covered':n in prior,'historical_sha_matches':prior.get(n,{}).get('sha256')==source[n]if n in prior else None})
 compiler=Path('/usr/bin/c++')if backend=='native'else Path('/opt/homebrew/Cellar/emscripten/6.0.8/libexec/em++')
 logs=[B/('merged-'+backend+'-configure.log'),B/('merged-native-solver-build.log'if backend=='native'else'merged-wasm-build-cache-access.log')]
 if backend=='wasm':logs.append(B/'merged-wasm-build.log')
 for p in logs:raw.append(retain(p,'logs/'+p.name))
 builds[backend]={'returncode':None,'configure_returncode':None,'argv':None,'historical_outer_status_argv':'not available in retained evidence; never inferred from successful log','observed_log_completion':'configure and corrected solver build logs record successful target completion','logs':[pin(p)for p in logs],'compiler_version_logs':[pin(B/('merged-'+backend+'-configure.log')),pin(d/'CMakeFiles/4.4.3/CMakeCXXCompiler.cmake')],'resolved_compiler':pin(compiler.resolve()),'generated_dependency_paths':sorted(generated_deps),'external_dependency_paths_not_hashed':sorted(external),'current_object':pin(d/'CMakeFiles/atlas_solver.dir/cpp/main.cpp.o'),'current_scalar_library':pin(d/'libatlas_scalar_functions.a')}
assert generated['native']['header']['sha256']==generated['wasm']['header']['sha256']
upload=json.loads((B/'final-live-upload/manifest.json').read_text());u={r['path']:r for r in upload['files']};publication={}
for role,name in [('module','atlas.js'),('wasm','atlas.wasm')]:
 p=B/'final-live-upload/assets'/name;assert sha(p)==artifacts[role]['sha256']==u[name]['sha256'];publication[role]={'borrowed_build':artifacts[role],'retained_actual_uploaded_asset':pin(p),'upload_manifest_row':u[name]}
http=N/'current17-live-metadata-v1/models.json';assert sha(http)==generated['native']['json']['sha256']
for p in sorted((B/'merged-ci-numerical-v1').glob('*.json')):raw.append(retain(p,'prior-numerical/'+p.name))
for p in(B/'final-live-upload/manifest.json',B/'final-live-artifact-checks.json',http,source_manifest,R/'docs/ingestion/manzari-dafalias-1997/DELIVERY.md'):raw.append(retain(p,'authority/'+('source-context-manifest.json'if p==source_manifest else'uploaded-manifest.json'if p==B/'final-live-upload/manifest.json'else p.name)))
main=S/'cpp/main.cpp';assert sha(main)==sha(W/'cpp/main.cpp')
receipt={'identity':'baseline-five-current17-existing-build-handoff-v1','revision':REV,'author_run':'/root/publication_operations_review','measurement_time_utc':observed,'provenance_class':'late-readonly-existing-build-binding; not a historical prebuild freeze','source_sha256':source,'source_map_class':'fresh current640 retained sourcecontext verification; not claimed as original build-before inventory','source_context_manifest':pin(source_manifest),'artifacts':artifacts,'generated':generated,'builds':builds,'build_tools':{k:pin(Path(p).resolve())for k,p in{'cmake':'/opt/homebrew/bin/cmake','native_cxx':'/usr/bin/c++','emcmake':'/opt/homebrew/bin/emcmake','emcc':'/opt/homebrew/bin/emcc'}.items()},'build_tool_measurement_class':'late current filesystem bytes; versions from retained configure/compiler metadata, no new version probes','raw_provenance':[r['retained']for r in raw],'retention_map':raw,'prior_inventory':{'count':146,'matching_current640':145,'not_in808':missing,'changed':changed,'all_original_before_after_inventory_bytes_retained':True},'actual_dependency_source_bindings':dependencies,'cpp_main':{'current640':pin(main),'retained702':pin(W/'cpp/main.cpp'),'bytes_equal':True,'historical146_prebuild_covered':False,'limitation':'object .d names original cpp/main.cpp; current702 and retained640 byte identity does not retroactively create a prebuild hash observation'},'published_wasm_equality':publication,'actual_http_catalogue':pin(http),'known_prior_failure':'merged-wasm-build.log cache lock PermissionError retained; corrected cache-access build log successful, statuses not fabricated','unresolved_provenance_fields':['historical solver configure/build exact outer returncode and argv unavailable','historical146 inventory omits cpp/main.cpp','all current808 source/tool/object hashes are late observations, not original prebuild receipts'],'reuse_acceptance':None,'scope':'No artifact/tool/engine/module executed; no browser/network/Git/sourceinstall; separate independent review and actual original scientific gates required'}
terminals=N/'shared640-build-terminals-recovered-v1.json';terminal_data=json.loads(terminals.read_text());terminal_retention=retain(terminals,'authority/original-build-terminals.json');receipt['raw_provenance'].append(terminal_retention['retained']);receipt['retention_map'].append(terminal_retention)
receipt['recovered_original_terminal_authority']=pin(terminals)
receipt['historical_source_HEAD_observation']={'revision':'30234bb0dd5995f49d3aaba669aaf9baa1336e3d','terminal_id':'exec-4203ce07-c7f7-4b48-af56-f554684d7f28','clean_porcelain_output':True,'scope':'original build-root observation; current binding revision640 is not substituted for historical HEAD'}
for backend in ('native','wasm'):
 buildlog='merged-native-solver-build.log' if backend=='native' else 'merged-wasm-build-cache-access.log'
 configurelog='merged-'+backend+'-configure.log'
 build=next(c for c in terminal_data['commands'] if buildlog in c['command'])
 configure=next(c for c in terminal_data['commands'] if configurelog in c['command'])
 assert build['exitCode']==configure['exitCode']==0 and build['status']==configure['status']=='completed'
 def argv(c):
  tokens=shlex.split(shlex.split(c['command'])[2]);return tokens[:tokens.index('>')]
 receipt['builds'][backend].update({'returncode':build['exitCode'],'configure_returncode':configure['exitCode'],'argv':argv(build),'configure_argv':argv(configure),'original_build_terminal':build,'original_configure_terminal':configure,'historical_outer_status_argv':'genuine original commandExecution records recovered read-only from original owner chat; no rerun/inference'})
receipt['known_original_failed_build_terminal']=next(c for c in terminal_data['commands'] if c['exitCode']==2)
receipt['unresolved_provenance_fields']=['historical146 inventory omits cpp/main.cpp','all current808 source/tool/object hashes are late observations, not original prebuild receipts']
(O/'handoff.json').write_text(js(receipt));(O/'dependency-source-bindings.json').write_text(js(dependencies));print(js({'handoff_sha256':sha(O/'handoff.json'),'artifacts':artifacts,'project_dependency_observations':len(dependencies),'retained_raw_files':len(raw),'prior_inventory146_matches145':True,'exact_uploaded_wasm_module':True,'historical_outer_status_argv':'genuine original recovered terminals bound'}))
