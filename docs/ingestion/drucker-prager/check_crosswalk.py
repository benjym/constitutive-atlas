"""DP bounded source/contract checks, no compiled or author-code execution."""
import argparse,copy,hashlib,json,math,sys
from fractions import Fraction as Q
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args();sys.path.insert(0,str(a.repo))
    from atlas.model import validate,defaults,interpret
    from atlas.initialization import initialize_state
    from atlas.dsl import ValidationError
    from tools.verify_plasticity import dp_reference
    base=Path(__file__).parent;x=json.loads((base/'formulation-crosswalk.json').read_text());p=a.repo/'models/drucker-prager.json';m=json.loads(p.read_text());digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==x['root_definition_sha256']
    c=copy.deepcopy(m);c['schema_version']='0.3';c.pop('integration');c.update({k:x[k] for k in ('formulation','state','initialization')});validate(c);checks=['root identity','complete v0.3 profile/state/init validate']
    assert set(x['parameter_crosswalk'])==set(m['parameters']) and set(x['derived_crosswalk'])=={d['name'] for d in m['derived']} and set(x['equation_crosswalk'])==set(m['equations']);checks.append('all parameters,derived and equations mapped')
    params=defaults(m);state={f['name']:f['initial'] for f in m['state'] if f['name']!='gamma'};initialize=lambda s,ps=params:initialize_state(c,s,ps)
    assert initialize(state)['initial']==[*state['sigma'],state['e'],0];checks.append('persistent fields preserved,temporary gamma zero-filled')
    for field in state:
        try:initialize({k:v for k,v in state.items() if k!=field})
        except ValidationError:checks.append('missing '+field+' rejected')
        else:raise AssertionError('missing state admitted')
    for label,bad in [('supplied gamma',{**state,'gamma':.1}),('initial outside yield',{**state,'sigma':[4e5,1e5,1e5,0,0,0]}),('e0',{**state,'e':0})]:
        try:initialize(bad)
        except (ValidationError,ValueError):checks.append(label+' rejected')
        else:raise AssertionError(label+' admitted')
    # Exact smooth-yield negative-work witness inside current parameter boxes.
    M=Q(6,5);Md=Q(2);pressure=Q(100000);cohesion=Q(10000);q=M*pressure+cohesion;gamma=Q(1,1000);work=gamma*(q-Md*pressure);assert work==Q(-70)
    stress=[float(pressure+2*q/3),float(pressure-q/3),float(pressure-q/3),0,0,0];badparams={**params,'Md':float(Md)};prepared=initialize({'sigma':stress,'e':.7},badparams);assert prepared['initial'][:6]==stress;checks.append('Md>M negative-plastic-work witness remains admitted by current guards')
    witness={'parameters':badparams,'sigma':stress,'p_exact':str(pressure),'q_exact':str(q),'gamma_exact':str(gamma),'plastic_work_Pa_exact':str(work),'runtime_initialization_accepted':True,'interpretation':'Hypothetical smooth plastic increment at this yield state; not a newly executed trajectory or a physical-admission pass.'}
    zero=interpret(c,{**state,'gamma':0},{**state,'gamma':0},[0]*6,params);assert all(v==0 for v in [*zero['sigma'].v,zero['e'],zero['gamma']]);checks.append('zero-load residual vanishes with gamma0')
    limits=[1e-4]*6+[1e-9,1e-9];start=[*state['sigma'],state['e'],0];residuals=[]
    for label,de in [('elastic',[.0001,0,0,0,0,0]),('smooth',[.01,-.005,-.005,0,0,0]),('apex',[-.002,-.002,-.002,.00001,0,0])]:
        out,branch=dp_reference(start,de,list(params.values()));named=lambda v:{'sigma':v[:6],'e':v[6],'gamma':v[7]};res=interpret(c,named(out),named(start),de,params);flat=[*res['sigma'].v,res['e'],res['gamma']];ratio=max(abs(v)/t for v,t in zip(flat,limits));assert all(math.isfinite(v) for v in flat) and ratio<=1
        assert branch=={'elastic':'elastic','smooth':'smooth-plastic','apex':'apex-limit'}[label];residuals.append({'id':label,'branch':branch,'reference_state':out,'residual':flat,'max_absolute_budget_fraction':ratio})
    try:dp_reference(start,[-.002]*3+[0]*3,[params['p_ref'],params['E'],params['nu'],params['M'],0,params['c']])
    except ValueError:checks.append('Md0 beyond-apex reference correctly has no hydrostatic correction')
    else:raise AssertionError('nondilatant impossible correction supplied')
    artifacts=[]
    for name in ('drucker-prager-investigation-v1','drucker-prager-apex-v2'):
        record=json.loads((a.repo/'catalogue/evidence'/f'{name}.json').read_text())
        for artifact in record['artifacts']:
            h=hashlib.sha256((a.repo/artifact['path']).read_bytes()).hexdigest();assert h==artifact['sha256'];artifacts.append({'record':name,'outcome':record['outcome'],'path':artifact['path'],'sha256':h,'rerun':False})
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
    result={'kind':'dp-source-contract-check-v3','root_sha256':digest,'contract_checks':checks,'contract_check_count':len(checks),'negative_work_witness':witness,'reference_residual_budgets':limits,'scalar_reference_residuals':residuals,'historical_artifacts':artifacts,'compiled_calls':0,'root_migrated':False,'scientific_admission_changed':False,'passed':True};text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text)
    else:print(text,end='')
if __name__=='__main__':main()
