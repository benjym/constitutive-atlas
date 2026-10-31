from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys
root=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(root))
from tools.research_rate_observations import checked_protocol,sha
study=root/'catalogue/investigations/barodesy2015-rates-v1';protocol=study/'protocol.json'
checked_protocol(protocol)
assert sha(protocol)=='f16ca12fc78ddbed79af78dc61ae9a17935174acf49b9cb77b37b63a35cb5a7d'
build=Path('/private/tmp/atlas-barodesy2015-native-v1');assert not build.exists(),'fresh build directory required'
receipt_path=study/'native-build.json';assert not receipt_path.exists()
commands=[['cmake','--version'],['c++','--version'],[sys.executable,'--version'],
 ['cmake','-S',str(root/'cmake/research'),'-B',str(build),'-DATLAS_MODEL_FILE='+str(root/'docs/ingestion/barodesy-sand/rate-study-v2/model-draft.json'),'-DATLAS_RESEARCH_TRANSPORT=rate'],
 ['cmake','--build',str(build),'--target','atlas_isolated','--parallel','1']]
rows=[]
for i,argv in enumerate(commands):
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 result=subprocess.run(argv,cwd=root,text=True,capture_output=True)
 doc={'argv':argv,'cwd':str(root),'started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
 path=study/f'native-build-command-{i}.json';assert not path.exists();path.write_text(json.dumps(doc,indent=2)+'\n')
 rows.append({'path':str(path.relative_to(root)),'sha256':sha(path),'returncode':result.returncode})
 print('Retained command',i,'returncode',result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
checked_protocol(protocol)
for source,target in ((build/'generated/models.hpp',study/'native-generated-models.hpp'),(build/'generated/models.json',study/'native-generated-models.json')):
 assert not target.exists();shutil.copyfile(source,target)
assert json.loads((build/'generated/models.json').read_text())==[json.loads((root/'docs/ingestion/barodesy-sand/rate-study-v2/model-draft.json').read_text())]
script=study/'native-build-script.py';assert not script.exists();shutil.copyfile(__file__,script)
receipt={'version':'isolated-rate-build-receipt-0.1','backend':'native','protocol_sha256':sha(protocol),'all_commands_succeeded':all(r['returncode']==0 for r in rows),'artifacts':{'native':{'path':str(build/'atlas_isolated'),'sha256':sha(build/'atlas_isolated')}},'commands':rows,'generated':{p.name:sha(p) for p in (study/'native-generated-models.hpp',study/'native-generated-models.json')},'orchestration_sha256':sha(script),'source_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=root,text=True,capture_output=True,check=True).stdout.strip()}
receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
print('Native isolated target built; no rate execution. Receipt SHA256',sha(receipt_path),flush=True)
