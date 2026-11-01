"""Transport-only exact reviewed j2 profile execution; stops on any failure."""
import datetime,hashlib,json,os,pathlib,subprocess,re
if not __debug__:raise RuntimeError('Unoptimized execution required')
D=pathlib.Path(__file__).resolve().parent
P=D.parent/'current-profile-execution-v3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
f=read(D/'freeze.json');plan=read(P/'plan.json');tool=read(P/'toolchain.json')
profile=next(x for x in plan['profiles']if x['profile']=='j2')
evidence=pathlib.Path(profile['output'])
actual_binding_hashes={}
def verify():
 for n,h in f['inputs'].items():
  if sha(pathlib.Path(n))!=h:raise RuntimeError('Execution input changed '+n)
 if {str(p)for p in evidence.glob('*.inputs.json')}!=set(actual_binding_hashes):raise RuntimeError('Actualconfigure binding inventory changed')
 for name,h in actual_binding_hashes.items():
  receipt=pathlib.Path(name)
  if sha(receipt)!=h:raise RuntimeError('Actualconfigure binding changed')
  binding=read(receipt)
  build=pathlib.Path(binding.get('build',profile['native_build']))
  if sha(build/'CMakeCache.txt')!=binding['cache_sha256']:raise RuntimeError('Actual cache changed')
  for rel,digest in binding.get('compiler_binding_files',{}).items():
   if sha(build/rel)!=digest:raise RuntimeError('Actual compiler metadata changed')
  if binding.get('passed')is not True:raise RuntimeError('Actualconfigure binding failed')
  for row in binding['actual_tool_pins'].values():
   p=pathlib.Path(row['path'])
   if str(p.resolve())!=row['realpath']or sha(p)!=row['sha256']:raise RuntimeError('Actualconfigure tool changed '+str(p))
def capture(argv,cwd,env,folder):
 verify()
 folder.mkdir(parents=True,exist_ok=False)
 row=dict(argv=argv,cwd=cwd,env_changes={k:v for k,v in env.items()if os.environ.get(k)!=v},start=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='started')
 (folder/'process.json').write_text(json.dumps(row,indent=2)+'\n')
 with (folder/'stdout').open('wb')as out,(folder/'stderr').open('wb')as err:
  child=subprocess.Popen(argv,cwd=cwd,env=env,stdout=out,stderr=err);row['pid']=child.pid;row['returncode']=child.wait()
 row.update(end=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='observed',stdout_sha256=sha(folder/'stdout'),stderr_sha256=sha(folder/'stderr'))
 (folder/'process.json').write_text(json.dumps(row,indent=2)+'\n');verify();return row['returncode']
def configure_receipt(stage):
 build=pathlib.Path(profile['native_build'if stage.startswith('native')else'wasm_build']);cache=build/'CMakeCache.txt';values={}
 for line in cache.read_text().splitlines():
  if line and not line.startswith(('#','//'))and ':'in line and '='in line:
   k,rest=line.split(':',1);_,v=rest.split('=',1)
   if k in ['CMAKE_CXX_COMPILER','CMAKE_C_COMPILER','CMAKE_AR','CMAKE_RANLIB','CMAKE_LINKER','CMAKE_MAKE_PROGRAM','CMAKE_OSX_SYSROOT','CMAKE_TOOLCHAIN_FILE','CMAKE_GENERATOR']:values[k]=v
 compiler_binding_files={}
 for meta in sorted((build/'CMakeFiles').glob('*/CMake*Compiler.cmake')):
  compiler_binding_files[str(meta.relative_to(build))]=sha(meta)
  for key,value in re.findall(r'^set\((CMAKE_(?:CXX_COMPILER|C_COMPILER|AR|RANLIB)) "([^"]+)"\)$',meta.read_text(),re.MULTILINE):
   if key in values and values[key]!=value:raise RuntimeError('Conflicting actual compiler '+key)
   values[key]=value
 required=['CMAKE_CXX_COMPILER','CMAKE_C_COMPILER','CMAKE_AR','CMAKE_RANLIB','CMAKE_MAKE_PROGRAM','CMAKE_GENERATOR']
 if any(k not in values for k in required):raise RuntimeError('Incomplete actual compiler configuration')
 pins={}
 for k,v in values.items():
  if k=='CMAKE_GENERATOR':
   if v!='Unix Makefiles':raise RuntimeError('Unexpected generator')
   continue
  if k=='CMAKE_OSX_SYSROOT':
   if v:raise RuntimeError('Unexpected explicit sysroot')
   continue
  if not v or not pathlib.Path(v).is_absolute()or not pathlib.Path(v).is_file():raise RuntimeError('Missing actual configure tool '+k+'='+v)
  p=pathlib.Path(v);h=sha(p)
  if str(p)in tool['files']:
   if tool['files'][str(p)]['sha256']!=h or tool['files'][str(p)]['realpath']!=str(p.resolve()):raise RuntimeError('Actual configure tool changed '+str(p))
  elif str(p)in ['/usr/bin/c++','/usr/bin/cc']:
   if str(p.resolve())!=str(p) or h!=tool['files']['/usr/bin/clang']['sha256']:raise RuntimeError('Unexpected compiler alias '+str(p))
  else:raise RuntimeError('Actual configure tool not frozen '+str(p))
  pins[k]=dict(path=str(p),realpath=str(p.resolve()),sha256=h)
 sdk=[k for k in tool['files']if k.endswith('/SDKSettings.json')]
 for n in sdk:
  if sha(pathlib.Path(n))!=tool['files'][n]['sha256']:raise RuntimeError('SDK settings changed')
 metadata={str(p.relative_to(build)):sha(p)for p in (build/'CMakeFiles').rglob('*')if p.is_file()and p.suffix in ['.cmake','.yaml']}
 receipt=dict(identity='current-profile-actual-configure-v3',profile=profile['profile'],build=str(build),compiler_binding_files=compiler_binding_files,cache_sha256=sha(cache),values=values,actual_tool_pins=pins,sdk_settings={n:tool['files'][n]for n in sdk},compiler_metadata=metadata,passed=True)
 path=evidence/(stage+'.inputs.json')
 with path.open('x')as stream:stream.write(json.dumps(receipt,indent=2)+'\n')
 actual_binding_hashes[str(path)]=sha(path)
 verify()
for st in profile['steps']:
 verify();env={**os.environ,**st['env']};name=st['stage'];folder=evidence/'processes'/name
 base=['python3','-B',str(P/'stage_receipt.py'),'--profile','j2','--stage',name]
 pre=base+['--phase','pre','--output',str(evidence/'stage-receipts'/(name+'.pre.json'))]
 if capture(pre,st['cwd'],env,evidence/'processes'/(name+'.pre')):raise RuntimeError('Precondition failed '+name)
 status=capture(st['argv'],st['cwd'],env,folder)
 post=base+['--phase','post','--output',str(evidence/'stage-receipts'/(name+'.post.json')),'--exit-status',str(status),'--stdout-file',str(folder/'stdout'),'--stderr-file',str(folder/'stderr')]
 poststatus=capture(post,st['cwd'],env,evidence/'processes'/(name+'.post'))
 verify();print(json.dumps(dict(stage=name,returncode=status,post_receipt_returncode=poststatus)),flush=True)
 if status or poststatus:raise RuntimeError('Stage failed '+name)
 if name.endswith('-configure'):configure_receipt(name)
