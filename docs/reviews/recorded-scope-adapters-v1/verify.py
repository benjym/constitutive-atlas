"""Saved adapter transport replay; no solver or build is required."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from atlas.recorded_scope import scoped_recorded_wire
from atlas.recorded_scope_execution import verify_scoped_recorded_response
from tests.scoped_recorded_execution_cases import retained

def verify(packet):
    p=Path(packet);read=lambda n:json.loads((p/n).read_text());pre=read('pre-execution.json');policy=read('freeze.json');report=read('summary.json');payload=read('responses.json')
    assert pre['policy']==policy and report['status']=='passed' and report['material_calls']==policy['max_material_calls']==3 and report['metadata_calls']==policy['max_metadata_calls']==3 and report['builds']==0
    assert report['receipts']==[f'{i:03d}.json' for i in range(6)] and report['exact_saved_responses']==policy['labels']
    catalogue,retained_rows=retained();assert pre['catalogue']==payload['catalogue']==catalogue and len(payload['rows'])==3
    for i,(spec,row) in enumerate(zip(pre['requests'],payload['rows'])):
        assert row['label']==policy['labels'][i] and row['request']==spec
        metadata=read(f'{2*i:03d}.json');material=read(f'{2*i+1:03d}.json')
        for receipt in [metadata,material]:assert receipt['solver_sha256']==policy['solver_sha256'] and receipt['command'][0]==policy['solver']
        assert metadata['command'][1:]==['--describe'] and metadata['returncode']==0 and json.loads(metadata['stdout'])==catalogue and metadata['wires']=={}
        out=json.loads(material['stdout']);assert material['returncode']==(0 if out['ok'] else 1)
        args=dict(zip(material['command'][1::2],material['command'][2::2]));assert args['--mode']=='recorded' and args['--model']==spec['model'] and args['--recorded-stress-scope']==spec['stress_scope']
        assert ('--recorded-restarts' in args)==('restart_settings' in spec)
        model=next(m for m in catalogue['models'] if m['id']==spec['model']);controls,knots=scoped_recorded_wire(spec,model)
        csv=lambda values:','.join(repr(float(x)) for x in values)
        assert material['wires']=={'--recorded-controls-file':csv(controls),'--recorded-knots-file':csv(knots)}
        assert verify_scoped_recorded_response(out,spec,catalogue)==row['response']
        prior=next(r for r in retained_rows if r['label']==row['label']);assert prior['request']==spec and prior['response']==out
    browser=read('browser-contract.json');assert browser['returncode']==0 and json.loads(browser['stdout'])==[True]*3
    assert report['javascript_scope_verification'] and report['wasm_execution'] is False and report['scientific_admission'] is False
    return dict(status='passed',saved_material_requests=3,saved_metadata_calls=3,native_calls=0,builds=0)
if __name__=='__main__':print(json.dumps(verify(Path(__file__).parent)))
