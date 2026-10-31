"""Assess exact retained context journals against prospective acceptance."""
from pathlib import Path
import json,hashlib
STUDY=Path(__file__).resolve().parent

def unique(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('duplicate key: '+k)
        out[k]=v
    return out

def load(path):
    return json.loads(Path(path).read_text(),object_pairs_hook=unique,
        parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite wire value:'+x)))

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

def assess(study=STUDY):
    study=Path(study)
    for name,pin in load(study/'manifest.json').items():
        if hashlib.sha256((study/name).read_bytes()).hexdigest()!=pin:
            raise ValueError('changed frozen input:'+name)
    protocol=load(study/'protocol.json')
    expected={'version':'expression-generated-context-observations-v1',
              'material':load(study/'expected.json'),'history':load(study/'history-expected.json')}
    results={};observations={}
    for backend in ('native','wasm'):
        directory=study/backend;receipt=load(directory/'receipt.json')
        if receipt['inputs']!=protocol['inputs']:raise ValueError('wrong inputs:'+backend)
        if [(x['label'],x['exit_code'])for x in receipt['commands']] != [('configure',0),('build',0),('observe',0)]:
            raise ValueError('incomplete commands:'+backend)
        if (directory/'observe.stderr.txt').read_bytes():raise ValueError('observation stderr:'+backend)
        actual=load(directory/'observe.stdout.txt');observations[backend]=actual
        mismatches=[]
        if set(actual)!=set(expected)or actual.get('version')!=expected['version']:mismatches.append('root shape/version')
        for family in ('material','history'):
            rows=actual.get(family,[]);want=expected[family]
            if len(rows)!=len(want):mismatches.append(family+': count')
            for i,(a,b)in enumerate(zip(rows,want)):
                if canonical(a)!=canonical(b):mismatches.append(family+':'+str(i)+':'+b['id'])
        results[backend]={'material_rows':len(actual.get('material',[])),
                          'history_rows':len(actual.get('history',[])),
                          'mismatches':mismatches,'pass':not mismatches}
    parity=canonical(observations['native'])==canonical(observations['wasm'])
    return {'version':'expression-generated-context-assessment-v1','backends':results,
            'native_wasm_bit_parity':parity,'pass':all(x['pass']for x in results.values())and parity,
            'scope':'generated material/Jet/history routing; no constitutive accuracy or scientific admission'}

if __name__=='__main__':
    result=assess();print(json.dumps(result,indent=2));raise SystemExit(0 if result['pass']else 1)
