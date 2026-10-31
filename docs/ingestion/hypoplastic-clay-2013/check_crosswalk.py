"""Source-only v0.3 contract check; no builds or constitutive-history replay."""
import argparse,copy,hashlib,json,math,sys
from pathlib import Path

def run(root):
    sys.path.insert(0,str(root))
    from atlas.model import migrate_formulation,validate
    from atlas.initialization import initialize_state
    from atlas.dsl import ValidationError
    packet=Path(__file__).resolve().parent
    c=json.loads((packet/'crosswalk.json').read_text())
    source=root/c['research_definition'];assert hashlib.sha256(source.read_bytes()).hexdigest()==c['research_definition_sha256']
    old=json.loads(source.read_text());m=migrate_formulation(old)
    m['state'][1]['semantics']={'role':'persistent','quantity':'void_ratio','transformation':'scalar_invariant'}
    validate(m)
    assert m['formulation']==c['formulation'] and m['initialization']==c['initialization']
    assert [{'name':s['name'],'shape':s['shape'],'unit':s['unit'],'semantics':s['semantics']} for s in m['state']]==c['state_contract']
    for k in ['equations','derived','domain','parameters']:assert old[k]==m[k],k
    parameters={k:v['default'] for k,v in m['parameters'].items()}
    parameters.update(phi_c=math.radians(25),lambda_star=.1,kappa_star=.01,N=1,nu=.2)
    pressure=10000.;e=math.expm1(parameters['N']-parameters['lambda_star']*math.log(pressure/parameters['p_ref']))
    state={'sigma':[pressure]*3+[0.]*3,'e':e};before=copy.deepcopy((state,parameters,m))
    out=initialize_state(m,state,parameters)
    assert (state,parameters,m)==before and len(out['initial'])==7 and out['initial']==state['sigma']+[e]
    reject=[]
    for name,bad in [('omitted_e',{'sigma':state['sigma']}),('negative_e',dict(state,e=-.1))]:
        try:initialize_state(m,bad,parameters)
        except ValidationError:reject.append(name)
        else:raise AssertionError(name+' accepted')
    return {'version':'clay2013-source-closure-v1','checks':'pass','contract_validated':True,'unchanged_mathematics':['equations','derived','domain','parameters'],'explicit_NCL_smoke_state':state,'parameters':parameters,'negative_cases_rejected':reject,'compiled_calls':0,'scope':'contract and initialization consistency; not independent source algebra or material validation'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args()
    result=run(a.root);text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if a.output:a.output.write_text(text)
    print(text,end='')
