"""Pure helper adversarial checks; no import/execution of material runner."""
from pathlib import Path
import json,ast,math
B=Path(__file__).resolve().parent.parent
p=B/'check_domain_supplement.py';tree=ast.parse(p.read_text());model=json.loads((B/'model.json').read_text())
ns={'math':math,'MODEL':model,'checks':[]}
names=['check','get','numbers','invariants','audit','audit_prefix']
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(p),'exec'),ns)
params={k:v['default'] for k,v in model['parameters'].items()}
def row(parent,de):return {'command':['runner','--initial',','.join(map(str,parent)),'--strain',','.join(map(str,de)),'--parameters',','.join(str(params[k]) for k in model['parameters'])]}
def run_audit(parent,de,state,name):
 ns['checks']=[];ns['audit'](row(parent,de),{'ok':True,'state':state},name);return ns['checks'].copy()
records=[]
for pressure in [60000.,1e-6,1e-12,1e-24]:
 z=[pressure]*3+[0]*3+[13.,0.]
 ec=(pressure/101325)**.2/(.2*2300);de=[-.5*ec]*3+[0]*3
 good=[pressure*.5**5]*3+[0]*3+[13.,0.]
 checks=run_audit(z,de,good,'exact');assert all(c['passed'] for c in checks)
 bad=[pressure*.999]*3+[0]*3+[13.,0.]
 checks=run_audit(z,de,bad,'stagnated');assert any(c['name'].endswith('half_source_accuracy') and not c['passed'] for c in checks)
 records.append({'pressure':pressure,'exact_source_accepted':True,'nearly_stagnated_endpoint_rejected':True})
z=[60000.]*3+[0]*3+[13.,0.];ec=(60000/101325)**.2/(.2*2300)
r=row(z,[-.6*ec]*3+[0]*3);ns['checks']=[];ns['audit_prefix']([r,r],[{'ok':True,'state':z},{'ok':True,'state':z}],'synthetic')
assert ns['checks'][0]['passed'] and not ns['checks'][1]['passed']
# A spurious work increment is rejected independently of the stress endpoint.
s=[60000*.5**5]*3+[0]*3+[13.,1.];checks=run_audit(z,[-.5*ec]*3+[0]*3,s,'work')
assert any(c['name'].endswith('elastic_invariants') and not c['passed'] for c in checks)
result={'id':'REVIEW-lade-domain-control-v1-supplement-helper-challenge','tiny_pressure_cases':records,'cumulative_stagnating_prefix_rejected':True,'spurious_elastic_work_rejected':True,'scope':'Synthetic pure Python helper inputs only; no material execution, compiled or Wasm calls'}
Path(__file__).with_name('supplement-helper-results.json').write_text(json.dumps(result,indent=2)+'\n');print('4source/4stagnation cases, cumulative crossing and spurious work helper checks pass')
