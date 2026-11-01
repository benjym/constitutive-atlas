"""Pure source/case/freeze verification; never loads a compiled backend."""
import json
from pathlib import Path
import prepare_accuracy,study
B=Path(__file__).resolve().parent
study.verify_freeze();old,new=prepare_accuracy.verify_inputs();assert json.loads((B/'cases.json').read_text())['cases']==new
for c in new:
 if c['id']=='late-budget-rollback':assert c['args'][10]==2
 if c['id']=='late-budget-prefix':assert c['args'][12]==2
print(json.dumps({'passed':True,'cases':len(new),'compiled_calls':0,'same_model_references_C_ABI_physical_inputs_and_assessor':True,'negative_budget_two_retained':True,'fine_rtol':3e-11,'fine_atol':3e-14,'fine_budget':1000000,'coarse_rtol':1e-5,'coarse_atol':1e-8},indent=2))
