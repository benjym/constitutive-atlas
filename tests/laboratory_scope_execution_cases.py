"""Frozen native laboratory responses, reconstructed into explicit requests."""
import json
from atlas.model import ROOT
def retained():
    packet=ROOT/'docs/reviews/laboratory-scope-contract-v1'
    catalogue=json.loads((packet/'generated-models.json').read_text());rows=[]
    for p in sorted((packet/'observations').glob('[0-9]*.json')):
        receipt=json.loads(p.read_text());label=receipt['label']
        if not(label.startswith('scoped-elastic-')or label.startswith('total-analytical-')):continue
        response=json.loads(receipt['stdout'])
        request=dict(response_contract='stress-scope-0.1',stress_scope=response['stress']['scope'],model=response['model'],parameters=response['parameters'],initial=response['initial'],protocol=response['protocol'],target=response['target'],steps=response['steps'],cycles=response['cycles'],integration_settings=response['integration_settings'])
        rows.append(dict(label=label,request=request,response=response))
    assert len(rows)==10
    return catalogue,rows
