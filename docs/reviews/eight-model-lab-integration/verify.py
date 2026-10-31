"""Production identities and retained eight-model browser evidence."""
from pathlib import Path
import json,hashlib,importlib.util
s=Path(__file__).resolve().parent;r=s.parents[2];read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(s/'integration-pins.json')
for n,h in pins['source_files'].items():assert sha(r/n)==h,n
for n,h in pins['artifacts'].items():
 p=Path(n)
 if p.exists():assert sha(p)==h,n
study=r/'catalogue/investigations/clay2013-preview-v2'
for p in(study/'models').glob('*.json'):assert p.read_bytes()==(r/'models'/p.name).read_bytes(),p.name
for n in ['models.hpp','models.json']:
 assert(r/'build/generated'/n).read_bytes()==(Path('/private/tmp/atlas-eight-model-wasm/generated')/n).read_bytes()==(study/'generated'/n).read_bytes()
archive=read(s/'archive.json');assert sha(r/archive['archived_path'])==archive['sha256']
assert read(s/'browser-export.json')['specification']==read(study/'browser/export.json')['specification']
spec=importlib.util.spec_from_file_location('clay_8',study/'assess.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.physical(read(s/'browser-export.json')['result'],'run')==m.physical(read(study/'browser/export.json')['result'],'run')
assert read(s/'browser-comparison.json')['pass']is True
log=(s/'production-parity.log').read_text();assert 'passed for 40 model/protocol combinations'in log
for n in ['4 cases','2 hypoplastic states','6 increments']:assert n in log,n
assert 'Ran 28 tests' in(s/'focused-tests.log').read_text()and'OK (skipped=3)'in(s/'focused-tests.log').read_text()
for n,h in read(s/'evidence-manifest.json').items():assert sha(s/n)==h,n
print(json.dumps({'production_evidence_pass':True,'local_models':8,'catalogue_entries':len(read(r/'catalogue/manifest.json')['models']),'production_protocol_pairs':40,'exact_browser_channels':True,'scientific_admission':False,'deployment':False},indent=2))
