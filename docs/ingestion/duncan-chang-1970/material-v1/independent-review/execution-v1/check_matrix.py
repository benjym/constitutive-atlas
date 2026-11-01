"""Source-only exact-wire/matrix/freeze audit; no material engine execution."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import runpy,json,struct,hashlib
B=Path(__file__).resolve().parents[2];E=B/'execution-v1';R=Path.cwd()
ref=runpy.run_path(str(B/'reference.py'));q=ref['q']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bit(x):
    if isinstance(x,float):return struct.pack('>d',x).hex()
    if isinstance(x,list):return list(map(bit,x))
    if isinstance(x,dict):return {k:bit(v)for k,v in x.items()}
    return x
def main():
    req=json.loads((E/'requests.json').read_text());assert bit(req)==json.loads((E/'requests-binary64.json').read_text())
    old=json.loads((B/'candidate.json').read_text());new=json.loads((E/'candidate.json').read_text());assert [k for k in old if old[k]!=new[k]]==['name','description']
    counts={k:len(req[k])for k in ['cases','paths','transactions','invalids','diagnostics','derivatives','presets']}
    assert list(counts.values())==[72,42,2,43,1,2,2]
    with localcontext()as c:
        c.prec=160
        for case in req['cases']:
            eps,h,branch,_,_=ref['compliance'](case['target'],case['initial'],case['parameters'])
            assert list(map(float,eps))==case['de']
            assert branch==case['branch']
            assert all(struct.pack('>d',float(format(v,'.17g')))==struct.pack('>d',v)for v in case['de']+case['initial']+case['target'])
        for transaction in req['transactions']:
            p=transaction['parameters'];assert p['nu']==0 and transaction['de'][1:]==[0]*5
            Ei=q(p['K'])*q(p['pa'])*(D(100000)/q(p['pa']))**q(p['n']);Eur=Ei*q(p['Kur'])/q(p['K'])
            boundary=Ei*(1-q(p['Rf'])*D(95000)/D(200000))**2;strain=q(transaction['de'][0]);lo=D(10000)/Eur;hi=D(10000)/boundary
            assert lo<strain<hi and strain/2<lo
            assert D(90000)+q(p['E_failure'])*strain<D(100000)
        for path in req['paths']:
            if path['kind']!='failure-crossing':continue
            p=path['parameters'];sp=ref['sin'](q(p['phi']));F=2*D(100000)*sp/(1-sp);Ei=q(p['K'])*q(p['pa'])*(D(100000)/q(p['pa']))**q(p['n']);threshold=F/(Ei*(1-q(p['Rf'])))
            assert abs(q(path['source_failure_strain'])-threshold)/threshold<D('1e-14')
            assert sum(q(x[0])for x in path['increments'])>threshold
    freeze=json.loads((E/'freeze.json').read_text());bad=[]
    for name,sha in freeze['files'].items():
        path=E/'frozen'/name if name.startswith(('cpp/','atlas/','schemas/'))else R/name
        assert digest(path)==sha,(name,'retained')
        if name.startswith(('cpp/','atlas/','schemas/')):assert digest(R/name)==sha,(name,'current')
    generic=json.loads((R/'docs/reviews/newton-endpoint-constraints-v1/independent-review/final-bindings-v5.json').read_text())
    assert freeze['files']['cpp/include/atlas/solver.hpp']==generic['files']['cpp/include/atlas/solver.hpp']
    assert all(v['exit']==0 for v in freeze['toolchain'].values())
    return {'pass':True,'coverage':counts,'all_endpoint_compliance_wire_values_reproduced':True,'gap_root_intervals_checked':True,'failure_crossing_thresholds_checked':True,'recursive_wire_manifest_checked':True,'freeze_entries_rehashed':len(freeze['files']),'solver_sha256':freeze['files']['cpp/include/atlas/solver.hpp'],'freeze_sha256':digest(E/'freeze.json'),'requests_sha256':digest(E/'requests.json'),'material_updates':0,'compiled_calls':0}
if __name__=='__main__':print(json.dumps(main(),indent=2))
