"""Compare every physical control row and reference checkpoint outside the runtime."""
import json,math,sys
from pathlib import Path
from wire import D,assess,read

def measure(case,result):
    data=[float(x) for x in case['args'][4].split(',')]
    rows=[data[i:i+7] for i in range(0,len(data),7)]
    targets=[float(x) for x in case['args'][5].split(',')]
    n=len(rows)+1
    knots=[targets[i:i+n] for i in range(0,len(targets),n)]
    errors=[]
    for i,(point,knot) in enumerate(zip(result['points'],knots,strict=True)):
        assert point['coordinate']==knot[0]
        z=point['state']
        previous=result['points'][max(i-1,0)]
        span=knot[0]-previous['coordinate'] if i else 1.
        stress_cap=1e-7+1e-11*math.dist(z[:6],previous['state'][:6])/span
        for tagrow,want in zip(rows,knot[1:],strict=True):
            tag,*coeff=tagrow
            load=z[:6] if tag else point['strain']
            residual=abs(math.fsum(a*b for a,b in zip(coeff,load,strict=True))-want)
            scale=max(map(abs,coeff))
            error=residual/scale/(span if tag else 1.)
            errors.append((bool(tag),error,stress_cap if tag else 1e-14))
    return dict(pass_=all(x<=lim for _,x,lim in errors),
                max_stress_rate=max((x for tag,x,_ in errors if tag),default=0.),
                max_strain=max((x for tag,x,_ in errors if not tag),default=0.),
                row_count=len(rows),observations=len(errors))

out={}
for f in read(D/'wire-fixtures.json'):
    raw=Path(sys.argv[1])/(f['id']+'.json')
    if not raw.exists():continue
    result=read(raw)
    report=assess(f,result)
    if not f['negative'] and result['ok']:
        report['physical_rows']=measure(f,result)
        report['pass_'] &= report['physical_rows']['pass_']
    out[f['id']]=report
passed=len(out)==6 and all(x['pass_'] for x in out.values())
print(json.dumps(dict(pass_=passed,cases=out),indent=2))
sys.exit(not passed)
