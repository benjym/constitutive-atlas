"""Verify frozen source/implementation, final receipt and prospective example/cases."""
from pathlib import Path
import json,hashlib,math
P=Path(__file__).resolve().parent.parent;R=P.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
counts={}
for directory,digest in [('source-v2','9637c8859d36def48aac3cb43785141395f69572e00e54a4689e33020e70123a'),('implementation-v1','7747199d17a8a3d9e6b324dde8ce731054e316babd5482696a6cafa3ba194c3e')]:
 path=P/directory/'manifest.json';assert sha(path)==digest;m=read(path)
 files=m['files']+([m['candidate']] if 'candidate' in m else [])
 for pin in files:assert sha(Path(pin['path']))==pin['sha256']
 counts[directory]=len(files)
E=P/'execution-v1';q=read(E/'qualification.json');review=read(E/'build-review.json');receipt=read(E/'build-receipt.json')
assert receipt['status']=='passed' and receipt['definition_sha256']==q['binding']['model_sha256']
assert receipt['artifacts']==q['binding']['artifacts'] and receipt['source_closure']==q['binding']['source_closure']
assert review['binding']==q['binding'] and review['status']=='accepted'
for key,name in [('qualification','qualification.json'),('independent_review','build-review.json')]:
 assert receipt[key]['path']==str((E/name).relative_to(R)) and receipt[key]['sha256']==sha(E/name)
I=P/'implementation-v1';cases=read(I/'package-cases.json');assert (I/'package-cases.json').read_bytes()==(E/'package-cases.json').read_bytes()
refs=read(I/'references.json');refmap={r['case']:r for r in refs['rows']};compared=0
for case in cases['cases']:
 name,seg=case['id'].split('-segment');ref=refmap[name]['refinements'][-1]['endpoints'][int(seg)-1]
 endpoint=case['expected'][-1]
 assert list(endpoint['context']['state'].values())==ref['state'] and endpoint['observables']['stress']==ref['stress'];compared+=11
example=read(I/'example.json');ref=refmap['multishear']['refinements'][-1]['endpoints'][0]
assert list(example['expected']['context']['state'].values())==ref['state'] and example['expected']['observables']['stress']==ref['stress'];compared+=11
assert cases['tolerance']=={'stress_absolute_Pa':.2,'void_ratio_absolute':2e-6}
output={'passed':True,'manifest_members':counts,'package_cases':len(cases['cases']),'example_and_package_reference_components':compared,'build_receipt_sha256':sha(E/'build-receipt.json'),'no_material_or_compiled_calls':True}
(Path(__file__).parent/'packet-check-results.json').write_text(json.dumps(output,indent=2)+'\n');print(output)
