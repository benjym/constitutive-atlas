"""Interpreter smooth residual directional differences versus independent source columns."""
from pathlib import Path
import sys,json,math
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parents[3]))
from atlas.model import load,interpret
m=load(B/'candidate.json');refs=json.loads((B/'references.json').read_text());results=[]
def value(z,n,d,p):
    r=interpret(m,{'sigma':z[:6],'h':z[6]},{'sigma':n[:6],'h':n[6]},d,p);return list(r['sigma'].v)+[r['h']]
for case in refs['derivatives']:
    sweep_errors=[]
    for sweep in case['sweeps']:
        worst=0.
        for j,column in enumerate(sweep['columns']):
            block=0 if j<7 else 1 if j<14 else 2;index=j if j<7 else j-7 if j<14 else j-14;scale=1e5 if j<14 else 1.;step=2.**(-sweep['exponent'])*scale
            plus=[list(case[k]) for k in ['current','previous','de']];minus=[x[:] for x in plus];plus[block][index]+=step;minus[block][index]-=step
            rp=value(*plus,case['parameters']);rm=value(*minus,case['parameters'])
            for x,y,reference in zip(rp,rm,column):
                actual=(x-y)/(2*step)*scale/1e5;expected=float(reference);worst=max(worst,abs(actual-expected)/max(1.,abs(expected)))
        sweep_errors.append(worst)
    plateau=any(a<=2e-5 and b<=2e-5 for a,b in zip(sweep_errors,sweep_errors[1:]));assert plateau,(case['id'],sweep_errors)
    results.append(dict(id=case['id'],sweep_errors=sweep_errors,pass_=plateau))
out=dict(identity='duncan-interpreter-directional-v1',states=2,columns_each=20,steps_each=4,results=results,pass_=True,material_updates=0,compiled_calls=0);(B/'derivative-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
