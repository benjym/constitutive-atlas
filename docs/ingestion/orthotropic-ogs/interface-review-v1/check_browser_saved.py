"""Reviewer saved-browser exports against independently written Decimal Cholesky oracle."""
import importlib.util,json,sys
from pathlib import Path
from decimal import localcontext
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
p=ROOT/'docs/ingestion/orthotropic-ogs/scientific-review-v1/check_independent.py';spec=importlib.util.spec_from_file_location('review_oracle',p);oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
B=ROOT/'docs/ingestion/orthotropic-ogs/browser-v1';site=Path(sys.argv[1]);identity=json.loads((site/'material-point-orthotropic/identity.json').read_text());counts={}
for name in ['default','custom','latest']:
 d=json.loads((B/(name+'.json')).read_text());r=d['request'];assert d['ok'] and d['provenance']==identity and len(d['records'])==len(r['increments']);assert len(d['points'])==len(r['increments'])+1
 stress=list(map(oracle.dec,r['initial']));strain=[oracle.dec(0)]*6;count=0;maxerr=0.
 with localcontext() as ctx:
  ctx.prec=80
  for i,point in enumerate(d['points']):
   if i:
    row=r['increments'][i-1];inc=oracle.increment(r['parameters'],row);stress=[a+b for a,b in zip(stress,inc)];strain=[a+oracle.dec(b) for a,b in zip(strain,row)]
    record=d['records'][i-1];response=record['response'];assert response['state']==point['state'] and response['initial']==d['points'][i-1]['state'];assert response['strain']==row and response['parameters']==r['parameters'] and response['model']==r['model'] and response['catalogue_hash']==identity['catalogue_hash']
   assert len(point['state'])==len(point['strain'])==6
   for a,b in zip(point['state'],stress):
    e=abs(a-float(b));assert e<=1e-6,(name,i,e);count+=1;maxerr=max(maxerr,e)
   for a,b in zip(point['strain'],strain):assert abs(a-float(b))<=1e-15
 counts[name]={'all_six_stress_comparisons':count,'all_six_cumulative_strain_comparisons':count,'max_stress_error_Pa':maxerr,'original_initial_and_actual_returned_state_chain':True}
assert json.loads((B/'default.json').read_text())==json.loads((B/'replayed.json').read_text());assert json.loads((B/'custom.json').read_text())==json.loads((B/'custom-fresh.json').read_text())
if (B/'reset.json').exists():assert json.loads((B/'default.json').read_text())==json.loads((B/'reset.json').read_text())
print(json.dumps({'passed':True,'independent_oracle':'Decimal80 source-compliance Cholesky; no production reference imported','exports':counts,'exact_default_replay_and_custom_fresh':True,'exact_reset':(B/'reset.json').exists()},indent=2))
