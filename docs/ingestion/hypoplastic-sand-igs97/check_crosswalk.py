"""Source-contract verification only; no native helper/solver or author code."""
import argparse,copy,hashlib,json,sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path);a=ap.parse_args();sys.path.insert(0,str(a.repo))
    from atlas.model import validate
    from atlas.initialization import initialize_state
    from atlas.dsl import ValidationError
    base=Path(__file__).resolve().parent;x=json.loads((base/'formulation-crosswalk.json').read_text());root=a.repo/'models/hypoplastic-sand-igs97.json';m=json.loads(root.read_text());digest=hashlib.sha256(root.read_bytes()).hexdigest();assert digest==x['root_definition_sha256']
    candidate=copy.deepcopy(m);candidate['schema_version']='0.3';candidate.pop('integration');candidate['formulation']=x['formulation'];candidate['state']=x['state'];candidate['initialization']=x['initialization'];validate(candidate)
    checks=['exact root definition hash','explicit v0.3 structure, units and semantics validate in memory','all derived quantities mapped','all state equations mapped','all parameters mapped','all persistent fields explicitly initialized']
    assert {v['name'] for v in m['derived']}==set(x['derived_crosswalk'])
    assert set(m['equations'])==set(x['equation_crosswalk'])
    assert set(m['parameters'])==set(x['parameter_crosswalk'])
    for old,new in zip(m['state'],candidate['state'],strict=True):
        assert old=={k:v for k,v in new.items() if k!='semantics'}
    r=json.loads((a.repo/'docs/benchmarks/kfs-tmd2-research-range-v1/inputs/requests.json').read_text())[0]
    p=dict(zip(m['parameters'],r['parameters'],strict=True));state={'sigma':r['initial'][:6],'e':r['initial'][6],'h':r['initial'][7:]}
    prepared=initialize_state(candidate,parameters=p,state=state)
    assert prepared['initial']==r['initial'];checks.append('published TMD2 explicit state accepted unchanged without projection')
    for label,bad in [('missing history',{'sigma':state['sigma'],'e':state['e']}),('outside numerical band',{**state,'h':[1.02*p['R'],0,0,0,0,0]})]:
        try:initialize_state(candidate,parameters=p,state=bad)
        except ValidationError:checks.append(label+' rejected')
        else:raise AssertionError(label+' admitted')
    assert hashlib.sha256(root.read_bytes()).hexdigest()==digest
    result={'kind':'igs97-source-contract-check','root_sha256':digest,'checks':checks,'count':len(checks),'passed':True,'compiled_calls':0,'root_migrated':False,'model_status':m['status'],'scientific_admission_changed':False}
    text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text)
    else:print(text,end='')
if __name__=='__main__':main()
