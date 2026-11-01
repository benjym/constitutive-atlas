"""Read-only prospective merged-source check; no compiled execution."""
from pathlib import Path
import json,hashlib,subprocess,sys,re
S=Path(sys.argv[1]);B=S/'docs/ingestion/orthotropic-ogs/integration-v3/origin-before';H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=json.loads((S/'docs/ingestion/orthotropic-ogs/integration-v3/PLAN.json').read_text())
for p,h in plan['files'].items():assert sha(S/p)==h,p
paths=['web/app.js','tools/build_web.py','tools/build_maxwell_laboratory.py','.github/workflows/verify.yml','catalogue/manifest.json','catalogue/approved-models.json']
for p in paths:assert not any(m in (S/p).read_text() for m in ['<<<<<<<','=======\n','>>>>>>>']),p
for f in ['manifest.json','approved-models.json']:
 a=json.loads((B/'catalogue'/f).read_text());b=json.loads((S/'catalogue'/f).read_text());filtered=[r for r in b['models'] if r.get('id')!='orthotropic-linear-elastic-ogs' and r.get('model_id')!='orthotropic-linear-elastic-ogs'];assert filtered==a['models'];assert len(b['models'])==len(a['models'])+1
assert (B/'tools/build_maxwell_laboratory.py').read_bytes()==(S/'tools/build_maxwell_laboratory.py').read_bytes()
# Every original line in the workflow survives in order; additions must not drop old gates.
a=(B/'.github/workflows/verify.yml').read_text().splitlines();b=(S/'.github/workflows/verify.yml').read_text().splitlines();it=iter(b);assert all(any(x==v for x in it) for v in a)
app=(S/'web/app.js').read_text();assert "setupOrthotropicLaboratory({cancelOrdinary:()=>cancel('')})" in app
for name in ['setupTimedLaboratory','setupSlsLaboratory','setupPathLaboratory','setupMaxwellLaboratory','setupImplicitPathLaboratory','setupJ2Laboratory']:assert app.count(name)==(B/'web/app.js').read_text().count(name),name
assert "if(active)$('model').value=id;" in app and "if(active&&id==='lade-duncan-1975-midpoint-elastic-eq19-gap-v4')" in app
segment=app[app.index("if(timedView?.supports(id))"):app.index("if(j2View?.active)j2View.select(false);",app.index("if(timedView?.supports(id))")+len("if(timedView?.supports(id))"))] if False else app
assert "}} return active;\n    if(active)" not in segment
workflow=(S/'.github/workflows/verify.yml').read_text();job=None;uploads=[];shell=[]
lines=workflow.splitlines()
for i,l in enumerate(lines):
 m=re.match(r'^  ([a-zA-Z0-9_-]+):$',l)
 if m:job=m.group(1)
 if l.strip().startswith('name: orthotropic-'):uploads.append({'job':job,'artifact':l.strip().split(': ',1)[1]})
 if l.strip()=='run: |':
  indent=len(l)-len(l.lstrip());block=[]
  for q in lines[i+1:]:
   if q.strip() and len(q)-len(q.lstrip())<=indent:break
   block.append(q[indent+2:])
  code='\n'.join(block)+'\n'
  if 'orthotropic' in code:
   p=subprocess.run(['bash','-n'],input=code,text=True,capture_output=True);assert p.returncode==0,(job,p.stderr);shell.append({'job':job,'line':i+1,'bash_syntax_ok':True})
assert [(x['job'],x['artifact']) for x in uploads]==[('native','orthotropic-native-${{ matrix.os }}'),('wasm','orthotropic-wasm-macos'),('wasm-linux','orthotropic-wasm-linux')],uploads
assert sha(S/'models/research/orthotropic/orthotropic-linear-elastic-ogs.json')=='60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14'
result={'status':'prospective-source-no-blocker','merged_origin':plan['merged_origin'],'source_hashes':{p:sha(S/p) for p in paths},'all_original_workflow_lines_preserved_in_order':True,'all_prior_catalogue_and_approval_entries_preserved_exactly':True,'maxwell_packager_exact_origin_bytes':True,'all_previous_controller_setup_counts_preserved':True,'artifact_jobs':uploads,'new_shell_blocks':shell,'final_acceptance':'pending actual current-runtime CI raw backend outputs and tested-upload/browser/live evidence'}
print(json.dumps(result,indent=2))
