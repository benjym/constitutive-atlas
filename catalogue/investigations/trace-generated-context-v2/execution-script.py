import pathlib,subprocess,json,hashlib,datetime,os,sys,platform
r=pathlib.Path('/Users/bmar5496/code/constitutive-atlas'); s=r/'catalogue/investigations/trace-generated-context-v2'; backend=sys.argv[1]; b=pathlib.Path('/private/tmp/atlas-trace-context-v2-'+backend+'-v1'); out=s/backend; assert not out.exists(), 'refusing to overwrite retained evidence'; out.mkdir()
env=os.environ.copy();env.update(EMCC_CORES='1',EM_CACHE=str(r/'.cache/emscripten'))
p=json.loads((s/'protocol.json').read_text())
for f,h in p['inputs'].items(): assert hashlib.sha256((r/f).read_bytes()).hexdigest()==h,f
receipt={'backend':backend,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':platform.platform(),'inputs':p['inputs'],'commands':[],'build_dir':str(b),'artifacts':{}}
def run(label,cmd):
 proc=subprocess.run(cmd,cwd=r,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 for name,data in [('stdout',proc.stdout),('stderr',proc.stderr)]: (out/(label+'.'+name+'.txt')).write_bytes(data)
 receipt['commands'].append({'label':label,'argv':cmd,'exit_code':proc.returncode})
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(backend,label,proc.returncode,flush=True)
 if proc.returncode: raise SystemExit(proc.returncode)
cmd=['cmake','-S',str(r/'cmake/trace-context-v2'),'-B',str(b),'-DCMAKE_BUILD_TYPE=Release']
if backend=='wasm': cmd=['/opt/homebrew/bin/emcmake']+cmd
run('configure',cmd)
run('build',['cmake','--build',str(b),'--target','atlas_trace_context','--parallel','1'])
artifacts=['atlas_trace_context'] if backend=='native' else ['atlas-trace-context.js','atlas-trace-context.wasm']
for f in artifacts:
 data=(b/f).read_bytes(); receipt['artifacts'][f]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
if backend=='native': run('observe',[str(b/'atlas_trace_context')])
else:
 driver=b/'observe.mjs'; driver.write_text("import fs from 'node:fs';\nimport create from './atlas-trace-context.js';\nconst m=await create({wasmBinary:fs.readFileSync(new URL('./atlas-trace-context.wasm',import.meta.url))});\nconsole.log(m.ccall('atlas_trace_context','string',[],[]));\n")
 (out/'observe.mjs').write_bytes(driver.read_bytes())
 run('observe',['/opt/homebrew/bin/node',str(driver)])
receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat(); (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
