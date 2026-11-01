"""Reviewer retained-evidence audit: never loads/runs compiled code or material."""
from pathlib import Path
from decimal import Decimal as D, localcontext
import hashlib,json,subprocess,sys
ROOT=Path.cwd(); BASE=ROOT/'docs/ingestion/norsand-1993'; OUT=BASE/'approval-v1'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=ROOT/'models/research/norsand/norsand-jefferies-1993-active-axial.json'
assert h(model)=='67ff78f8cd56fd8812ba42f4456105b6e7ae217090dbcf40d8f8d5f839995d2c'
assert h(ROOT/'.local/private-sources/norsand-1993/supplied-original-v2/NorSandGeot1993.pdf')=='fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9'
shared=BASE/'shared-integration-v1'; stage=BASE/'e2-v3'
q=json.loads((shared/'target-qualification-v2.json').read_text());count=0
for path,digest in q['artifacts'].items():
 assert h(ROOT/path)==digest,path;count+=1
for path,digest in q['results'].items():
 assert h(shared/path)==digest,path;count+=1
native=json.loads((shared/'native-results-v1.json').read_text());wasm=json.loads((shared/'wasm-results-v2.json').read_text())
assert native['rows']==wasm['rows']
run=subprocess.run([sys.executable,'-B',str(stage/'check_backend_results_v3.py'),str(stage/'backend-requests-v2.json'),str(shared/'native-results-v1.json'),str(shared/'wasm-results-v2.json')],check=True,capture_output=True,text=True)
checker=json.loads(run.stdout)
refs=json.loads((stage/'references-v2.json').read_text());report=json.loads((stage/'interpreter-qualification-v1.json').read_text()); maximum=0.; invmax=0.
with localcontext() as ctx:
 ctx.prec=70
 for ref,row in zip(refs['cases'],report['rows']):
  assert ref['id']==row['id']; r=ref['reference']; o=r['outputs']; n=D(ref['N']);m=D('1.2');p=D(o['mean_pressure']);pi=D(o['image_pressure']);eta=D(o['eta']);ev=D(o['ev']);e=D(o['e'])
  eta_source=m/n*(1+(n-1)*((p/pi).ln()*n/(1-n)).exp()) if n else m*(1+(pi/p).ln())
  assert abs(eta-eta_source)<D('1e-35')
  assert abs(p-D(r['controls_end']['stress_ratio_control'])*D(o['deviatoric_stress'])-D(r['controls_end']['pressure_control']))/D(130000)<D('1e-35')
  inv=abs((1+e)*ev.exp()/(1+D(r['initial_state']['e']))-1); assert inv<D('1e-10');invmax=max(invmax,float(inv))
  err=0.
  for k,rv in o.items():
   a=rv if isinstance(rv,list) else [rv];out=row['outputs'][k];b=out if isinstance(out,list) else [out]; assert len(a)==len(b)
   scale=130000 if k in ('mean_pressure','deviatoric_stress','image_pressure','stress') else 1
   err=max(err,max(abs(float(x)-y)/scale for x,y in zip(a,b)))
  assert err<=2e-6; assert abs(err-row['max_reference_error'])<1e-15; maximum=max(maximum,err)
  assert row['restart_error']==0 and row['rejection_checks']==5
result={'reviewer':'/root/norsand_original_review','scope':'retained artifact/hash/source algebra audit only; no compiled/material calls','target_artifact_result_hashes':count,'backend_checker':checker,'backend_rows_exact_equal':True,'source_reference_cases':len(refs['cases']),'maximum_source_comparison_error':maximum,'maximum_reference_volume_invariant':invmax,'model_sha256':h(model),'script_sha256':h(Path(__file__)),'result':'PASS'}
print(json.dumps(result,indent=2))
