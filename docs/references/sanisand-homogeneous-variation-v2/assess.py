"""Saved-only coverage, coordinate reconstruction and unchanged output-gate audit."""
from decimal import Decimal as D,localcontext
import copy,gzip,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OLD=ROOT/'docs/reviews/sanisand-transverse-extension-v1'
sys.path.insert(0,str(OLD))
spec=importlib.util.spec_from_file_location('old_audit',OLD/'assess_study.py');previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def require(ok,message):
 if not ok:raise ValueError(message)
def coordinates(run):
 require(run['status']=='completed','incomplete run')
 require(run['method']=='power10-homogeneous-variation-v2','method identity')
 require(len(run['samples'])==17,'sample coverage')
 with localcontext() as ctx:
  ctx.prec=run['precision']
  for s in run['samples']:
   require(type(s['decimal_exponent']) is int,'exponent type')
   require(len(s['normalized_variation'])==len(s['variation'])==3,'variation dimensions')
   require(len(s['base_state_cartesian'])==27,'base dimensions')
   values=[D(x) for x in s['normalized_variation']+s['variation']+s['base_state_cartesian']]
   require(all(x.is_finite() for x in values),'nonfinite coordinate')
   psi=list(map(D,s['normalized_variation']));phi=list(map(D,s['variation']))
   require(D(1)<=max(map(abs,psi))<D(10),'normalization')
   require([x.scaleb(s['decimal_exponent']) for x in psi]==phi,'reconstruction')
   base=list(map(D,s['base_state_cartesian']))
   for offset in (0,9,18):require(base[offset+4]==base[offset+8],'transverse base symmetry')
  first=run['samples'][0]
  require(list(map(D,first['variation']))==[D(1),D(0),D(0)] and first['decimal_exponent']==0,'initial variation')
def audit(data):
 policy=load(HERE/'policy.json')
 require(data['new_candidate_calls']==0 and data['new_configs']==3,'scope')
 require(data['case']==policy['case'],'case')
 require(len(data['runs'])==3,'run coverage')
 require({(r['precision'],r['tolerance']) for r in data['runs']}=={tuple(x) for x in policy['configs']},'config coverage')
 for r in data['runs']:
  require(r['case']==policy['case'],'run case');coordinates(r)
 original=load(OLD/'continuous-v1/study.json.gz')
 replacements={(r['precision'],r['tolerance']):r for r in data['runs']}
 composite=copy.deepcopy(original);replaced=0
 for i,r in enumerate(composite['variational']):
  if r['case']==policy['case']:
   require(r['status']=='failed','replace only historical failure')
   composite['variational'][i]=replacements[(r['precision'],r['tolerance'])];replaced+=1
 require(replaced==3,'replacement coverage')
 assessment=previous.audit(composite,load(OLD/'policy.json'))
 # Additional prospective base check against independent symmetric Cartesian reference.
 reference=load(ROOT/'docs/references/sanisand-project-monotonic-v1/reference-p80-t12.json.gz')
 case=next(c for c in reference['cases'] if c['id']==policy['case'])
 worst=D(0)
 with localcontext() as ctx:
  ctx.prec=100
  require(len(case['samples'][1:])==17,'reference coverage')
  for r in data['runs']:
   for s,ref in zip(r['samples'],case['samples'][1:]):
    require(abs(D(s['parameter'])-D(ref['parameter']))<D('1e-70'),'reference coordinates')
    raw=list(map(D,ref['state']));expected=[]
    for offset in (0,7,13):
     b=raw[offset:offset+6];expected += [b[0],b[3]/D(2).sqrt(),b[5]/D(2).sqrt(),b[3]/D(2).sqrt(),b[1],b[4]/D(2).sqrt(),b[5]/D(2).sqrt(),b[4]/D(2).sqrt(),b[2]]
    worst=max(worst,max(abs(D(a)-b)/(D(20000) if i<9 else D(1)) for i,(a,b) in enumerate(zip(s['base_state_cartesian'],expected))))
 require(worst<=D(policy['base_scaled_error_max']),'base reference agreement')
 return {'kind':'composite-homogeneous-variation-v2','pass':True,'new_runs':3,'reused_variation_runs':15,'reused_nonlinear_runs':8,'maximum_base_scaled_error':str(worst),'unchanged_output_audit':assessment,'original_v1_audit_pass':False,'native_qualification_pass':False,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(audit(load(Path(sys.argv[1]))),indent=2))
