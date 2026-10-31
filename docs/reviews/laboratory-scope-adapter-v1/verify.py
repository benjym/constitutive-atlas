"""Assess the frozen saved laboratory outputs without executing a solver."""
import copy,json,math,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tests.laboratory_scope_execution_cases import retained

def read(p):return json.loads(p.read_text())
def compare(a,b,path=''):
    if type(b) in (float,int):
        assert type(a) in (float,int) and math.isfinite(a) and abs(a-b)<=1e-9*max(1,abs(b))
        if path.split('.')[-1] in ['iterations','substeps','rejected','steps','cycles','protocol']:assert a==b
    elif isinstance(b,dict):
        assert isinstance(a,dict) and set(a)==set(b)
        for k in b:compare(a[k],b[k],path+'.'+k)
    elif isinstance(b,list):
        assert isinstance(a,list) and len(a)==len(b)
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'.'+str(i))
    else:assert type(a)==type(b) and a==b

def assess(packet):
    p=Path(packet);inputs=read(p/'inputs.json');catalogue,rows=retained();assert inputs==dict(catalogue=catalogue,rows=rows)
    outputs=read(p/'responses.json');assert len(outputs)==11
    for row,out in zip(rows,outputs[:10]):
        assert out['label']==row['label']
        compare({k:v for k,v in out['result'].items()if k!='elapsed_ms'},{k:v for k,v in row['response'].items()if k!='elapsed_ms'})
    x=outputs[-1];assert x['label']=='independent-exact-reversal';s=x['request'];out=x['result'];f=read(p/'freeze.json')['independent_case']
    assert (s['model'],s['stress_scope'],s['protocol'],s['target'],s['steps'],s['cycles'])==(f['model'],f['scope'],f['protocol'],f['target'],f['steps'],f['cycles'])
    assert out['ok'] is True and out['api_version']=='experimental-laboratory-scope-0.1' and out['catalogue_hash']==catalogue['sha256'] and out['model']==s['model']
    assert out['parameters']==s['parameters'] and out['initial']==s['initial'] and out['integration_settings']==s['integration_settings']
    assert out['stress']==dict(source='state',name='sigma',measure='cauchy',scope='effective',tensor_representation='mandel',sign='compression_positive')
    assert out['pore_pressure']==dict(quantity='change',availability='unavailable',reason='not_reconstructed_for_protocol')
    assert out['protocol']==1 and out['steps']==16 and 'target'not in out and 'cycles'not in out
    l=s['loading'];assert l['producer']['algorithm']=='cyclic-sine-rne12-v1' and l['producer']['steps']==16 and l['producer']['cycles']==1
    bits=l['controls_bits'];controls=[struct.unpack('>d',bytes.fromhex(b))[0] for b in bits]
    assert len(bits)==17 and out['loading']['controls_bits']==bits and out['loading']['controls']==controls
    assert [controls[i] for i in [0,4,8,12,16]]==[0.,1e-5,0.,-1e-5,0.]
    points=out['points'];assert len(points)==17 and [pt['control']for pt in points]==controls
    assert points[0]['state']==s['initial'] and points[0]['strain']==[0]*6 and all(pt['u']is None for pt in points)
    model=next(m for m in catalogue['models']if m['id']==s['model']);parameters=dict(zip(model['parameters'],s['parameters']))
    stress_error=0.;strain_error=0.
    for pt in points:
        a=pt['control'];stress=[s['initial'][0]+parameters['E']*a,s['initial'][1],s['initial'][2],0.,0.,0.];strain=[a,-parameters['nu']*a,-parameters['nu']*a,0.,0.,0.]
        assert len(pt['state'])==len(s['initial']) and len(pt['strain'])==6 and all(type(v)in(int,float)and math.isfinite(v)for v in [*pt['state'],*pt['strain']])
        stress_error=max(stress_error,max(abs(x-y)for x,y in zip(pt['state'][:6],stress)));strain_error=max(strain_error,max(abs(x-y)for x,y in zip(pt['strain'],strain)))
    assert stress_error<=f['stress_tolerance_Pa'] and strain_error<=f['strain_tolerance']
    # Preserve the run's auxiliary, non-policy failure. It assumed constant void
    # ratio despite the declared elastic volumetric evolution equation.
    process=read(p/'process.json');assert process['returncode']!=0 and 'history changed' in process['stderr']
    return dict(native_pairs=10,wasm_material_requests=11,max_stress_error_Pa=stress_error,max_strain_error=strain_error,original_auxiliary_failure_retained=True,native_calls=0,builds=0)
if __name__=='__main__':print(json.dumps(assess(Path(__file__).parent),indent=2))
