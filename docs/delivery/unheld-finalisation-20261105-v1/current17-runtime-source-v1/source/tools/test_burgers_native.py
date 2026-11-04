"""Run prospectively frozen Burgers reference/transaction suite on a fresh engine."""
import argparse,copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'docs/ingestion/burgers-itasca900/integration-v1'
sys.path.insert(0,str(PACKET));sys.path.insert(0,str(ROOT))
from study import Backend,execute,assess

def refinement(calls):
    rows={c['label']:c['response'] for c in calls}
    # Match study.assess's own reference construction without changing its policy.
    from reference import reference
    req=json.loads((PACKET/'requests.json').read_text())
    spec=next(c['spec'] for c in req['schedules'] if c['id']=='relaxation')
    exact=list(map(float,reference(spec,100)[-1]['state']))
    errors={}
    for name,lo,hi in [('stress',0,6),('Kelvin',6,12)]:
        fine=max(abs(a-b) for a,b in zip(rows['relaxation']['points'][-1]['state'][lo:hi],exact[lo:hi]))
        coarse=max(abs(a-b) for a,b in zip(rows['relaxation-coarse']['points'][-1]['state'][lo:hi],exact[lo:hi]))
        assert fine<coarse,(name,fine,coarse)
        errors[name]=dict(fine=fine,coarse=coarse)
    return errors
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('engine');ap.add_argument('output');ap.add_argument('--wasm',action='store_true');a=ap.parse_args()
    backend=Backend('wasm' if a.wasm else 'native',a.engine,a.output)
    try:calls=execute(backend)
    finally:backend.close()
    report=assess(calls);report['separate_refinement']=refinement(calls)
    corrupted=copy.deepcopy(calls)
    target=next(c['response']['points'][-1]['state'] for c in corrupted if c['label']=='relaxation')
    target[9]+=10*report['separate_refinement']['Kelvin']['coarse']
    try:refinement(corrupted)
    except AssertionError:report['Kelvin_corruption_rejected']=True
    else:raise AssertionError('Worsened fine Kelvin channel escaped refinement gate')
    (Path(a.output)/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
