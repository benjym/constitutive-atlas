import json,hashlib,importlib.util,sys,ast,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;sys.path.insert(0,str(R))
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
P=R/'docs/ingestion/vibe-2026/maxwell-refresh-v1';B=R/'docs/ingestion/maxwell-itasca900/integration-v1'
assert h(P/'manifest.json')=='e797a05de66c2cba7c99a15b59d9cb4ba99770b3bed6f344a9001fcddfe01d77'
manifest=read(P/'manifest.json')
for f in manifest['files']:assert h(R/f['path'])==f['sha256'] and (R/f['path']).stat().st_size==f['bytes']
p=read(P/'plan.json')
for f in p['files']:assert h(R/f['path'])==f['sha256']
for name,v in p['source_manifest']['files'].items():assert h(R/name)==v
encoded=json.dumps(p['source_manifest']['files'],sort_keys=True,separators=(',',':')).encode();assert hashlib.sha256(encoded).hexdigest()==p['source_manifest']['sha256']
source=R/'tools/qualify_maxwell_refresh.py';ast.parse(source.read_text())
collector=load('independent_maxwell_refresh_source',source);m=load('independent_original_maxwell_assessor',R/'tests/test_maxwell.py');tx=load('independent_original_maxwell_transactions',B/'check_transactions.py')
assert collector.guard(P/'plan.json')[0]==p
cases=read(B/'reference-cases.json');assert len(cases['cases'])==24 and p['original_policy']==cases['policy']
for name,cid in collector.PRESETS.items():assert read(R/'examples/maxwell'/f'{name}.json')==next(c['specification'] for c in cases['cases'] if c['id']==cid)
assessments={}
for backend in ['native','wasm']:
 rows=read(B/f'{backend}-raw.json');m.assess_rows(cases['cases'],rows)
 tc=tx.cases_for(B/f'{backend}-raw.json');tr=read(B/f'{backend}-transactions-raw.json');assert len(tc)==14;tx.assess(tc,tr)
 assessments[backend]={'reference_cases':len(rows),'transaction_cases':len(tr),'status':'historical-saved-data-pass-only'}
comparer=B/'compare_backends_v2.py';prefix=comparer.read_text().split("for suffix in ('raw','transactions-raw'):")[0];n={'__file__':str(comparer)};exec(compile(prefix,str(comparer),'exec'),n)
for suffix in ['raw','transactions-raw']:
 nr,wr=read(B/f'native-{suffix}.json'),read(B/f'wasm-{suffix}.json');assert [r['id'] for r in nr]==[r['id'] for r in wr]
 for a,b in zip(nr,wr):
  assert len(a['calls'])==len(b['calls'])==2
  for x,y in zip(a['calls'],b['calls']):assert x['returncode']==y['returncode'];n['compare'](json.loads(x['stdout']),json.loads(y['stdout']))
assert n['COUNT']==5962
for backend in ['native','wasm']:
 command=p['serial_build_commands'][backend][1];assert command[-4:]==['--target','atlas_maxwell_solver','--parallel','1']
# Source gate identity, complete original assessors and packager remain unchanged from merged commit.
original=['tools/build_maxwell_laboratory.py','tests/test_maxwell.py','tools/test_maxwell_wasm.mjs','tools/test_maxwell_public_presets.mjs',str(comparer.relative_to(R)),str((B/'check_transactions.py').relative_to(R)),str((B/'reference-cases.json').relative_to(R))]
for path in original:assert subprocess.check_output(['git','show','8543a0dbe:'+path],cwd=R)==(R/path).read_bytes()
result={'status':'accepted-prospective-source-only','manifest_sha256':h(P/'manifest.json'),'plan_sha256':h(P/'plan.json'),'collector_sha256':h(source),'source_pins':len(p['source_manifest']['files']),'additional_pins':len(p['files']),'original_source_byte_identity':original,'historical_reassessment':assessments,'historical_parity_comparisons':n['COUNT'],'maximum_stress_difference_Pa':n['MAX_STRESS'],'maximum_strain_difference':n['MAX_STRAIN'],'compiled_calls':0,'blocking_findings':[],'requires':'Fresh genuine native then Wasm build/material execution plus exact separate-agent build review before finalize/package','cleanup':'No processes/builds/downloads/temp trees created; no historical files modified.'}
(O/'maxwell-source-v1-decision.json').write_text(json.dumps(result,indent=2)+'\n')
mm={'files':[{'path':str((O/name).relative_to(R)),'sha256':h(O/name)} for name in ['check_maxwell_source_v1.py','maxwell-source-v1-decision.json']]};(O/'maxwell-source-v1-manifest.json').write_text(json.dumps(mm,indent=2)+'\n');print(json.dumps(result,indent=2));print('review_manifest',h(O/'maxwell-source-v1-manifest.json'))
