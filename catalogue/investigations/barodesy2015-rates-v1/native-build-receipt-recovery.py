from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(root))
from tools.research_rate_observations import checked_protocol,sha,digest
study=root/'catalogue/investigations/barodesy2015-rates-v1';protocol=study/'protocol.json';build=Path('/private/tmp/atlas-barodesy2015-native-v1')
checked_protocol(protocol);assert not (study/'native-build.json').exists()
model=json.loads((root/'docs/ingestion/barodesy-sand/rate-study-v2/model-draft.json').read_text());generated=json.loads((study/'native-generated-models.json').read_text())
assert generated['models']==[model] and generated['sha256']==digest([model])
assert (build/'generated/models.json').read_bytes()==(study/'native-generated-models.json').read_bytes()
assert (build/'generated/models.hpp').read_bytes()==(study/'native-generated-models.hpp').read_bytes()
original=study/'native-build-script-attempt-0.py';shutil.copyfile('/private/tmp/atlas-build-baro-native.py',original)
recovery=study/'native-build-receipt-recovery.py';shutil.copyfile(__file__,recovery)
(study/'native-build-attempt-0.json').write_text(json.dumps({'outcome':'postbuild-packaging-failed','build_commands_succeeded':True,'compiled_rate_calls':0,'reason':'Receipt assertion expected a JSON list; actual generated output is a catalogue object containing models. No compile/source/numerical failure.','script_sha256':sha(original),'recovery':'Validate models and sha256 in existing generated catalogue, preserve all build output and avoid rebuilding.'},indent=2)+'\n')
rows=[]
for i in range(5):
 path=study/f'native-build-command-{i}.json';record=json.loads(path.read_text());assert record['returncode']==0
 rows.append({'path':str(path.relative_to(root)),'sha256':sha(path),'returncode':record['returncode']})
receipt={'version':'isolated-rate-build-receipt-0.1','backend':'native','protocol_sha256':sha(protocol),'all_commands_succeeded':True,'artifacts':{'native':{'path':str(build/'atlas_isolated'),'sha256':sha(build/'atlas_isolated')}},'commands':rows,'generated':{p.name:sha(p) for p in (study/'native-generated-models.hpp',study/'native-generated-models.json')},'orchestration':{p.name:sha(p) for p in (original,recovery,study/'native-build-attempt-0.json')},'source_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=root,text=True,capture_output=True,check=True).stdout.strip(),'receipt_recovered_without_rebuild':True}
(study/'native-build.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Verified generated descriptor/header; recovered build receipt without rebuilding:',sha(study/'native-build.json'))
