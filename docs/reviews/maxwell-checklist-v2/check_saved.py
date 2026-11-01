"""Read-only retained evidence checks; writes only this review's results/receipts.
No reference generation, model evaluation, build, binary load or material call.
"""
import ast, hashlib, json, math, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/ingestion/maxwell-itasca900'; INT=BASE/'integration-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()
seen={}
def read(p):
 p=Path(p);p=p if p.is_absolute() else ROOT/p;b=p.read_bytes()
 seen[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]={'sha256':sha(b),'bytes':len(b)}
 return b
def obj(p):return json.loads(read(p))
modelpath='models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'; model=obj(modelpath)
assert seen[modelpath]['sha256']=='dc378ac0eb6956f7d0028b1fa5927d2906bf05e14ab45b116bc447c25e6b885f'
assert read(modelpath)==read(BASE/'candidate-v03.json')
# Reuse the exact frozen source closure, not the changing shared engine.
with tarfile.open(INT/'source-closure.tar.gz') as archive:
 members={m.name:m for m in archive.getmembers() if m.isfile()}; frozen={}
 for e in obj(INT/'execution-freeze.json')['files']:
  b=archive.extractfile(members[e['path']]).read();assert sha(b)==e['sha256'];frozen[e['path']]=b
 assert len(frozen)==92
 # Only these three pure assessor functions are executed. The collector,
 # generator, imports and module body are deliberately excluded.
 tree=ast.parse(frozen['tests/test_maxwell.py']); names={'norm_error','assess','assess_rows'}
 funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
 assert len(funcs)==3
 env={'math':math,'json':json,'MODEL':model['id'],'Z':[140000,80000,80000,3000,-2000,1000]}
 exec(compile(ast.Module(body=funcs,type_ignores=[]),'frozen-saved-assessor','exec'),env)
 errors={};calls={};cases=obj(INT/'reference-cases.json')['cases']
 for backend in ['native','wasm']:
  rows=obj(INT/f'{backend}-raw.json');errors[backend]=env['assess_rows'](cases,rows)
  tc=obj(INT/f'{backend}-transaction-cases.json')['cases'];tr=obj(INT/f'{backend}-transactions-raw.json')
  assert len(rows)==24 and len(tr)==len(tc)==14
  for c,r in zip(tc,tr):
   assert c['id']==r['id'] and len(r['calls'])==2
   parsed=[json.loads(x['stdout']) for x in r['calls']];assert parsed[0]==parsed[1]
   for x,d in zip(r['calls'],parsed):
    assert x['returncode']==(0 if c['ok'] else 1);errors[backend][c['id']]=env['assess'](c,d)
  calls[backend]=sum(len(r['calls']) for r in rows+tr);assert calls[backend]==76
 parity=[]
 for name in ['compare_backends.py','compare_backends_v2.py']:
  tree=ast.parse(read(INT/name));f=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compare'];assert len(f)==1
  pe={'math':math,'COUNT':0,'MAX_STRESS':0,'MAX_STRAIN':0};exec(compile(ast.Module(body=f,type_ignores=[]),name,'exec'),pe)
  failure=None
  try:
   for suffix in ['raw','transactions-raw']:
    ns=obj(INT/f'native-{suffix}.json');ws=obj(INT/f'wasm-{suffix}.json')
    assert [r['id'] for r in ns]==[r['id'] for r in ws]
    for n,w in zip(ns,ws):
     for nc,wc in zip(n['calls'],w['calls']):pe['compare'](json.loads(nc['stdout']),json.loads(wc['stdout']))
  except AssertionError as e:failure=repr(e)
  parity.append({'assessor':name,'passed':failure is None,'failure':failure,'comparisons':pe['COUNT'],'max_stress_Pa':pe['MAX_STRESS'],'max_strain_rate':pe['MAX_STRAIN']})
 assert parity[0]['failure'] and parity[1]['passed'] and parity[1]['comparisons']==5962
# Preserve existing explicit-user authority; this agent review is supplementary.
prior=obj('docs/admission/maxwell-approved-v1/approval.json')
assert prior['id']=='maxwell-user-approval-v1' and prior['definition']['sha256']==sha(read(modelpath))
assert prior['approval_authority']['kind']=='explicit-user-instruction'
for e in obj('docs/admission/maxwell-approved-v1/source-retention.json')['sources']:
 assert sha(read(e['durable_private_path']))==e['sha256']
read('docs/admission/maxwell-approved-v1/README.md')
# Exact primary bytes retained privately; only hashes and locators are emitted.
receipt=obj(BASE/'source-receipts.json');retention=obj(BASE/'retention-v1/plan.json');assert retention['source_receipt_sha256']==sha(read(BASE/'source-receipts.json'))
sources=[]
for e,r in zip(receipt['sources'],retention['files']):
 b=read(r['destination']);assert sha(b)==e['sha256']==r['sha256'];assert len(b)==r['bytes']==e['bytes'];sources.append({'id':e['id'],'private_path':r['destination'],'sha256':sha(b),'bytes':len(b)})
# Bind saved historical output manifests and all review/evidence packet files.
for directory in [BASE,ROOT/'docs/reviews/maxwell-scientific-agent-v1',ROOT/'docs/reviews/maxwell-scientific-integration-v1']:
 for p in sorted(directory.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts and p.name != 'DELIVERY.md':read(p)
for e in obj('docs/reviews/maxwell-scientific-agent-v1/manifest.json')['files']:assert sha(read(e['path']))==e['sha256']
for p in ['docs/AGENT_REVIEW_POLICY.md','docs/MODEL_DELIVERY_CHECKLIST.md','docs/FORMULATION_CONTRACT.md','docs/TIME_ODE_API.md','docs/TIMED_SCHEDULES.md','schemas/agent-review.schema.json','docs/AGENT_REVIEW_TEMPLATE.json','atlas/agent_review.py']:read(p)
# Exact continuous algebra was independently inspected from the original pages;
# this run reuses saved references and does not regenerate them.
result={'passed':True,'run_id':'/root/maxwell_checklist_review','model_sha256':sha(read(modelpath)),'frozen_source_members':len(frozen),'saved_calls_per_backend':calls,'saved_assessor_errors_Pa':errors,'parity':parity,'durably_retained_originals':sources,'compiled_calls':0,'builds':0,'reference_generation':0,'scope':'supplementary agent review of existing frozen CLI/ABI qualification only','existing_user_approval':'maxwell-user-approval-v1','prior_durable_retention_verified':True}
(OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'receipts.json').write_text(json.dumps({'files':[{'path':p,**e} for p,e in sorted(seen.items())]},indent=2)+'\n')
print(json.dumps({'passed':True,'frozen_source_members':len(frozen),'saved_calls_per_backend':calls,'original_parity_passed':parity[0]['passed'],'parity_v2_comparisons':parity[1]['comparisons'],'durable_originals':len(sources),'compiled_calls':0,'reference_generation':0},indent=2))
