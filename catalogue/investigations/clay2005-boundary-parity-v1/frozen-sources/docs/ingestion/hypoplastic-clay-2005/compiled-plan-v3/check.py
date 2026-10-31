"""Source/contract/corpus checks only; never rerun oracle or execute compiled artifacts."""
import argparse,json,hashlib,sys,math,importlib.util
from pathlib import Path

def run(root):
    sys.path.insert(0,str(root))
    from atlas.model import validate
    from tools import research_rate_observations_v2 as transport
    here=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    model=read(here/'model.json');old_dir=root/'docs/ingestion/hypoplastic-clay-2005/rate-study-v2';old=read(old_dir/'model.json');validate(model)
    for k in ['equations','derived','domain','parameters']:assert model[k]==old[k],k
    assert model['schema_version']=='0.3' and model['initialization']['required_state']==['sigma','e']
    assert model['state'][1]['semantics']=={'role':'persistent','quantity':'void_ratio','transformation':'scalar_invariant'}
    for n in ['reference.json','invalid-cases.json','support-inputs.json','support-reference.json','protocol.json']:assert (here/('source-'+n)).read_bytes()==(old_dir/n).read_bytes(),n
    pins={entry['path']:entry['sha256'] for entry in read(old_dir/'manifest.json')['files']}
    for n in ['model.json','reference.json','invalid-cases.json','support-inputs.json','support-reference.json','protocol.json']:assert sha(old_dir/n)==pins[n],n
    assert read(here/'source-reference.json')['source_sha256']=='8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3'
    assert 'plus' in (old_dir/'SOURCE_CORRECTION.md').read_text().lower()
    spec=importlib.util.spec_from_file_location('packet_corpus',here/'corpus.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    corpus=read(here/'corpus.json');assert corpus==module.assemble()
    cases=corpus['cases'];assert len(cases)==109 and len(set(c['id'] for c in cases))==109
    assert corpus['parameter_order']==list(model['parameters'])
    stream='--describe\n'+''.join('\t'.join(c['args'])+'\n' for c in cases);assert (here/'requests.tsv').read_text()==stream
    controls={};count={}
    for c in cases:
        e=c['expectation'];kind=e['kind'];count[kind]=count.get(kind,0)+1
        assert type(e['ok']) is bool and e['ok']==(kind!='reject')
        args=c['args'];assert len(args)==4 and args[0]==model['id']
        arrays=[list(map(float,x.split(','))) for x in args[1:]]
        assert list(map(len,arrays))==[9,7,6] and all(math.isfinite(x) for a in arrays for x in a)
        if kind=='finite_only':assert set(e)=={'kind','ok'} # no dummy reference or hidden numerical source budget
        if kind=='accuracy':
            assert len(e['values'])==len(e['absolute_budgets'])==len(e['parity_budgets'])==7
            assert all(type(x) in (int,float) and math.isfinite(x) for x in e['values']+e['absolute_budgets']+e['parity_budgets'])
        if 'recovery_of' in c:
            assert c['args']==controls[c['recovery_of']]['args']
            assert c['expectation']==controls[c['recovery_of']]['expectation']
            assert cases[cases.index(c)-1]['id']==c['after_rejection']
            assert cases[cases.index(c)-1]['expectation']['kind']=='reject'
        controls[c['id']]=c
    assert count=={'accuracy':70,'finite_only':10,'reject':29}
    # Minimal capability witness is compatible through model/arity/profile validation,
    # then rejected specifically because generic v2 demands a numerical reference.
    finite=next(c for c in cases if c['expectation']['kind']=='finite_only')
    witness={'version':'research-instantaneous-rate-protocol-0.2','files':{'model.json':sha(here/'model.json')},'model_file':'model.json','model_definition':model,'cases':[finite]}
    assert read(here/'transport-v2-gap-witness.json')==witness
    saved=transport.ROOT
    try:
        transport.ROOT=here
        try:transport.checked_protocol(here/'transport-v2-gap-witness.json')
        except KeyError as exc:assert exc.args==('values',);gap="KeyError('values'): v2 requires numerical source reference for every accepted case"
        else:raise AssertionError('finite-only gap unexpectedly absent; review actual new transport contract')
    finally:transport.ROOT=saved
    return {'version':'clay2005-compiled-plan-v3-source-check','pass':True,'model_sha256':sha(here/'model.json'),'unchanged_mathematical_fields':['equations','derived','domain','parameters'],'byte_identical_retained_sources':5,'retained_v2_manifest_validated':True,'counts':corpus['counts'],'tag_counts_including_recovery':count,'literal_arity':[9,7,6],'transport_v2_gap_witness':gap,'oracle_replays':0,'builds':0,'compiled_calls':0,'admission':False}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--output',type=Path);v=a.parse_args();result=run(v.root);text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if v.output:
        if v.output.exists():raise FileExistsError(v.output)
        v.output.write_text(text)
    print(text,end='')
