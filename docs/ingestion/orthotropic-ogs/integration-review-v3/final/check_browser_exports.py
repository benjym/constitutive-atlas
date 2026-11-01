"""Independent saved final-browser source-law audit; no compiled calls."""
from pathlib import Path
import importlib.util,json,sys,hashlib
from decimal import localcontext
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('review_oracle',ROOT/'docs/ingestion/orthotropic-ogs/scientific-review-v1/check_independent.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
assert len(sys.argv)>=3,'Usage: checker ACTUAL_TESTED_UPLOAD EXPORTED_BROWSER_JSON...'
site=Path(sys.argv[1]);identity=json.loads((site/'material-point-orthotropic/identity.json').read_text());reports={}
for name in sys.argv[2:]:
 path=Path(name);d=json.loads(path.read_text());r=d['request'];assert d['ok'] and d['provenance']==identity and len(d['records'])==len(r['increments']);assert len(d['points'])==len(r['increments'])+1
 assert r['model']=='orthotropic-linear-elastic-ogs' and r['settings']==[1e-11,1e-6,60,0,1,20]
 strain=[oracle.dec(0)]*6;stress=list(map(oracle.dec,r['initial']));n=0;maximum=0.
 with localcontext() as c:
  c.prec=80
  for i,point in enumerate(d['points']):
   assert point['step']==i and len(point['state'])==len(point['strain'])==6
   if i:
    row=r['increments'][i-1];stress=[a+b for a,b in zip(stress,oracle.increment(r['parameters'],row))];strain=[a+oracle.dec(b) for a,b in zip(strain,row)];rec=d['records'][i-1];res=rec['response'];assert res['ok'] and res['state']==point['state'] and res['initial']==d['points'][i-1]['state'] and res['strain']==row and res['parameters']==r['parameters'] and res['catalogue_hash']==identity['catalogue_hash'] and res['model']==r['model']
   for a,b in zip(point['state'],stress):
    e=abs(a-float(b));assert e<=1e-6,(name,i,e);maximum=max(maximum,e);n+=1
   for a,b in zip(point['strain'],strain):assert abs(a-float(b))<=1e-15
 reports[str(path)]={'stress_components':n,'strain_components':n,'maximum_stress_error_Pa':maximum,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'all_actual_returned_states_chained':True}
print(json.dumps({'passed':True,'oracle':'Independent Decimal80 Cholesky source compliance; no production cofactor or parent Fraction reference imported','identity':identity,'exports':reports},indent=2))
