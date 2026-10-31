"""Reproduce current boundary behavior without changing model guards or using compiled code."""
import argparse,copy,hashlib,json,sys
from pathlib import Path

HASHES={'hypoplastic-sand-vw96':'1df95f8128c4f16066004de7615289075bafe96d2174e06e5cd76704f45bbd61','hypoplastic-sand-igs97':'83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path);args=ap.parse_args();sys.path.insert(0,str(args.repo))
    from atlas.model import defaults,evaluation_environment
    from atlas.initialization import initialize_state
    from atlas.dsl import ValidationError
    cases=[]
    for model_id,digest in HASHES.items():
        path=args.repo/'models'/f'{model_id}.json';assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
        model=json.loads(path.read_text());crosswalk=json.loads((args.repo/'docs/ingestion'/model_id/'formulation-crosswalk.json').read_text())
        assert crosswalk['root_definition_sha256']==digest
        candidate=copy.deepcopy(model);candidate['schema_version']='0.3';candidate.pop('integration');candidate.update({k:crosswalk[k] for k in ('formulation','state','initialization')})
        params=defaults(model);state={f['name']:f['initial'] for f in model['state']};env=evaluation_environment(model,state,state,[0]*6,params)
        # Expected admission is fixed here before any candidate initialization.
        deck=[('isotropic',{},True),('outside_appendix_C',{'sigma':[450000,-75000,-75000,0,0,0]},True),('mixed_sign_inside_shape_range',{'sigma':[-100000,300000,300000,0,0,0]},True),('near_isotropic_cutoff',{'sigma':[100000+3e-7,100000,100000,0,0,0]},True),('above_invariant_cutoff',{'sigma':[100000+1e-6,100000,100000,0,0,0]},True),('dense_endpoint',{'e':env['ed']},False),('loose_endpoint',{'e':env['ei']},False),('pressure_floor',{'sigma':[params['p_ref']*1e-8]*3+[0]*3},False)]
        if 'h' in state:
            deck += [('physical_history_surface',{'h':[params['R'],0,0,0,0,0]},True),('history_numerical_band',{'h':[1.005*params['R'],0,0,0,0,0]},True),('history_numerical_boundary',{'h':[1.01*params['R'],0,0,0,0,0]},False)]
        for name,updates,expected in deck:
            supplied={**state,**updates};error=None
            try:result=initialize_state(candidate,supplied,params);accepted=True
            except (ValidationError,ValueError) as exc:accepted=False;error=str(exc)
            assert accepted==expected,(model_id,name,accepted,error)
            details={}
            if accepted:
                flat=[v for f in candidate['state'] for v in (supplied[f['name']] if f['shape']=='sym' else [supplied[f['name']]])];assert result['initial']==flat
                values=evaluation_environment(candidate,supplied,supplied,[0]*6,params)
                details={key:values[key] for key in ('mean','j2','tanpsi','lode','F')}
                if 'rho' in values:details.update(history_norm=values['hn'],rho=values['rho'])
                if name=='isotropic':assert values['j2']==0 and values['F']==1
                if name=='near_isotropic_cutoff':assert 0<values['j2']<=1e-24 and values['lode']==0
                if name=='above_invariant_cutoff':assert values['j2']>1e-24
                if name=='history_numerical_band':assert values['hn']>params['R'] and values['rho']==1
            cases.append({'model':model_id,'id':name,'state':supplied,'parameters':params,'expected_runtime_admission':expected,'observed_runtime_admission':accepted,'no_projection':True if accepted else None,'error':error,'derived':details})
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    output={'kind':'vw96-igs-applicability-diagnostics-v1','model_hashes':HASHES,'scope':'Current Python declared-domain initialization only; no physical admissibility verdict or trajectory verification.','cases':cases,'count':len(cases),'passed':True,'compiled_calls':0,'model_changes':False}
    text=json.dumps(output,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    else:print(text,end='')
if __name__=='__main__':main()
