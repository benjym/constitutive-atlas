"""Bounded elasticity source/contract check; no native or third-party execution."""
import argparse,copy,hashlib,json,math,sys
from fractions import Fraction as Q
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args();sys.path.insert(0,str(a.repo))
    from atlas.model import validate,defaults,interpret
    from atlas.initialization import initialize_state
    from atlas.dsl import ValidationError
    base=Path(__file__).resolve().parent;x=json.loads((base/'formulation-crosswalk.json').read_text());path=a.repo/'models/linear-elastic.json';m=json.loads(path.read_text());digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==x['root_definition_sha256']
    candidate=copy.deepcopy(m);candidate['schema_version']='0.3';candidate.pop('integration');candidate.update({k:x[k] for k in ('formulation','state','initialization')});validate(candidate)
    checks=['root identity','complete v0.3 formulation/state/initialization validate without root migration']
    assert set(x['derived_crosswalk'])=={d['name'] for d in m['derived']};assert set(x['parameter_crosswalk'])==set(m['parameters']);assert set(x['equation_crosswalk'])==set(m['equations']);checks.append('every derived,parameter,equation mapped')
    for old,new in zip(m['state'],candidate['state'],strict=True):assert old=={k:v for k,v in new.items() if k!='semantics'}
    p=defaults(m);state={f['name']:f['initial'] for f in m['state']};assert initialize_state(candidate,state,p)['initial']==[*state['sigma'],state['e']];checks.append('explicit state preserved without projection')
    for name in state:
        try:initialize_state(candidate,{k:v for k,v in state.items() if k!=name},p)
        except ValidationError:checks.append('missing '+name+' rejected')
        else:raise AssertionError('missing state accepted')
    try:initialize_state(candidate,{**state,'e':0},p)
    except ValidationError:checks.append('e=0 rejected by project domain')
    else:raise AssertionError('nonpositive e accepted')
    assert initialize_state(candidate,{**state,'sigma':[-1e5]*3+[0]*3},p)['initial'][:3]==[-1e5]*3;checks.append('tensile initial stress accepted as intended for elasticity')
    # Exact algebra, using rational coefficients and six basis vectors in Kelvin space.
    algebra=[]
    for nu in (Q(-99,100),Q(-1,5),Q(1,4),Q(49,100),Q(499,1000)):
        E=Q(30000000);G=E/(2*(1+nu));K=E/(3*(1-2*nu));lam=E*nu/((1+nu)*(1-2*nu));assert K==lam+2*G/3 and G>0 and K>0
        for j in range(6):
            d=[Q(int(i==j)) for i in range(6)];trace=sum(d[:3]);cart=[lam*trace+2*G*d[i] if i<3 else 2*G*d[i] for i in range(6)];voldev=[K*trace+2*G*(d[i]-trace/3) if i<3 else 2*G*d[i] for i in range(6)];assert cart==voldev
        algebra.append({'nu_exact':str(nu),'lame_bulk_identity':True,'positive_energy_coefficients':True,'six_basis_stiffness_columns_equal':True})
    evidence=json.loads((a.repo/'catalogue/evidence/linear-elastic-analytical-v1.json').read_text());artifact=evidence['artifacts'][0];report_path=a.repo/artifact['path'];assert hashlib.sha256(report_path.read_bytes()).hexdigest()==artifact['sha256'];report=json.loads(report_path.read_text());assert len(report['cases'])==29
    replay=[];t=report['tolerances']
    for case in report['cases']:
        args=case['arguments'];values=list(map(float,args[args.index('--parameters')+1].split(',')));parameters=dict(zip(m['parameters'],values,strict=True));previous={'sigma':case['initial'][:6],'e':case['initial'][6]};current={'sigma':case['expected'][:6],'e':case['expected'][6]}
        residual=interpret(candidate,current,previous,case['total_strain'],parameters);flat=[*residual['sigma'].v,residual['e']];limits=[(t['stress_absolute_Pa'] if i<6 else t['void_absolute'])+t['relative']*abs(v) for i,v in enumerate(case['expected'])];ratio=max(abs(v)/limit for v,limit in zip(flat,limits));assert all(math.isfinite(v) for v in flat) and ratio<=1
        replay.append({'id':case['id'],'expected_state_residual_max_budget_fraction':ratio})
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    result={'kind':'elasticity-source-contract-check-v2','root_sha256':digest,'contract_checks':checks,'contract_check_count':len(checks),'exact_algebra_regimes':algebra,'exact_basis_column_checks':30,'saved_expected_state_residual_checks':replay,'historical_report_sha256':artifact['sha256'],'historical_native_report_rerun':False,'compiled_calls':0,'root_migrated':False,'scientific_admission_changed':False,'passed':True}
    output=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(output)
    else:print(output,end='')
if __name__=='__main__':main()
