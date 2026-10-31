"""Bounded source-contract diagnostics; no builds, compiled calls or root migration."""
import argparse,copy,hashlib,json,math,sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args();sys.path.insert(0,str(a.repo))
    from atlas.model import validate,defaults,interpret,evaluation_environment
    from atlas.initialization import initialize_state
    from atlas.dsl import ValidationError
    base=Path(__file__).resolve().parent;x=json.loads((base/'formulation-crosswalk.json').read_text());path=a.repo/'models/hypoplastic-sand-vw96.json';m=json.loads(path.read_text());digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==x['root_definition_sha256']
    checks=['root exact-byte identity']
    candidate=copy.deepcopy(m);candidate['schema_version']='0.3';candidate.pop('integration');candidate['formulation']=x['formulation'];candidate['state']=x['state'];candidate['initialization']=x['initialization'];validate(candidate);checks.append('complete explicit v0.3 candidate validates in memory')
    for name,keys in [('derived_crosswalk',{d['name'] for d in m['derived']}),('equation_crosswalk',set(m['equations'])),('parameter_crosswalk',set(m['parameters']))]:
        assert set(x[name])==keys;checks.append(name+' covers every root field')
    for old,new in zip(m['state'],candidate['state'],strict=True):assert old=={k:v for k,v in new.items() if k!='semantics'}
    checks.append('state values/order/scales unchanged')
    p=defaults(m);state={f['name']:f['initial'] for f in m['state']};flat=[*state['sigma'],state['e']]
    assert initialize_state(candidate,state,p)['initial']==flat;checks.append('example explicit initialization accepted without projection')
    for name in state:
        try:initialize_state(candidate,{k:v for k,v in state.items() if k!=name},p)
        except ValidationError:checks.append('missing '+name+' rejected')
        else:raise AssertionError('missing persistent field accepted')
    zero=interpret(candidate,state,state,[0]*6,p);assert list(zero['sigma'].v)==[0]*6 and zero['e']==0;checks.append('zero strain produces zero stress and void-ratio rates')
    igs=json.loads((a.repo/'models/hypoplastic-sand-igs97.json').read_text());assert igs['derived'][:18]==m['derived'] and igs['domain'][:8]==m['domain'];checks.append('IGS first18 derived quantities and first8 domain guards exactly match VW96')
    pdiff={}
    for name,field in m['parameters'].items():
        other=igs['parameters'][name];assert {k:v for k,v in field.items() if k!='label'}=={k:v for k,v in other.items() if k!='label'}
        if field!=other:pdiff[name]={'vw96_label':field.get('label'),'igs97_label':other.get('label')}
    checks.append('host parameter defaults/units/bounds match IGS; label differences explicitly retained')
    witnesses=[]
    for name,sigma in [('outside_appendix_C_range',[450000,-75000,-75000,0,0,0]),('mixed_sign_inside_appendix_C_range',[-100000,300000,300000,0,0,0])]:
        s={'sigma':sigma,'e':.7};prepared=initialize_state(candidate,s,p);assert prepared['initial']==sigma+[.7]
        env=evaluation_environment(candidate,s,s,[0]*6,p)
        within=env['tanpsi']<math.sqrt(2);assert within==(name=='mixed_sign_inside_appendix_C_range')
        expected_F=1 if not within else .2;assert math.isclose(env['F'],expected_F,rel_tol=1e-13,abs_tol=1e-13)
        witnesses.append({'id':name,'state':s,'parameters':p,'accepted_by_current_declared_domain':True,'tanpsi':env['tanpsi'],'tanpsi_squared':env['tanpsi']**2,'lode_cosine':env['lode'],'F':env['F'],'within_stated_appendix_C_shape_range':within,'all_principal_stresses_compressive':False,'interpretation':'Algebraic domain diagnostic, not evidence of physical applicability or a newly prescribed rejection rule.'})
    checks.append('both exact-source domain witnesses reproduced by current Python initialization without projection')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    result={'kind':'vw96-source-contract-diagnostics-v2','root_sha256':digest,'checks':checks,'count':len(checks),'passed':True,'witnesses':witnesses,'host_parameter_label_differences':pdiff,'compiled_calls':0,'root_migrated':False,'model_status':m['status'],'scientific_admission_changed':False}
    text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text)
    else:print(text,end='')
if __name__=='__main__':main()
