"""Validate candidate contract and prospective literal inputs only; no compiled calls."""
import argparse,hashlib,json,math,sys,copy
from pathlib import Path

def run(root):
    sys.path.insert(0,str(root))
    from atlas.model import validate
    from atlas.initialization import initialize_state
    from atlas.dsl import ValidationError
    here=Path(__file__).resolve().parent
    read=lambda p:json.loads(p.read_text())
    model=read(here/'model.json');old=read(root/'models/research/clay2013/hypoplastic-clay-2013-research.json')
    validate(model)
    same=['equations','derived','domain','parameters']
    for name in same:assert model[name]==old[name],name
    row=next(x for x in read(root/'catalogue/manifest.json')['models'] if x['id']==model['id'])
    assert row['id']=='hypoplastic-clay-2013' and model['status']=='draft'
    assert model['schema_version']=='0.3' and 'integration' not in model
    assert model['initialization']['required_state']==['sigma','e']
    reqs=read(here/'requests.json');policy=read(here/'acceptance.json')
    assert len(reqs)==policy['requests_per_backend']==18
    assert len({r['id'] for r in reqs})==18
    assert {(r['protocol'],r['cycles']) for r in reqs[:10]}=={(p,c) for p in range(5) for c in (0,1)}
    names=list(model['parameters']);params={k:v['default'] for k,v in model['parameters'].items()}
    expected_parameters=','.join(format(params[k],'.17g') for k in names)
    initialized=[];rejected=[];before=copy.deepcopy(model)
    for r in reqs:
        assert r['parameters']==expected_parameters and r['integration_settings']==policy['settings_csv']
        assert r['model']==model['id'] and type(r['expected_ok']) is bool
        if 'same_result_as' in r:
            baseline=next(x for x in reqs if x['id']==r['same_result_as']);assert reqs.index(baseline)<reqs.index(r)
            assert {k:v for k,v in r.items() if k not in ('id','same_result_as')}=={k:v for k,v in baseline.items() if k not in ('id','same_result_as')}
        if not r['initial']:
            try:initialize_state(model,{},params)
            except ValidationError:rejected.append(r['id'])
            else:raise AssertionError('omitted state accepted')
            continue
        z=list(map(float,r['initial'].split(',')));state={'sigma':z[:6],'e':z[6]}
        try:out=initialize_state(model,state,params)
        except (ValidationError,ValueError,ArithmeticError):
            assert not r['expected_ok'],r['id'];rejected.append(r['id'])
        else:
            assert r['expected_ok'],r['id'];assert out['initial']==z;initialized.append(r['id'])
    assert model==before
    browser=next(r for r in reqs if r['id']=='actual-browser-default')
    assert (browser['protocol'],browser['target'],browser['steps'],browser['cycles'])==(1,.01,100,0)
    initial=list(map(float,browser['initial'].split(',')));p=initial[0];e=initial[-1]
    pe=params['p_ref']*math.exp((params['N']-math.log1p(e))/params['lambda_star'])
    omega=-math.log(math.cos(params['phi_c'])**2)/math.log(2)-.3*math.sin(params['phi_c'])**2
    return {'version':'clay2013-laboratory-preview-source-check-v1','pass':True,'validated_schema':'0.3','unchanged_fields':same,'candidate_sha256':hashlib.sha256((here/'model.json').read_bytes()).hexdigest(),'request_count':len(reqs),'source_only_initialization_successes':initialized,'source_only_initialization_rejections':rejected,'browser_default_diagnostic':{'p':p,'e':e,'pe':pe,'isotropic_ASBS_residual':(p/pe)**omega-1,'preparation_claim':'none; default UI example is outside ASBS and remains explicit research input'},'compiled_calls':0,'predicted_protocol_success_verified':False}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--output',type=Path);v=a.parse_args();result=run(v.root);txt=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if v.output:v.output.write_text(txt)
    print(txt,end='')
