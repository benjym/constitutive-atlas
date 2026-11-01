"""Explicit recorded scope codec parity and legacy no-fallback boundary."""
import copy
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from atlas.dsl import ValidationError
from atlas.model import ROOT,all_models,load,migrate_formulation
from atlas.stress import stress_binding
from atlas.recorded import execute_recorded,recorded_wire
from atlas.recorded_scope import validate_scoped_recorded_run,validate_scoped_recorded_model,scoped_recorded_wire
from tests.test_recorded_api import specimen


def corpus():
    rows=[];request={**specimen(),'version':'experimental-recorded-run-0.2','stress_scope':'effective'}
    for model in all_models():
        s=copy.deepcopy(request);s['model']=model['id'];s['stress_scope']=stress_binding(model)['scope']
        rows.append(dict(name=model['id'],request=s,model=model,accepted=True))
        wrong=copy.deepcopy(s);wrong['stress_scope']='total' if s['stress_scope']=='effective' else 'effective'
        rows.append(dict(name=model['id']+'-opposite-scope',request=wrong,model=copy.deepcopy(model),accepted=False))
    model=migrate_formulation(load(ROOT/'models/linear-elastic.json'))
    for scope in ['effective','total']:
        m=copy.deepcopy(model);m['formulation']['stress']['scope']=scope
        s=copy.deepcopy(request);s['stress_scope']=scope;s['restart_settings']={'max_restarts':0}
        rows.append(dict(name='explicit-'+scope,request=s,model=m,accepted=True))
    base=rows[-1]
    mutations=['missing-scope','unknown-scope','opposite-scope','old-version','extra','wrong-id','observable','missing-binding','time','unit','shape','temporary','extra-binding','duplicate-coordinate','bad-settings','bad-path-version','extra-path']
    for mutation in mutations:
        row=copy.deepcopy(base);row['name']=mutation;row['accepted']=False;s=row['request'];m=row['model']
        if mutation=='missing-scope':del s['stress_scope']
        elif mutation=='unknown-scope':s['stress_scope']='unspecified'
        elif mutation=='opposite-scope':s['stress_scope']='effective'
        elif mutation=='old-version':s['version']='experimental-recorded-run-0.1'
        elif mutation=='extra':s['extra']=1
        elif mutation=='wrong-id':s['model']='another-model'
        elif mutation=='observable':m['formulation']['stress']['source']='observable'
        elif mutation=='missing-binding':del m['formulation']['stress']
        elif mutation=='time':m['formulation']['time_dependence']='physical_time'
        elif mutation=='unit':m['state'][0]['unit']='1'
        elif mutation=='shape':m['state'][0]['shape']='scalar'
        elif mutation=='temporary':m['state'][0]['semantics']['role']='increment_unknown'
        elif mutation=='extra-binding':m['formulation']['stress']['extra']=True
        elif mutation=='duplicate-coordinate':s['path']['knots'][1]['coordinate']=s['path']['knots'][0]['coordinate']
        elif mutation=='bad-settings':s['control_settings']={'max_material_trials':0}
        elif mutation=='bad-path-version':s['path']['version']='experimental-recorded-path-0.2'
        elif mutation=='extra-path':s['path']['extra']=1
        rows.append(row)
    return rows

class RecordedScopeTests(unittest.TestCase):
    def test_python_browser_parity_and_input_identity(self):
        rows=corpus();before=copy.deepcopy(rows);expected=[]
        for row in rows:
            try:
                self.assertIs(validate_scoped_recorded_run(row['request']),row['request'])
                self.assertIs(validate_scoped_recorded_model(row['request'],row['model']),row['request'])
                c,k=scoped_recorded_wire(row['request'],row['model']);result=dict(accepted=True,wire=dict(controls=c,knots=k))
            except ValidationError:result=dict(accepted=False)
            self.assertEqual(result['accepted'],row['accepted'],row['name']);expected.append(result)
        result=subprocess.run(['node','tests/test_recorded_scope_browser.mjs'],cwd=ROOT,input=json.dumps(rows,allow_nan=False),capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout),expected);self.assertEqual(rows,before)
        models=all_models()
        self.assertEqual({row['name'] for row in rows if row['accepted'] and not row['name'].startswith('explicit-')},{model['id'] for model in models})
        self.assertEqual(sum(row['name'].endswith('-opposite-scope') for row in rows),len(models))
        self.assertEqual(len(rows),2*len(models)+2+17)

    def test_ordered_wire_is_identical_to_legacy_mechanics(self):
        for row in corpus():
            if not row['accepted']:continue
            request=row['request'];legacy={k:v for k,v in request.items() if k!='stress_scope'};legacy['version']='experimental-recorded-run-0.1'
            self.assertEqual(scoped_recorded_wire(request,row['model']),recorded_wire(legacy))

    def test_legacy_execution_rejects_new_request_without_any_process(self):
        for row in corpus():
            if not row['accepted']:continue
            with patch('subprocess.run') as run:
                with self.assertRaises(ValidationError):execute_recorded(row['request'],'unused')
                run.assert_not_called()

    def test_unrepresentable_integer_and_nonfinite_inputs_reject(self):
        for value in [2**53+1,float('inf'),float('nan')]:
            row=corpus()[0];row['request']['initial']=[value]*7
            with self.assertRaises(ValidationError):validate_scoped_recorded_run(row['request'])

if __name__=='__main__':unittest.main()
