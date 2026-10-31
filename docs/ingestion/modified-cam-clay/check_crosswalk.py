"""Source/contract diagnostics only. No compiled, author-code or solver execution."""
import argparse,copy,hashlib,json,math,sys
from fractions import Fraction as Q
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args();sys.path.insert(0,str(a.repo))
    from atlas.model import validate,defaults,interpret,evaluation_environment
    from atlas.initialization import initialize_state
    from atlas.dsl import ValidationError
    from tools.verify_plasticity import mcc_general_reference
    base=Path(__file__).parent;x=json.loads((base/'formulation-crosswalk.json').read_text());p=a.repo/'models/modified-cam-clay.json';m=json.loads(p.read_text());digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==x['root_definition_sha256']
    c=copy.deepcopy(m);c['schema_version']='0.3';c.pop('integration');c.update({k:x[k] for k in ('formulation','state','initialization')});validate(c)
    checks=['root identity','complete explicit v0.3 profile/state/init validate']
    for name,keys in [('parameter_crosswalk',set(m['parameters'])),('derived_crosswalk',{d['name'] for d in m['derived']}),('equation_crosswalk',set(m['equations']))]:assert set(x[name])==keys
    checks.append('all parameters,derived quantities and equations mapped')
    params=defaults(m);state={f['name']:f['initial'] for f in m['state'] if f['name']!='gamma'};initial=[*state['sigma'],state['e'],state['pc'],0]
    assert initialize_state(c,state,params)['initial']==initial;checks.append('persistent sigma/e/pc preserved,temporary gamma zero-filled')
    for field in state:
        try:initialize_state(c,{k:v for k,v in state.items() if k!=field},params)
        except ValidationError:checks.append('missing '+field+' rejected')
        else:raise AssertionError('missing persistent state admitted')
    for label,bad,bad_params in [('supplied gamma',{**state,'gamma':.1},params),('initial outside yield',{**state,'sigma':[3e5]*3+[0]*3},params),('zero pc',{**state,'pc':0},params),('lambda equals kappa',state,{**params,'lambda_c':params['kappa']})]:
        try:initialize_state(c,bad,bad_params)
        except (ValidationError,ValueError,ArithmeticError):checks.append(label+' rejected')
        else:raise AssertionError(label+' admitted')
    numerical={**state,'sigma':[200000+.0001]*3+[0]*3};initialize_state(c,numerical,params);env=evaluation_environment(c,{**numerical,'gamma':0},{**numerical,'gamma':0},[0]*6,params);assert 0<env['yield_scaled']<=1e-8;checks.append('small positive initial yield inside numerical tolerance retained without projection')
    unchanged=interpret(c,{**state,'gamma':0},{**state,'gamma':0},[0]*6,params);assert all(v==0 for v in [*unchanged['sigma'].v,unchanged['e'],unchanged['pc'],unchanged['gamma']]);checks.append('zero-load residual vanishes with gamma0 and unchanged persistent state')
    # Exact witnesses of the two printed source discrepancies, not source amendments.
    M=Q(6,5);pressure=Q(1,2);pc=Q(1);q=M*pressure
    assert q*q+M*M*pressure*(pressure-pc)==0 and q*q+M*pressure*(pressure-pc)!=0
    phi=Q(1,3);rate=Q(1,100);from_volume=(1-phi)*rate;from_printed=(1+phi)*rate;assert from_volume!=from_printed
    algebra={'critical_point_M_squared_yield':True,'single_M_disagrees_at_critical_slope':True,'porosity_rate_from_Eq9':str(from_volume),'porosity_rate_from_printed_Eq7':str(from_printed),'source_tension_positive_volume_rate':str(rate)}
    # Fixed diagnostic residual budgets precede reference calls; not a numerical admission gate.
    limits=[1e-4]*6+[1e-9,1e-4,1e-9];comparisons=[]
    for label,pc0,de in [('elastic',2e5,[.001]*3+[0]*3),('wet_hardening',1e5,[0,0,0,.04,0,0]),('dry_softening',4e5,[0,0,0,.06,0,0])]:
        start=[1e5]*3+[0,0,0,.7,pc0,0];out=mcc_general_reference(start,de,list(params.values()));named=lambda v:{'sigma':v[:6],'e':v[6],'pc':v[7],'gamma':v[8]};res=interpret(c,named(out),named(start),de,params);flat=[*res['sigma'].v,res['e'],res['pc'],res['gamma']];ratio=max(abs(v)/t for v,t in zip(flat,limits));assert all(math.isfinite(v) for v in flat) and ratio<=1
        if label=='wet_hardening':assert out[7]>pc0 and out[8]>0
        if label=='dry_softening':assert out[7]<pc0 and out[8]>0
        comparisons.append({'id':label,'reference_state':out,'residual':flat,'max_absolute_budget_fraction':ratio})
    artifacts=[]
    for name in ('modified-cam-clay-investigation-v1','modified-cam-clay-scalar-v2'):
        record=json.loads((a.repo/'catalogue/evidence'/f'{name}.json').read_text())
        for artifact in record['artifacts']:
            h=hashlib.sha256((a.repo/artifact['path']).read_bytes()).hexdigest();assert h==artifact['sha256'];artifacts.append({'record':name,'outcome':record['outcome'],'path':artifact['path'],'sha256':h,'rerun':False})
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
    result={'kind':'mcc-source-contract-check-v3','root_sha256':digest,'contract_checks':checks,'contract_check_count':len(checks),'exact_source_conflict_witnesses':algebra,'reference_residual_budgets':limits,'source_reference_residuals':comparisons,'initial_yield_tolerance_witness':env['yield_scaled'],'historical_artifacts':artifacts,'compiled_calls':0,'root_migrated':False,'scientific_admission_changed':False,'passed':True};text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text)
    else:print(text,end='')
if __name__=='__main__':main()
