"""Transport-only exact eight-stage Power profile execution; stops on any failure."""
import datetime,hashlib,json,os,pathlib,subprocess
if not __debug__:raise RuntimeError('Unoptimized execution required')
D=pathlib.Path(__file__).resolve().parent
P=D.parent/'current-profile-execution-v3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
f=read(D/'freeze-v2.json');plan=read(P/'plan.json');tool=read(P/'toolchain.json')
profile=next(x for x in plan['profiles']if x['profile']=='power-creep')
evidence=pathlib.Path(profile['output'])
def verify():
 for n,h in f['inputs'].items():
  if sha(pathlib.Path(n))!=h:raise RuntimeError('Execution input changed '+n)
def capture(argv,cwd,env,folder):
 folder.mkdir(parents=True,exist_ok=False)
 row=dict(argv=argv,cwd=cwd,env_changes={k:v for k,v in env.items()if os.environ.get(k)!=v},start=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='started')
 (folder/'process.json').write_text(json.dumps(row,indent=2)+'\n')
 with (folder/'stdout').open('wb')as out,(folder/'stderr').open('wb')as err:
  child=subprocess.Popen(argv,cwd=cwd,env=env,stdout=out,stderr=err);row['pid']=child.pid;row['returncode']=child.wait()
 row.update(end=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='observed',stdout_sha256=sha(folder/'stdout'),stderr_sha256=sha(folder/'stderr'))
 (folder/'process.json').write_text(json.dumps(row,indent=2)+'\n');return row['returncode']
def configure_receipt(stage):
 build=pathlib.Path(profile['native_build'if stage.startswith('native')else'wasm_build']);cache=build/'CMakeCache.txt';values={}
 for line in cache.read_text().splitlines():
  if line and not line.startswith(('#','//'))and ':'in line and '='in line:
   k,rest=line.split(':',1);_,v=rest.split('=',1)
   if k in ['CMAKE_CXX_COMPILER','CMAKE_C_COMPILER','CMAKE_AR','CMAKE_RANLIB','CMAKE_LINKER','CMAKE_MAKE_PROGRAM','CMAKE_OSX_SYSROOT','CMAKE_TOOLCHAIN_FILE','CMAKE_GENERATOR']:values[k]=v
 pins={}
 for k,v in values.items():
  if not v or not pathlib.Path(v).is_file():continue
  p=pathlib.Path(v);h=sha(p)
  if str(p)in tool['files']:
   if tool['files'][str(p)]['sha256']!=h:raise RuntimeError('Actual configure tool changed '+str(p))
  elif str(p)in ['/usr/bin/c++','/usr/bin/cc']:
   if str(p.resolve())!=str(p) or h!=tool['files']['/usr/bin/clang']['sha256']:raise RuntimeError('Unexpected compiler alias '+str(p))
  else:raise RuntimeError('Actual configure tool not frozen '+str(p))
  pins[k]=dict(path=str(p),realpath=str(p.resolve()),sha256=h)
 sdk=[k for k in tool['files']if k.endswith('/SDKSettings.json')]
 for n in sdk:
  if sha(pathlib.Path(n))!=tool['files'][n]['sha256']:raise RuntimeError('SDK settings changed')
 metadata={str(p.relative_to(build)):sha(p)for p in (build/'CMakeFiles').rglob('*')if p.is_file()and p.suffix in ['.cmake','.yaml']}
 receipt=dict(identity='current-power-actual-configure-v3',cache_sha256=sha(cache),values=values,actual_tool_pins=pins,sdk_settings={n:tool['files'][n]for n in sdk},compiler_metadata=metadata,passed=True)
 (evidence/(stage+'.inputs.json')).write_text(json.dumps(receipt,indent=2)+'\n')
# The original configure command/pre/post already ran exactly once under v1.
verify()
pre=read(evidence/'stage-receipts/native-configure.pre.json');post=read(evidence/'stage-receipts/native-configure.post.json')
if pre.get('passed')is not True or post.get('passed')is not True or post.get('exit_status')!=0:raise RuntimeError('Original configure did not pass')
configure_receipt('native-configure')
for st in profile['steps'][1:]:
 verify();env={**os.environ,**st['env']};name=st['stage'];folder=evidence/'processes'/name
 base=['python3','-B',str(P/'stage_receipt.py'),'--profile','power-creep','--stage',name]
 pre=base+['--phase','pre','--output',str(evidence/'stage-receipts'/(name+'.pre.json'))]
 if capture(pre,st['cwd'],env,evidence/'processes'/(name+'.pre')):raise RuntimeError('Precondition failed '+name)
 status=capture(st['argv'],st['cwd'],env,folder)
 post=base+['--phase','post','--output',str(evidence/'stage-receipts'/(name+'.post.json')),'--exit-status',str(status),'--stdout-file',str(folder/'stdout'),'--stderr-file',str(folder/'stderr')]
 poststatus=capture(post,st['cwd'],env,evidence/'processes'/(name+'.post'))
 verify();print(json.dumps(dict(stage=name,returncode=status,post_receipt_returncode=poststatus)),flush=True)
 if status or poststatus:raise RuntimeError('Stage failed '+name)
 if name.endswith('-configure'):configure_receipt(name)
