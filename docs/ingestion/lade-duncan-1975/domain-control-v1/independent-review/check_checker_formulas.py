"""Static checker formula audit; extracts only pure helpers, never runners."""
from pathlib import Path
import ast,math,json,hashlib
B=Path(__file__).resolve().parent.parent
p=B/'check_native_domain.py';tree=ast.parse(p.read_text());ns={'math':math}
helpers=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['level','rotate']],type_ignores=[])
exec(compile(helpers,str(p),'exec'),ns)
v=[1.1,1.,.9,0,0,0];rot=ns['rotate'](v);f=ns['level'](rot)
assert abs(f-300/11)<1e-12
assert abs(sum(rot[:3])-3)<1e-14
assert abs(sum(x*x for x in rot)-sum(x*x for x in v))<1e-14
refs=json.loads(Path(__file__).with_name('left-reference-results.json').read_text())['source_references'];rows=[]
for label,n,K in [('dense',.8,2300),('loose',.86,1600)]:
 for p0 in [60000.,1e-6,1e-12,1e-24]:
  for amin in [1.,.9]:
   expected=next(x for x in refs if x['set']==label and float(x['initial_coefficient_pressure_Pa'])==p0 and float(x['least_shape_eigenvalue'])==amin)
   critical=-(p0/101325)**(1-n)/((1-n)*K)*amin**(-n)
   relative=abs(critical-float(expected['critical_proportional_strain']))/abs(critical)
   assert relative<1e-13
   for fraction in [.5,.9,.99]:
    pressure=p0*(1-fraction)**(1/(1-n));target=float(expected['source_coefficient_pressure_Pa'][str(fraction)])
    assert abs(pressure-target)/target<1e-13
   rows.append({'set':label,'p0':p0,'amin':amin,'critical_relative_difference_vs_80digit_source':relative})
result={'id':'REVIEW-lade-domain-control-v1-checker-formula-audit','rotation_preserves_f_trace_and_mandel_norm':True,'rotated_constant_f':f,'reference_cases':rows,'checker_sha256':{name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in ['check_native_domain.py','check_native_triaxial.py','check_native_lifecycle.py','check_native_legacy.py','check_wasm.mjs']},'limits':['Pure helper extraction and independent reference formula comparison only','No material execution or compiled calls','Coverage omissions documented separately; formula correctness does not imply qualification gate completion']}
Path(__file__).with_name('checker-formula-results.json').write_text(json.dumps(result,indent=2)+'\n');print('16 source formula/reference combinations and rotated tensor invariants pass')
