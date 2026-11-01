"""Prepare immutable qualification inputs without compiling or running material code."""
from pathlib import Path
import json,shutil,sys
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/reviews/newton-endpoint-constraints-v1';F=B/'qualification'
assert not F.exists()
F.mkdir()
for name in ['00-tresca','01-duncan','02-fixture','03-infeasible','04-restart','05-no-root','06-grid','07-grid-domain','08-grid-nonfinite']:
 shutil.copyfile(O/'frozen'/(name+'.json'),F/(name+'.json'))
m=json.loads((F/'02-fixture.json').read_text());m['id']='fixture-alternate-partition';m['name']='Synthetic discontinuous trace-history partition fixture'
m['parameters']['p_ref']['default']=1.
m['state'][0]['initial']=[0.]*6;m['state'][1]['initial']=50/64
m['derived']=[{'name':'modulus','expr':'select(trace(sigma)<h_n,10*p_ref,2*p_ref)'}]
m['equations']={'sigma':'sigma-sigma_n-modulus*de','h':'h-select(trace(sigma)<h_n,h_n,trace(sigma))'}
m['domain']=['p_ref>0*p_ref'];m['initial_checks']=['h>=trace(sigma)','h>=0*p_ref'];m['solution_constraints']=['h>=trace(sigma)','h>=0*p_ref']
(F/'09-partition.json').write_text(json.dumps(m,indent=2)+'\n')
for name in ['corpus.inc','history.inc','checks.inc','requests.hpp']:
 shutil.copyfile(O/'frozen'/name,F/name)
shutil.copyfile(O/'driver-v5.cpp',F/'regression.cpp')
shutil.copyfile(O/'requests-v5.json',F/'requests-v5.json');shutil.copyfile(O/'assess-v5.py',F/'assess-regression.py')
shutil.copytree(O/'prior-tresca',F/'prior-tresca')
sys.path.insert(0,str(R))
from atlas.compiler import generate
generate(F/'generated',sorted(F.glob('0*.json')))
print('Prepared generic qualification; no compilation')
