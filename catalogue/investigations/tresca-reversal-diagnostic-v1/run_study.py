"""Prospective frozen private laboratory build; one explicit target/backend serially."""
from pathlib import Path
import json,hashlib,subprocess,sys,time,shutil
P=Path(__file__).parent;ROOT=P.parents[2];STAGE=Path('/private/tmp/atlas-tresca-reversal-diagnostic-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def process(name,cmd,stdin=None):
 t=time.monotonic()
 if stdin:
  with stdin.open()as src:r=subprocess.run(cmd,stdin=src,capture_output=True,text=True,cwd=ROOT,timeout=60)
 else:r=subprocess.run(cmd,capture_output=True,text=True,cwd=ROOT,timeout=60)
 (P/(name+'-process.json')).write_text(json.dumps({'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds':time.monotonic()-t},indent=2)+'\n');print(name,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.stderr)
 return r.stdout
if __name__=='__main__':
 phase=sys.argv[1]
 if phase=='freeze':
  assert not(P/'prospective-freeze.json').exists()
  pins={}
  for p in (P/'frozen/cpp').rglob('*'):
   if p.is_file():pins[str(p.relative_to(P/'frozen'))]=sha(p)
  for n in ['atlas/compiler.py','atlas/model.py','schemas/model-v0.3.schema.json','docs/reviews/certified-spectral-range-v1/exact.py']:pins[n]=sha(ROOT/n)
  (P/'source-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
  files={str(p.relative_to(ROOT)):sha(p)for p in P.rglob('*')if p.is_file()and '__pycache__'not in p.parts}
  (P/'prospective-freeze.json').write_text(json.dumps({'version':'tresca-reversal-diagnostic-prospective-0.1','files':files,'no_material_execution_before_freeze':True},indent=2)+'\n')
  for p in P.rglob('*'):
   if p.is_file()and '__pycache__'not in p.parts:
    dst=STAGE/p.relative_to(P);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
  print('Frozen',len(files),'files before build')
 else:
  assert phase in ['native','wasm']
  for n,h in json.loads((P/'prospective-freeze.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
  for n,h in json.loads((P/'source-pins.json').read_text()).items():assert sha(ROOT/n)==h,n
  for p in [*list((P/'frozen').rglob('*')),*list((P/'generated').rglob('*')),*list((P/'instrumented').rglob('*')),P/'driver.cpp',P/'CMakeLists.txt',P/'inputs.hpp']:
   if p.is_file():assert sha(p)==sha(STAGE/p.relative_to(P))
  prefix=['emcmake']if phase=='wasm'else []
  process(phase+'-configure',prefix+['cmake','-S',str(STAGE),'-B',str(STAGE/phase),'-DCMAKE_BUILD_TYPE=Release'])
  process(phase+'-build',['cmake','--build',str(STAGE/phase),'--target','atlas_tresca_reversal_diagnostic','--parallel','1'])
  cmd=[str(STAGE/'native/atlas_tresca_reversal_diagnostic')]if phase=='native'else ['node',str(STAGE/'wasm/tresca-reversal-diagnostic.js')]
  out=process(phase+'-execution',cmd);(P/(phase+'-response.json')).write_text(out)
  artifacts=[STAGE/'native/atlas_tresca_reversal_diagnostic']if phase=='native'else [STAGE/'wasm/tresca-reversal-diagnostic.js',STAGE/'wasm/tresca-reversal-diagnostic.wasm']
  (P/(phase+'-artifacts.json')).write_text(json.dumps({str(p):sha(p)for p in artifacts},indent=2)+'\n')
