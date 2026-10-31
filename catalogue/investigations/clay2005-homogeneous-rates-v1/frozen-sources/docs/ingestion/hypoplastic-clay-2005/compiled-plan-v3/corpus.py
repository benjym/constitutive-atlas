"""Assemble unchanged retained literals/budgets; never evaluate a material/reference law."""
from pathlib import Path
import json,math,hashlib
HERE=Path(__file__).resolve().parent

def read(name):return json.loads((HERE/name).read_text())
def sha(name):return hashlib.sha256((HERE/name).read_bytes()).hexdigest()
def csv(values):return ','.join(format(v,'.17g') for v in values)
def assemble():
    m=read('model.json');ref=read('source-reference.json');inv=read('source-invalid-cases.json');sup=read('source-support-inputs.json');sr=read('source-support-reference.json')
    defaults={k:v['default'] for k,v in m['parameters'].items()};names=list(defaults);cases=[]
    def row(c,kind,origin):
        params=dict(defaults);params.update(c['parameters'])
        args=[m['id'],csv([params[n] for n in names]),csv(c['state']),csv(c['increment'])]
        return {'id':kind+'/'+c['id'],'origin':{'file':origin,'sha256':sha(origin),'case_id':c['id']},'args':args,'expectation':{'kind':kind,'ok':kind!='reject'}}
    def accuracy(c,origin='source-reference.json'):
        v=row(c,'accuracy',origin);policy=ref['policy'];sb=policy['stress_absolute_floor_Pa']+policy['stress_relative_to_scale']*c['stress_scale'];vb=policy['void_absolute_floor']+policy['void_relative_to_scale']*c['void_scale']
        v['expectation'].update(values=c['expected'],absolute_budgets=[sb]*6+[vb],parity_budgets=[sb]*6+[vb]);return v
    for c in ref['cases']:cases.append(accuracy(c))
    for c in sup['cases']:
        if c['expected_accepted']:cases.append(row(c,'finite_only','source-support-inputs.json'))
    negatives=[(c,'source-invalid-cases.json') for c in inv['cases']]+[(c,'source-support-inputs.json') for c in sup['cases'] if not c['expected_accepted']]
    baseline=cases[0]
    for c,origin in negatives:
        v=row(c,'reject',origin);v['id']=('historical-invalid/' if origin=='source-invalid-cases.json' else 'support-reject/')+c['id'];cases.append(v)
        recovery=accuracy(ref['cases'][0]);recovery.update(id='recovery/'+v['id'],recovery_of=baseline['id'],after_rejection=v['id']);cases.append(recovery)
    return {'version':'clay2005-tagged-instantaneous-corpus-v3','model_file':'model.json','model_sha256':sha('model.json'),'parameter_order':names,'source_policy':ref['policy'],'counts':{'original_accuracy':41,'accepted_finite_only':10,'historical_reject':10,'support_reject':19,'recovery':29,'calls':109,'raw_rows_with_descriptor':110},'parity_policy':{'accuracy':'same fixed absolute component budgets as source accuracy, prospectively chosen for backend parity','finite_only':'abs(native-wasm)/max(1,abs(native),abs(wasm))<=1e-10; backend comparison only, no source expected rate','finite_only_scaled_budget':1e-10},'cases':cases}
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();v=assemble();s=json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n';stream='--describe\n'+''.join('\t'.join(c['args'])+'\n' for c in v['cases'])
    if a.check:
        assert (HERE/'corpus.json').read_text()==s
        assert (HERE/'requests.tsv').read_text()==stream
        print('Exact retained-input corpus and literal stream reproduce; no material/reference execution.')
    else:
        for name,text in [('corpus.json',s),('requests.tsv',stream)]:
            target=HERE/name
            if target.exists():raise FileExistsError(target)
            target.write_text(text)
