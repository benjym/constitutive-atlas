"""Requests reconstructed from the frozen native scope gate, without execution."""
import json
from atlas.model import ROOT
PACKET=ROOT/'docs/reviews/recorded-scope-native-v1'
def retained():
    catalogue=json.loads((PACKET/'generated-models.json').read_text());cases=json.loads((PACKET/'cases.json').read_text());rows=[]
    for i,case in enumerate(cases):
        if case['scope'] not in ['effective','total'] or case['error']:continue
        c,k=case['controls'],case['knots']
        path=dict(version='experimental-recorded-path-0.1',coordinate=dict(name='sample_index',unit='1',meaning='path_order'),initial_strain=[0]*6,controls=[dict(kind='stress' if c[j] else 'strain',coefficients=c[j+1:j+7]) for j in range(0,len(c),7)],knots=[dict(coordinate=k[j],targets=k[j+1:j+7]) for j in range(0,len(k),7)])
        request=dict(version='experimental-recorded-run-0.2',stress_scope=case['scope'],model=case['model'],initial=case['initial'],path=path)
        if case['restart'] is not None:request['restart_settings']=dict(max_restarts=case['restart'])
        if case['control'] is not None:request['control_settings']=dict(max_material_trials=case['control'])
        receipt=json.loads((PACKET/'observations'/f'{i:03d}.json').read_text())
        rows.append(dict(label=case['label'],request=request,response=json.loads(receipt['stdout']),returncode=receipt['returncode']))
    return catalogue,rows
